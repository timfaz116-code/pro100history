from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import os

private_key = ed25519.Ed25519PrivateKey.generate()

priv_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.OpenSSH,
    encryption_algorithm=serialization.NoEncryption()
)

pub_ssh = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.OpenSSH,
    format=serialization.PublicFormat.OpenSSH
)

priv_path = os.path.join(os.path.dirname(__file__), "id_telegram")
pub_path = priv_path + ".pub"

with open(priv_path, "wb") as f:
    f.write(priv_pem)

with open(pub_path, "wb") as f:
    f.write(pub_ssh)

pub = pub_ssh.decode().strip()
print(f"Keys saved!")
print(f"\n=== PUBLIC KEY (вставьте в VPS) ===")
print(pub)
print("=== END ===")