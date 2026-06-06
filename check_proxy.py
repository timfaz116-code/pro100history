import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(
        hostname='2.26.143.133',
        port=22,
        username='root',
        password='dFc089nR1kHibfJO',
        timeout=30,
        allow_agent=False,
        look_for_keys=False
    )
    
    # Проверить статус Docker
    commands = [
        "docker ps -a",
        "docker logs telemt 2>&1",
        "docker images"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"\n=== {cmd} ===")
        print(stdout.read().decode())
        print(stderr.read().decode())
    
    client.close()
except Exception as e:
    print(f"Ошибка: {e}")