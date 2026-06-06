import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    secret = "0fd310829966b5189b9b4bd92d8be5a5"
    
    # Запустить на порту 8080
    commands = [
        "docker rm -f mtproxy",
        f"docker run -d --name mtproxy --restart unless-stopped -p 8080:443 -e SECRET={secret} -e PORT=443 -e WORKERS=2 jahus/mtproxy:latest"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
    
    import time
    time.sleep(10)
    
    # Проверить
    stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Ports}}"')
    print("\nPorts:", stdout.read().decode().strip())
    
    link = f"https://t.me/proxy?server=2.26.143.133&port=8080&secret={secret}"
    print(f"\n=== NEW LINK (port 8080) ===")
    print(link)
    
    client.close()
except Exception as e:
    print(f"Error: {e}")