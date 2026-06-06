import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=60)
    
    # Перезапуск с автоматическим секретом
    commands = [
        "docker rm -f mtproxy",
        "docker run -d --name mtproxy --restart unless-stopped -p 443:443 -p 8443:443 -e WORKERS=2 jahus/mtproxy:latest"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"=== {cmd} ===")
        print(stdout.read().decode())
    
    import time
    time.sleep(10)
    
    # Получить секрет и ссылку
    stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1 | grep -E "secret|Secret|tg://|Add in"')
    print("\n=== LINKS ===")
    print(stdout.read().decode())
    
    # Проверить логи полностью
    stdin, stdout, stderr = client.exec_command('docker logs mtproxy 2>&1 | tail -15')
    print("\n=== RECENT LOGS ===")
    print(stdout.read().decode())
    
    client.close()
except Exception as e:
    print(f"Error: {e}")