import json
import logging
import os
import psutil
import socket

logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def collect_process_data():
    """Сбор информации о запущенных процессах"""
    process_list = []

    for proc in psutil.process_iter(['pid', 'name', 'status']):
        try:
            proc_info = proc.info
            process_list.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return process_list


def write_json_file(data, filename='processes.json'):
    """Запись данных в JSON файл"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Сохранено в {filename}")
    except Exception as e:
        logging.error(f"Ошибка сохранения {filename}: {e}")


def process_client_request(connection, address):
    """Обработка запросов клиента"""
    logging.info(f"Клиент подключен: {address}")
    print(f"Клиент {address} подключен")

    try:
        while True:
            try:
                client_cmd = connection.recv(1024).decode('utf-8').strip()
                if not client_cmd:
                    break

                if client_cmd == "update":
                    print(f"Клиент {address} запросил обновление")
                    processes = collect_process_data()
                    write_json_file(processes)

                    try:
                        with open('processes.json', 'rb') as f:
                            json_data = f.read()
                        connection.sendall(json_data)
                        print(f"Данные отправлены {address}")
                        logging.info(f"Данные отправлены {address}")
                    except FileNotFoundError:
                        err_msg = "Файл не найден"
                        print(err_msg)
                        logging.error(err_msg)
                        connection.sendall(err_msg.encode('utf-8'))
                    except Exception as e:
                        err_msg = f"Ошибка отправки: {e}"
                        print(err_msg)
                        logging.error(err_msg)
                        connection.sendall(err_msg.encode('utf-8'))

                    break
                else:
                    response = f"Неизвестная команда: {client_cmd}"
                    connection.sendall(response.encode('utf-8'))
                    logging.warning(f"Неизвестная команда от {address}: {client_cmd}")

            except ConnectionResetError:
                print(f"Клиент {address} отключился")
                logging.warning(f"Клиент {address} отключился")
                break
            except Exception as e:
                print(f"Ошибка обработки {address}: {e}")
                logging.error(f"Ошибка обработки {address}: {e}")
                break

    finally:
        connection.close()
        print(f"Закрыто соединение с {address}")
        logging.info(f"Закрыто соединение с {address}")


def start_server():
    """Запуск сервера"""
    host = '127.0.0.1'
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind((host, port))
        except OSError as e:
            print(f"Ошибка привязки: {e}")
            logging.critical(f"Ошибка привязки: {e}")
            return

        s.listen()
        print(f"Сервер запущен на {host}:{port}")
        logging.info(f"Сервер запущен на {host}:{port}")

        try:
            while True:
                conn, addr = s.accept()
                process_client_request(conn, addr)
        except KeyboardInterrupt:
            print("Остановка сервера...")
            logging.info("Сервер остановлен")
        finally:
            s.close()
            logging.info("Сервер выключен")
            print("Сервер выключен")


if __name__ == "__main__":
    start_server()
