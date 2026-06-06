import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=60)
    
    import time
    time.sleep(10)
    
    # Получить все логи
    stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1')
    logs = stdout.read().decode()
    print("=== ALL LOGS ===")
    print(logs)
    
    # Построить ссылку вручную
    secret = "0fd310829966b5189b9b4bd92d8be5a5"
    link = f"https://t.me/proxy?server=2.26.143.133&port=443&secret={secret}"
    print(f"\n=== MANUAL LINK ===")
    print(link)
    
    client.close()
except Exception as e:
    print(f"Error: {e}")