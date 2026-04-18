# ip_guardian.py — AI IP Guardian: Isolation Forest + Hard Rules + Whitelist

import os, json, time, pickle, logging, random
from collections import defaultdict, deque
from datetime import datetime

import numpy as np

# ── Logging ──────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR    = os.path.join(_BASE, "../../logs")
CONFIG_DIR = os.path.join(_BASE, "../../config")
MODEL_DIR  = os.path.join(_BASE, "../../models")
for d in (LOG_DIR, CONFIG_DIR, MODEL_DIR):
    os.makedirs(d, exist_ok=True)

LOG_PATH      = os.path.join(LOG_DIR,  "ip_guardian.log")
WHITELIST_PATH= os.path.join(CONFIG_DIR,"whitelist.json")
MODEL_PATH    = os.path.join(MODEL_DIR, "ip_guardian.pkl")

logging.basicConfig(
    filename=LOG_PATH, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("IPGuardian")


def _load_whitelist() -> set:
    if os.path.exists(WHITELIST_PATH):
        with open(WHITELIST_PATH) as f:
            return set(json.load(f).get("ips", []))
    default = {"127.0.0.1", "::1"}
    with open(WHITELIST_PATH, "w") as f:
        json.dump({"ips": list(default)}, f, indent=2)
    return default


class IPGuardian:
    """
    3 lớp bảo vệ:
      L3 Whitelist  — bypass hoàn toàn
      L1 Hard Rules — block tức thì nếu vi phạm ngưỡng cứng
      L2 AI Model   — Isolation Forest anomaly detection
    """
    RATE_LIMIT  = 60     # req / 60s
    FAIL_RATE   = 0.80   # tỉ lệ verify thất bại
    BURST_LIMIT = 10     # req / 10s
    AI_THRESHOLD= 0.55   # decision_function threshold (âm = anomaly)

    def __init__(self):
        self.whitelist = _load_whitelist()
        self._stats: dict       = defaultdict(self._default_stats)
        self._times: dict       = defaultdict(lambda: deque(maxlen=500))
        self._known_ips: set    = set()
        self._model             = None
        self._decision_baseline = 0.0   # mean decision của traffic bình thường
        self._load_or_train()

    @staticmethod
    def _default_stats():
        return {"total": 0, "fail": 0, "messages": set(),
                "first_seen": time.time(), "last_seen": time.time()}

    # ── Model ─────────────────────────────────────────
    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    obj = pickle.load(f)
                    if isinstance(obj, dict):
                        self._model = obj["model"]
                        self._decision_baseline = obj.get("baseline", 0.0)
                    else:
                        self._model = obj
                logger.info("Loaded Isolation Forest model.")
                return
            except Exception:
                pass
        self._train()

    def _train(self):
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            logger.warning("scikit-learn không khả dụng. AI layer bị vô hiệu.")
            return

        rng = random.Random(42)
        # Normal traffic
        normal = []
        for _ in range(3000):
            normal.append([
                rng.uniform(0, 15),     # request_rate /60s
                rng.uniform(0, 0.15),   # fail_rate
                rng.randint(1, 15),     # unique_messages
                rng.randint(0, 23),     # hour_of_day
                rng.choice([0, 0, 0, 1]),  # is_new_ip (mostly known)
                rng.uniform(1, 60),     # time_since_last (giây)
                0,                      # burst_flag
            ])
        # Anomaly traffic (để model học biên giới)
        anomaly = []
        for _ in range(150):
            anomaly.append([
                rng.uniform(55, 120),   # rate rất cao
                rng.uniform(0.75, 1.0), # fail_rate cao
                rng.randint(1, 3),
                rng.randint(0, 23),
                1,
                rng.uniform(0.01, 0.3), # request dồn dập
                1,
            ])

        X = np.array(normal + anomaly)
        model = IsolationForest(
            n_estimators=300,
            contamination=0.05,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X)

        # Baseline = mean decision của normal samples
        baseline = float(model.decision_function(np.array(normal)).mean())
        self._model = model
        self._decision_baseline = baseline

        with open(MODEL_PATH, "wb") as f:
            pickle.dump({"model": model, "baseline": baseline}, f)
        logger.info(f"Trained Isolation Forest. baseline={baseline:.4f}")

    # ── Feature extraction (7D) ───────────────────────
    def _features(self, ip: str, success: bool, message: str) -> np.ndarray:
        now   = time.time()
        stats = self._stats[ip]
        times = self._times[ip]

        stats["total"]  += 1
        if not success:
            stats["fail"] += 1
        stats["messages"].add(message)
        stats["last_seen"] = now
        times.append(now)

        rate_60  = sum(1 for t in times if now - t <= 60)
        fail_r   = stats["fail"] / stats["total"]
        u_msgs   = len(stats["messages"])
        hour     = datetime.now().hour
        is_new   = int(ip not in self._known_ips)
        self._known_ips.add(ip)
        t_last   = (times[-1] - times[-2]) if len(times) >= 2 else 60.0
        burst    = sum(1 for t in times if now - t <= 10)
        b_flag   = int(burst >= self.BURST_LIMIT)

        return np.array([[rate_60, fail_r, u_msgs, hour, is_new, t_last, b_flag]])

    # ── API chính ─────────────────────────────────────
    def check(self, ip: str, success: bool = True, message: str = "") -> dict:
        # L3 Whitelist
        if ip in self.whitelist:
            return {"status": "allow", "layer": "whitelist",
                    "reason": "IP tin cậy", "score": 0.0}

        feat  = self._features(ip, success, message)
        stats = self._stats[ip]
        now   = time.time()
        times = self._times[ip]

        rate_60  = feat[0][0]
        fail_r   = feat[0][1]
        burst    = sum(1 for t in times if now - t <= 10)

        # L1 Hard Rules
        if rate_60 >= self.RATE_LIMIT:
            reason = f"Rate limit: {rate_60:.0f} req/60s"
            logger.warning(f"[BLOCK][L1] {ip} — {reason}")
            return {"status": "block", "layer": "hard_rule", "reason": reason, "score": 1.0}

        if fail_r >= self.FAIL_RATE and stats["total"] >= 5:
            reason = f"Fail rate: {fail_r:.0%}"
            logger.warning(f"[BLOCK][L1] {ip} — {reason}")
            return {"status": "block", "layer": "hard_rule", "reason": reason, "score": 1.0}

        if burst >= self.BURST_LIMIT:
            reason = f"Burst: {burst} req/10s"
            logger.warning(f"[BLOCK][L1] {ip} — {reason}")
            return {"status": "block", "layer": "hard_rule", "reason": reason, "score": 1.0}

        # L2 AI Model
        ai_score = 0.0
        if self._model is not None:
            dec = float(self._model.decision_function(feat)[0])
            # Chuẩn hoá: khi dec < 0 → bất thường
            # ai_score ∈ [0, 1]: 0 = bình thường, 1 = rất bất thường
            if dec >= 0:
                ai_score = 0.0
            else:
                # Scale âm decision thành score dương
                worst = -0.20  # mức rất bất thường
                ai_score = min(1.0, (-dec) / abs(worst))

            if ai_score >= self.AI_THRESHOLD:
                reason = f"AI anomaly score: {ai_score:.3f}"
                logger.warning(f"[WARN][L2] {ip} — {reason}")
                return {"status": "warn", "layer": "ai", "reason": reason, "score": ai_score}

        logger.info(f"[ALLOW] {ip} score={ai_score:.3f}")
        return {"status": "allow", "layer": "ok", "reason": "Bình thường", "score": ai_score}

    # ── Quản lý ───────────────────────────────────────
    def add_to_whitelist(self, ip: str):
        self.whitelist.add(ip)
        with open(WHITELIST_PATH, "w") as f:
            json.dump({"ips": list(self.whitelist)}, f, indent=2)
        logger.info(f"[WHITELIST+] {ip}")

    def remove_from_whitelist(self, ip: str):
        self.whitelist.discard(ip)
        with open(WHITELIST_PATH, "w") as f:
            json.dump({"ips": list(self.whitelist)}, f, indent=2)

    def get_stats(self, ip: str) -> dict:
        s = self._stats[ip]
        return {"total": s["total"], "fail": s["fail"],
                "fail_rate": s["fail"] / s["total"] if s["total"] else 0,
                "unique_msgs": len(s["messages"])}

    def reset_ip(self, ip: str):
        self._stats.pop(ip, None)
        self._times.pop(ip, None)
