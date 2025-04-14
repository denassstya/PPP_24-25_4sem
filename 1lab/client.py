from main import HOST, PORT
import socket
import struct
import json
import datetime
import os
import platform
import xml.etree.ElementTree as ET

HOST = '127.0.0.1'
PORT = 65432

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open("client.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
    print(message)

def send_data(sock, data):
    try:
        serialized_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        data_len = len(serialized_data)
        sock.sendall(struct.pack(">I", data_len))
        sock.sendall(serialized_data)
        log_message(f"Отправлено {data_len} байт данных")

    except Exception as e:
        log_message(f"Ошибка при отправке данных: {e}")

def receive_data(conn):
    try:
        prefix_size = struct.calcsize(">I")
        prefix = conn.recv(prefix_size)

        if not prefix:
            log_message("Сервер преждевременно закрыл соединение")
            return None

        (data_len,) = struct.unpack(">I", prefix)

        received_data = b""
        while len(received_data) < data_len:
            chunk = conn.recv(min(data_len - len(received_data), 4096))
            if not chunk:
                log_message("Сервер преждевременно закрыл соединение")
                return None
            received_data += chunk

        return json.loads(received_data.decode("utf-8"))

    except Exception as e:
        log_message(f"Ошибка получения данных: {e}")
        return None

def save_data_to_file(data, file_format="json"):
    now = datetime.datetime.now()
    directory = now.strftime("%d-%m-%Y")
    filename = now.strftime("%H:%M:%S")

    directory_path = os.path.join(os.getcwd(), directory)

    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            log_message(f"Создана директория: {directory_path}")
        except OSError as e:
            log_message(f"Ошибка при создании директории {directory_path}: {e}")
            return False

    filepath = os.path.join(directory_path, f"{filename}.{file_format}")

    try:
        if file_format == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            log_message(f"Данные сохранены в файл: {filepath}")
            return True
        elif file_format == "xml":

            root = ET.Element("processes")

            for process in data:
                process_element = ET.SubElement(root, "process")
                name_element = ET.SubElement(process_element, "name")
                name_element.text = process["name"]
                pid_element = ET.SubElement(process_element, "pid")
                pid_element.text = process["pid"]

            tree = ET.ElementTree(root)
            ET.indent(tree, space="\t", level=0)
            tree.write(filepath, encoding="utf-8", xml_declaration=True)
            log_message(f"Данные сохранены в файл: {filepath}")
            return True
        else:
            log_message("Неподдерживаемый формат файла")
            return False

    except Exception as e:
        log_message(f"Ошибка при сохранении данных в файл: {e}")
        return False

def send_signal_command(sock, pid, signal_name):
    """Отправляет команду на отправку сигнала процессу (кроссплатформенно)."""

    if platform.system() == "Windows":
        log_message("Отправка сигналов в Windows не поддерживается.")
        return

    request = {"command": "send_signal", "pid": pid, "signal": signal_name}
    send_data(sock, request)
    response = receive_data(sock)

    if response and response.get("status") == "ok":
        log_message(f"Сигнал {signal_name} успешно отправлен процессу с PID {pid}")
    else:
        log_message(f"Ошибка при отправке сигнала: {response}")

def get_signal_list():
  """Возвращает список доступных сигналов."""
  signals = [s for s in dir(signal) if s.startswith("SIG") and not s.startswith("SIG_")]
  return signals

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        log_message(f"Подключился к серверу {HOST}:{PORT}")

        while True:
            command = input("Введите команду (get_processes, send_signal, close, help): ")

            if command == "get_processes":
                format_input = input("В каком формате сохранить файл (json/xml)? ").lower()
                if format_input not in ("json", "xml"):
                    log_message("Неверный формат. Сохраняю в json.")
                    format_input = "json"

                request = {"command": "get_processes"}
                send_data(s, request)
                data = receive_data(s)

                if data:
                    print("Список процессов:\n", data)
                    save_data_to_file(data, format_input)
                    log_message(f"Получен и сохранен список процессов от сервера в формате {format_input}")
                else:
                    log_message("Не удалось получить данные от сервера")

            elif command == "send_signal":
                pid_str = input("Введите PID процесса: ")
                try:
                    pid = int(pid_str)
                    signal_name = input("Введите сигнал (например, SIGTERM, SIGKILL или 'help' для списка): ")
                    if signal_name == "help":
                      print("Доступные сигналы:")
                      for signal in get_signal_list():
                        print(signal)
                    else:
                      send_signal_command(s, pid, signal_name)
                except ValueError:
                    log_message("Неверный формат PID. Введите целое число.")

            elif command == "close":
                request = {"command": "close"}
                send_data(s, request)
                log_message("Запрос на закрытие соединения отправлен")
                break

            elif command == "help":
              print("Доступные команды:")
              print("  get_processes - получить список процессов")
              print("  send_signal   - отправить сигнал процессу")
              print("  close         - закрыть соединение")
              print("  help          - показать список команд")

            else:
                log_message("Неизвестная команда")

    except Exception as e:
        log_message(f"Ошибка: {e}")

    finally:
        s.close()
        log_message("Соединение закрыто")
