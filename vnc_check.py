import socket

vnc_host = "147.135.255.230"
vnc_port = 5969

try:
    print(f"Подключение к VNC {vnc_host}:{vnc_port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((vnc_host, vnc_port))
    if result == 0:
        print("Порт открыт!")
        data = sock.recv(1024)
        print(f"Данные: {data[:100]}")
    else:
        print(f"Порт закрыт или недоступен: {result}")
    sock.close()
except Exception as e:
    print(f"Ошибка: {e}")