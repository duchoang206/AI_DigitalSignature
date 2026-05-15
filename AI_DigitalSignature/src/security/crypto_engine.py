from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import hashlib

class CryptoEngine:
    @staticmethod
    def generate_key_pair():
        private_key = ec.generate_private_key(ec.SECP256K1())
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_bytes.decode('utf-8'), public_bytes.decode('utf-8')

    @staticmethod
    def sign_data(private_key_pem, data_bytes):
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None
        )
        signature = private_key.sign(
            data_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()

    @staticmethod
    def verify_signature(public_key_pem, signature_hex, data_bytes):
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8')
        )
        try:
            public_key.verify(
                bytes.fromhex(signature_hex),
                data_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_file_hash(data_bytes):
        return hashlib.sha256(data_bytes).hexdigest()
