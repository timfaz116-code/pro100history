import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Устанавливаем Teleproxy с защитой от DPI и fake-TLS
commands = [
    "docker rm -f telemt",
    "docker run -d --name teleproxy --restart unless-stopped -p 443:443 ghcr.io/teleproxy/teleproxy:latest -S 828fbd61cb5472a4a3434b67ba5e74d3 -H 443 --direct -p 8888 --aes-pwd /dev/null"
]

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"=== {cmd} ===")
        print(stdout.read().decode() + stderr.read().decode())
    
    import time
    time.sleep(10)
    
    stdin, stdout, stderr = client.exec_command('docker logs teleproxy 2>&1 | tail -20')
    print("\n=== LOGS ===")
    print(stdout.read().decode())
    
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")