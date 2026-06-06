import paramiko
import os
import time

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

# Пробуем несколько попыток
for attempt in range(5):
    try:
        print(f"Attempt {attempt+1}/5...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=20)
        
        print("Connected!")
        
        # Проверить iptables
        stdin, stdout, stderr = client.exec_command('iptables -L -n | head -20')
        print("\n=== IPTABLES ===")
        print(stdout.read().decode())
        
        # Проверить docker
        stdin, stdout, stderr = client.exec_command('docker ps')
        print("\n=== DOCKER ===")
        print(stdout.read().decode())
        
        # Проверить логи
        stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1 | tail -10')
        print("\n=== LOGS ===")
        print(stdout.read().decode())
        
        client.close()
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(3)