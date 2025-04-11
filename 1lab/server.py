import json
import socket
import logging
import psutil
import os

# Настройка логирования
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')


# Логируются только сообщения уровня INFO и выше.


def get_process_info():
    """Получает информацию о всех процессах и
       возвращает её в виде списка словарей."""
    processes = []
    # Итерируется по всем процессам и получает их PID, имя и статус.
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            process_info = proc.info
            processes.append(process_info)
        # Игнорируем процессы, которые недоступны
        # (например, завершенные или системные).
        except (psutil.NoSuchProcess, psutil.AccessDenied,
                psutil.ZombieProcess):
            continue
    return processes


def save_to_json(data, filename='processes.json'):
    """Сохраняет данные в JSON файл."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Данные успешно сохранены в файл {filename}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных в файл {filename}: {e}")

def handle_client(conn, addr):
    """Обрабатывает запросы клиента."""
    logging.info(f"Подключен клиент: {addr}")
    print(f"Клиент {addr} подключен.")
    try:
        while True:
            try:
                # Получаем команду от клиента
                command = conn.recv(1024).decode('utf-8').strip()
                if not command:
                    break

                if command == "update":
                    print(f"Клиент {addr} запросил обновление информации о процессах.")
                    processes = get_process_info()
                    save_to_json(processes)

                    try:
                        with open('processes.json', 'rb') as f:
                            file_data = f.read()
                        conn.sendall(file_data)  # Отправляем данные
                        print(f"Файл processes.json отправлен клиенту {addr}.")
                        logging.info(f"Файл processes.json успешно отправлен клиенту {addr}")
                    except FileNotFoundError:
                        error_message = "Файл processes.json не найден на сервере."
                        print(error_message)
                        logging.error(error_message)
                        conn.sendall(error_message.encode('utf-8'))  # Отправляем сообщение об ошибке клиенту
                    except Exception as e:
                        error_message = f"Ошибка при отправке файла processes.json клиенту: {e}"
                        print(error_message)
                        logging.error(error_message)
                        conn.sendall(error_message.encode('utf-8'))  # Отправляем сообщение об ошибке клиенту

                    break  # Закрываем соединение после отправки данных
                else:
                    response = f"Неизвестная команда: {command}"
                    conn.sendall(response.encode('utf-8'))
                    logging.warning(f"Клиент {addr} отправил неизвестную команду: {command}")

            except ConnectionResetError:
                print(f"Клиент {addr} внезапно разорвал соединение.")
                logging.warning(f"Клиент {addr} внезапно разорвал соединение.")
                break
            except Exception as e:
                print(f"Ошибка при обработке запроса от клиента {addr}: {e}")
                logging.error(f"Ошибка при обработке запроса от клиента {addr}: {e}")
                break  # Выходим из цикла обработки клиента при любой ошибке

    finally:
        conn.close()
        print(f"Соединение с клиентом {addr} закрыто.")
        logging.info(f"Соединение с клиентом {addr} закрыто.")


def server():
    """Запускает сервер."""
    host = '127.0.0.1'  # Loopback address (localhost)
    port = 12345  # Choose a port

    # Создаем IPv4 TCP сокет
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Позволяем повторно использовать адрес, если сервер был аварийно завершен
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Привязываем сокет к адресу и порту
        try:
            s.bind((host, port))
        except OSError as e:
            print(f"Невозможно привязать адрес к порту: {e}")
            logging.critical(f"Невозможно привязать адрес к порту: {e}")
            return  # Завершаем работу сервера
        # Начинаем прослушивать входящие соединения
        s.listen()
        print(f"Сервер прослушивает {host}:{port}")
        logging.info(f"Сервер запущен и прослушивает {host}:{port}")

        try:
            while True:
                conn, addr = s.accept()
                handle_client(conn, addr)
        except KeyboardInterrupt:
            print("Сервер завершает работу...")
            logging.info("Сервер завершает работу по сигналу KeyboardInterrupt.")
        finally:
            s.close()
            logging.info("Сервер остановлен.")
            print("Сервер остановлен.")


if __name__ == "__main__":
    server()
