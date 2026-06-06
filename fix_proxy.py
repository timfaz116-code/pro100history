import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Пробуем другой образ - mtproxy-docker
commands = [
    "docker rm -f telemt",
    "docker run -d --name telemt --restart unless-stopped -p 443:443 -e MTPROXY_SECRET=828fbd61cb5472a4a3434b67ba5e74d3 -e MTPROXY_PUBLIC_HOST=2.26.143.133 ghcr.io/wukko/mtproxy-docker:latest"
]

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"=== {cmd} ===")
        print(stdout.read().decode() + stderr.read().decode())
    
    import time
    time.sleep(15)
    
    stdin, stdout, stderr = client.exec_command('docker logs telemt 2>&1 | tail -30')
    output = stdout.read().decode()
    print("\n=== LOGS ===")
    print(output)
    
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")