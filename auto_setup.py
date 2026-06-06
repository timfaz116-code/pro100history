import paramiko
import os
import time

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

for i in range(10):
    try:
        print(f"Try {i+1}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=15)
        
        secret = "0fd310829966b5189b9b4bd92d8be5a5"
        
        commands = [
            "docker rm -f mtproxy",
            f"docker run -d --name mtproxy --restart unless-stopped -p 8080:443 -e SECRET={secret} -e PORT=443 jahus/mtproxy:latest"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
        
        time.sleep(8)
        
        stdin, stdout, stderr = client.exec_command('docker ps --format "{{.Ports}}"')
        print("Ports:", stdout.read().decode().strip())
        
        print(f"\nLink: https://t.me/proxy?server=2.26.143.133&port=8080&secret={secret}")
        
        client.close()
        break
    except Exception as e:
        print(f"Error: {str(e)[:50]}")
        time.sleep(3)