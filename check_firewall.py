import paramiko
import os
import time

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

# Проверить какие порты открыты на сервере
for i in range(10):
    try:
        print(f"Try {i+1}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=15)
        
        print("Connected!")
        
        # Показать все открытые порты
        stdin, stdout, stderr = client.exec_command('ss -tlnp | grep -E "docker|LISTEN"')
        print("\n=== OPEN PORTS ===")
        print(stdout.read().decode())
        
        # Проверить iptables INPUT
        stdin, stdout, stderr = client.exec_command('iptables -L INPUT -n --line-numbers')
        print("\n=== IPTABLES INPUT ===")
        print(stdout.read().decode())
        
        client.close()
        break
    except Exception as e:
        print(f"Error: {str(e)[:60]}")
        time.sleep(5)