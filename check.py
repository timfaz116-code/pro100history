import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Подключение...")
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1')
    logs = stdout.read().decode()
    print("=== LOGS ===")
    print(logs)
    
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")