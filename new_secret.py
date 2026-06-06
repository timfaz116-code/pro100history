import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=60)
    
    # Сгенерировать секрет
    stdin, stdout, stderr = client.exec_command('openssl rand -hex 16')
    secret = stdout.read().decode().strip()
    print(f"New secret: {secret}")
    
    # Запустить с новым секретом
    commands = [
        "docker rm -f mtproxy",
        f"docker run -d --name mtproxy --restart unless-stopped -p 443:443 -p 8443:443 -e SECRET={secret} -e WORKERS=2 jahus/mtproxy:latest"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"=== {cmd[:60]}... ===")
        print(stdout.read().decode())
    
    import time
    time.sleep(15)
    
    # Получить ссылку
    stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1')
    logs = stdout.read().decode()
    
    # Найти ссылку
    for line in logs.split('\n'):
        if 't.me/proxy' in line or 'tg://' in line:
            print(f"\n>>> LINK: {line.strip()} <<<")
    
    # Проверить работоспособность
    stdin, stdout, stderr = client.exec_command('docker ps')
    print("\n=== STATUS ===")
    print(stdout.read().decode())
    
    client.close()
except Exception as e:
    print(f"Error: {e}")