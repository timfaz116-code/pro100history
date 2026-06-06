import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Пробую с ключом...")
    client.connect(
        hostname='2.26.143.133',
        port=22,
        username='root',
        pkey=private_key,
        timeout=25,
        allow_agent=False,
        look_for_keys=False
    )
    
    stdin, stdout, stderr = client.exec_command('docker logs telemt 2>&1')
    print(stdout.read().decode())
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")