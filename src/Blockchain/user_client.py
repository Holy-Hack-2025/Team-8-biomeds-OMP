from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import os


class UserClient:
    def __init__(self, username):
        self.username = username
        self.private_key = None
        self.public_key = None
        self.load_keys()

    def load_keys(self):
        key_path = f"{self.username}_keys/"
        if not os.path.exists(key_path):
            os.makedirs(key_path, exist_ok=True)

        priv_path = os.path.join(key_path, "private.pem")
        pub_path = os.path.join(key_path, "public.pem")

        if os.path.exists(priv_path) and os.path.exists(pub_path):
            # Load existing keys
            with open(priv_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
            with open(pub_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(f.read())
        else:
            # Generate new keys
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()

            # Save keys
            with open(priv_path, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            with open(pub_path, "wb") as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

    def get_public_key_str(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()