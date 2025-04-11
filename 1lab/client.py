# client.py
import json
import logging
import os
import socket
from datetime import datetime

LOG_PATH = 'client_activity.log'
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_log_folder():
    """Создает папку для логов с текущей датой в названии"""
    now = datetime.now()
    folder_name = now.strftime("logs/%Y-%m-%d")
    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f"Создана папка для логов: {folder_name}")
    except OSError as err:
        print(f"Ошибка создания папки: {err}")
        return None
    return folder_name


def store_response(data, folder, command):
    """Сохраняет ответ сервера в JSON файл"""
    if not folder:
        print("Не указана папка для сохранения")
        return

    time_now = datetime.now()
    safe_cmd = command.replace(" ", "_").replace(":", "-")
    filename = time_now.strftime(f"%H-%M-%S_{safe_cmd}.json")
    full_path = os.path.join(folder, filename)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            try:
                json_content = json.loads(data.decode('utf-8'))
                json.dump(json_content, f, indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                f.write(data.decode('utf-8'))
        print(f"Данные сохранены в: {full_path}")
        logging.info(f"Сохранено в: {full_path}")
    except IOError as err:
        print(f"Ошибка записи: {err}")
        logging.error(f"Ошибка записи: {err}")


def server_communication(command):
    """Обмен данными с сервером"""
    server_config = ('127.0.0.1', 12345)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)

        try:
            sock.connect(server_config)
        except socket.timeout:
            print("Таймаут подключения")
            return

        print(f"Отправка команды: {command}")
        sock.sendall(command.encode('utf-8'))

        received_data = b''
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                received_data += chunk
        except socket.timeout:
            print("Таймаут получения данных")
        except Exception as e:
            print(f"Ошибка получения: {e}")
        finally:
            sock.close()

        if received_data:
            print("Данные получены")
            log_dir = create_log_folder()
            store_response(received_data, log_dir, command)
        else:
            print("Нет данных от сервера")

    except socket.gaierror as e:
        print(f"DNS ошибка: {e}")
        logging.error(f"DNS: {e}")
    except ConnectionRefusedError:
        print("Сервер недоступен")
        logging.error("Сервер не отвечает")
    except Exception as e:
        print(f"Ошибка: {e}")
        logging.error(f"Ошибка: {e}")


if __name__ == "__main__":
    # Запуск клиента с командой "update"
    server_communication("update")
