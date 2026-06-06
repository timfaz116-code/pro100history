import socket

# Проверка порта 8443
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    sock.connect(('2.26.143.133', 8443))
    print("PORT 8443: OPEN")
    sock.close()
except Exception as e:
    print(f"PORT 8443: CLOSED - {e}")