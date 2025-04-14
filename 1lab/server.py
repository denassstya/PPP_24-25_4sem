from main import HOST, PORT
import socket
import struct
import os
import json
import datetime
import signal
import platform
import subprocess

HOST = '127.0.0.1'
PORT = 65432

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open("server.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
    print(message)

def get_process_info():
    """Получает информацию о процессах в системе (кроссплатформенно)."""
    process_list = []
    try:
        if platform.system() == "Windows":
            # Используем tasklist для получения информации о процессах в Windows
            tasklist_output = subprocess.check_output(["tasklist"], text=True, encoding="utf-8")
            for line in tasklist_output.splitlines()[3:]:  # Пропускаем заголовки
                parts = line.split()
                if len(parts) >= 2:
                    process_name = parts[0]
                    pid = parts[1]
                    process_list.append({"name": process_name, "pid": pid})
        else:  # Linux/macOS
            process_list = os.popen('ps -ax').read().splitlines()
            process_list = [{"name": process, "pid": "N/A"} for process in process_list]

    except Exception as e:
        log_message(f"Ошибка при получении информации о процессах: {e}")
        return []

    return process_list

def send_data(conn, data):
    try:
        serialized_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        data_len = len(serialized_data)
        conn.sendall(struct.pack(">I", data_len))
        conn.sendall(serialized_data)
        log_message(f"Отправлено {data_len} байт данных")

    except Exception as e:
        log_message(f"Ошибка при отправке данных: {e}")

def receive_data(conn):
    try:
        prefix_size = struct.calcsize(">I")
        prefix = conn.recv(prefix_size)

        if not prefix:
            log_message("Клиент преждевременно закрыл соединение")
            return None

        (data_len,) = struct.unpack(">I", prefix)

        received_data = b""
        while len(received_data) < data_len:
            chunk = conn.recv(min(data_len - len(received_data), 4096))
            if not chunk:
                log_message("Клиент преждевременно закрыл соединение")
                return None
            received_data += chunk

        return json.loads(received_data.decode("utf-8"))

    except Exception as e:

        log_message(f"Ошибка получения данных: {e}")
        return None

def handle_client_request(conn, addr):
        log_message(f'Подключился клиент {addr}')

        try:
            while True:
                request = receive_data(conn)
                if not request:
                    break

                command = request.get("command")

                if command == "get_processes":
                    process_info = get_process_info()
                    send_data(conn, process_info)

                elif command == "send_signal":
                    pid = request.get("pid")
                    sig = request.get("signal")

                    try:
                        os.kill(int(pid), getattr(signal, sig))
                        log_message(f"Отправлен сигнал {sig} процессу с PID {pid}")
                        send_data(conn, {"status": "ok"})

                    except Exception as e:
                        log_message(f"Ошибка при отправке сигнала: {e}")
                        send_data(conn, {"status": "error", "message": str(e)})

                elif command == "close":
                    log_message("Клиент запросил закрытие соединения.")
                    break

                else:
                    log_message(f"Неизвестная команда: {command}")
                    send_data(conn, {"status": "error", "message": "Неизвестная команда"})

        except Exception as e:
            log_message(f"Ошибка при обработке запроса клиента: {e}")

        finally:
            conn.close()
            log_message(f'Соединение с {addr} закрыто')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        log_message(f"Сервер запущен на {HOST}:{PORT}")

        while True:
            try:
                conn, addr = s.accept()
                handle_client_request(conn, addr)
            except Exception as e:
                log_message(f"Ошибка в основном цикле сервера: {e}")
                break
