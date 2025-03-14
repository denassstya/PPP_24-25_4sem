import socket
import os
import datetime
import logging

#Настройка логирования
logging.basicConfig(filename="client.log", level=logging.INFO, format="%(asctime)s - %(message)s")

HOST = "127.0.0.1"
PORT = 65432


def save_file(data):
    """Сохраняет файл с процессами в директории с датой и временем"""
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    #Определяем формат файла по содержимому
    format_type = "json" if data.strip().startswith(b"[") else "xml"

    directory = f"./{timestamp[:10]}"  #Папка с датой (dd-mm-yyyy)
    os.makedirs(directory, exist_ok=True)

    filename = f"{directory}/{timestamp}.{format_type}"
    with open(filename, "wb") as f:
        f.write(data)

    logging.info(f"Файл сохранен: {filename}")
    print(f"Файл сохранен в {filename}")


def start_client():
    """Запуск клиента"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        logging.info(f"Подключение к серверу {HOST}:{PORT}")
        print(f"Подключено к серверу {HOST}:{PORT}")

        while True:
            command = input("Введите команду (update/signal <PID> <SIGNAL>/exit): ").strip()
            if not command:
                continue

            client.sendall(command.encode())

            if command == "update":
                data = client.recv(4096)
                save_file(data)

                if not data:
                    print("Ошибка: сервер не отправил данных.")
                    continue

                save_file(data)

            elif command.startswith("signal"):
                response = client.recv(1024).decode()
                print(response)

            elif command == "exit":
                logging.info("Клиент завершает работу")
                print("Выход из клиента.")
                break

            else:
                print("Ошибка: неизвестная команда")


if __name__ == "__main__":
    start_client()