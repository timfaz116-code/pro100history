import paramiko
import os

key_path = os.path.join(os.path.dirname(__file__), "id_telegram")
private_key = paramiko.Ed25519Key.from_private_key_file(key_path)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname='2.26.143.133', port=22, username='root', pkey=private_key, timeout=30)
    
    commands = [
        "docker ps",
        "docker logs telemt 2>&1 | tail -20",
        "netstat -tlnp | grep 443"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"=== {cmd} ===")
        print(stdout.read().decode())
        print(stderr.read().decode())
    
    # Проверить iptables/firewall
    stdin, stdout, stderr = client.exec_command("iptables -L -n | grep 443")
    print("=== IPTABLES ===")
    print(stdout.read().decode())
    
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")