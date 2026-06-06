import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# mtproxy с fake-TLS и защитой
commands = [
    "docker rm -f teleproxy telemt",
    "docker run -d --name mtproxy --restart unless-stopped -p 443:443 -p 8443:443 -e SECRET=828fbd61cb5472a4a3434b67ba5e74d3 -e WORKERS=4 -e PORT=443 jahus/mtproxy:latest"
]

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"=== {cmd} ===")
        print(stdout.read().decode())
    
    import time
    time.sleep(15)
    
    stdin, stdout, stderr = client.exec_command('docker ps')
    print("\n=== CONTAINERS ===")
    print(stdout.read().decode())
    
    stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1')
    logs = stdout.read().decode()
    print("\n=== LOGS ===")
    print(logs[:500])
    
    if 'tg://' in logs or 't.me/proxy' in logs:
        print("\n>>> LINK FOUND! <<<")
    
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")