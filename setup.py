import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    # Удаляем старые и ставим Teleproxy с fake-TLS
    commands = [
        "docker rm -f mtproxy teleproxy telemt",
        "docker run -d --name teleproxy --restart unless-stopped -p 443:443 -p 8443:443 ghcr.io/teleproxy/teleproxy:latest -S 828fbd61cb5472a4a3434b67ba5e74d3 -H 443 --direct -p 8888"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode() + stderr.read().decode())
    
    import time
    time.sleep(10)
    
    # Проверить статус
    stdin, stdout, stderr = client.exec_command('docker ps')
    print("=== CONTAINERS ===")
    print(stdout.read().decode())
    
    # Получить логи и ссылку
    stdin, stdout, stderr = client.exec_command('docker logs teleproxy 2>&1')
    logs = stdout.read().decode()
    print("=== LOGS ===")
    print(logs)
    
    client.close()
except Exception as e:
    print(f"Error: {e}")