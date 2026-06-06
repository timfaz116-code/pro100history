import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Попробуем с более длительным ожиданием
try:
    print("ПодключениеSSH...")
    transport = client.get_transport()
    transport.banner_timeout = 60
    
    client.connect(
        hostname='2.26.143.133',
        port=22,
        username='root',
        password='dFc089nR1kHibfJO',
        timeout=60,
        allow_agent=False,
        look_for_keys=False,
        gss_auth=False,
        disabled_algorithms={
            'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']
        }
    )
    
    stdin, stdout, stderr = client.exec_command('echo test')
    print("Результат:", stdout.read().decode())
    client.close()
    print("ОК")
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()