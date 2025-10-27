"""
Servidor de chat simple usando selectors.
- Acepta múltiples clientes.
- Broadcast: lo que envía un cliente llega a todos los demás.
- Usa non-blocking sockets y selectors.
- Maneja desconexiones limpias y socketes muertos.
"""

import selectors
import socket
import types
import sys
import traceback

HOST = '0.0.0.0'
PORT = 5000
sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # socket ya en modo non-blocking
    print(f"Conexión entrante desde {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    sel.register(conn, selectors.EVENT_READ, data=data)

def broadcast(sender_sock, message_bytes):
    # Enviar message_bytes a todos menos al sender
    to_remove = []
    for key in list(sel.get_map().values()):
        sock = key.fileobj
        data = key.data
        # saltar el socket del servidor (es un socket escuchador sin data)
        if data is None:
            continue
        if sock is sender_sock:
            continue
        try:
            sock.sendall(message_bytes)
        except Exception as e:
            print(f"[!] Error enviando a {data.addr}: {e}. Marcando para eliminar.")
            to_remove.append(sock)
    # limpiar sockets fallidos
    for s in to_remove:
        safe_unregister_and_close(s)

def safe_unregister_and_close(sock):
    try:
        key = sel.get_key(sock)
        addr = key.data.addr if key.data else ('?', '?')
    except KeyError:
        addr = ('?', '?')
    try:
        sel.unregister(sock)
    except Exception:
        pass
    try:
        sock.close()
    except Exception:
        pass
    print(f"Conexión cerrada: {addr}")

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    try:
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(4096)  # recibe bytes
            if recv_data:
                # Mensaje recibido: reenviarlo a todos
                # Opcional: puedes inspeccionar/parsear el mensaje aquí
                prefix = f"[{data.addr[0]}:{data.addr[1]}] ".encode('utf-8')
                broadcast(sock, prefix + recv_data)
            else:
                # socket cerrado por el cliente
                print(f"Cliente {data.addr} desconectó.")
                safe_unregister_and_close(sock)
    except ConnectionResetError:
        print(f"ConnectionResetError: {data.addr} desapareció abruptamente.")
        safe_unregister_and_close(sock)
    except Exception:
        print("Excepción durante servicio de conexión:")
        traceback.print_exc()
        safe_unregister_and_close(sock)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lsock:
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((HOST, PORT))
        lsock.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}")
        lsock.setblocking(False)
        # Registrar socket de escucha con data=None para identificarlo
        sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        # Evento en socket de escucha -> aceptar nueva conexión
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
        except KeyboardInterrupt:
            print("Servidor detenido por usuario (Ctrl-C).")
        finally:
            # Cerrar todo
            keys = list(sel.get_map().values())
            for k in keys:
                obj = k.fileobj
                try:
                    sel.unregister(obj)
                except Exception:
                    pass
                try:
                    obj.close()
                except Exception:
                    pass
            sel.close()
            print("Servidor cerrado.")

if __name__ == "__main__":
    main()
