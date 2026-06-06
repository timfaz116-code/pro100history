import paramiko
import os
import time

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

for attempt in range(3):
    try:
        print(f"Attempt {attempt+1}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
        
        # Проверить статус
        stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Names}}: {{.Status}}"')
        print("Status:", stdout.read().decode().strip())
        
        # Получить ссылку
        secret = "0fd310829966b5189b9b4bd92d8be5a5"
        link = f"https://t.me/proxy?server=2.26.143.133&port=443&secret={secret}"
        print(f"\n=== LINK ===")
        print(link)
        print(f"Secret: {secret}")
        
        client.close()
        break
    except Exception as e:
        print(f"Failed: {e}")
        time.sleep(5)