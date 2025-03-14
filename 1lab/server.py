import socket
import os
import json
import xml.etree.ElementTree as ET
import logging
import signal

#Настройка логирования
logging.basicConfig(filename="server.log", level=logging.INFO, format="%(asctime)s - %(message)s")

HOST = "127.0.0.1"
PORT = 65432
DATA_FORMAT = "json"  #Можно менять на "xml"


def get_process_info():
    """Собирает информацию о запущенных процессах"""
    processes = []
    for proc in os.popen("ps aux").readlines():
        parts = proc.split()
        if len(parts) > 10:
            processes.append({
                "USER": parts[0],
                "PID": parts[1],
                "CPU": parts[2],
                "MEM": parts[3],
                "COMMAND": " ".join(parts[10:])
            })

    if DATA_FORMAT == "json":
        with open("processes.json", "w") as f:
            json.dump(processes, f, indent=4)
        logging.info("Информация о процессах сохранена в JSON")

    elif DATA_FORMAT == "xml":
        root = ET.Element("Processes")
        for proc in processes:
            proc_elem = ET.SubElement(root, "Process")
            for key, value in proc.items():
                child = ET.SubElement(proc_elem, key)
                child.text = value
        tree = ET.ElementTree(root)
        tree.write("processes.xml")
        logging.info("Информация о процессах сохранена в XML")


def handle_signal(pid, sig):
    """Отправка сигнала процессу"""
    signal_dict = {
        "SIGTERM": signal.SIGTERM,
        "SIGKILL": signal.SIGKILL,
        "SIGSTOP": signal.SIGSTOP,
        "SIGCONT": signal.SIGCONT
    }

    try:
        if sig not in signal_dict:
            return f"Ошибка: неизвестный сигнал {sig}"

        os.kill(int(pid), signal_dict[sig])
        logging.info(f"Отправлен сигнал {sig} процессу {pid}")
        return f"Сигнал {sig} отправлен процессу {pid}"
    except Exception as e:
        logging.error(f"Ошибка при отправке сигнала: {e}")
        return str(e)


def start_server():
    """Запуск сервера"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        logging.info(f"Сервер запущен на {HOST}:{PORT}")
        print(f"Сервер слушает на {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                logging.info(f"Подключение от {addr}")
                print(f"Подключение от {addr}")

                while True:
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break

                    logging.info(f"Получена команда: {data}")

                    if data == "update":
                        get_process_info()
                        filename = "processes.json" if DATA_FORMAT == "json" else "processes.xml"
                        with open(filename, "rb") as f:
                            conn.sendall(f.read())

                    elif data.startswith("signal"):
                        parts = data.split()
                        if len(parts) != 3:
                            conn.sendall("Ошибка: неправильный формат команды".encode())
                        else:
                            _, pid, sig = parts
                            response = handle_signal(pid, sig)
                            conn.sendall(response.encode())

                    elif data == "exit":
                        logging.info("Завершение соединения с клиентом")
                        break

                    else:
                        conn.sendall("Ошибка: неизвестная команда".encode())


if __name__ == "__main__":
    start_server()