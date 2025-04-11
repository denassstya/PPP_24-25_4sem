import socket
import logging
import os
from datetime import datetime

# Настройка системы логирования
log_file_path = 'client_activity.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def make_log_directory():
    """Создает каталог для хранения журнальных файлов, основанный на текущей дате."""
    current_time = datetime.now()
    directory_name = current_time.strftime("logs/%Y-%m-%d")  # Изменен формат и имя папки
    try:
        os.makedirs(directory_name, exist_ok=True)  # Создаем директорию, если её нет
        print(f"Журнальная директория создана: {directory_name}")
    except OSError as error_info:
        print(f"Ошибка при создании директории: {error_info}")
        return None
    return directory_name

def archive_data(retrieved_data, log_directory, user_command):
    """Сохраняет полученную информацию в файл, имя которого зависит от команды и времени."""
    if not log_directory:
        print("Невозможно сохранить данные: отсутствует путь к директории.")
        return
    current_time = datetime.now()

    # Приводим команду к безопасному формату для имени файла
    valid_command = user_command.replace(" ", "_").replace(":", "-")
    file_title = current_time.strftime(f"%H-%M-%S_{valid_command}.dat")  # Изменен формат и расширение
    full_path = os.path.join(log_directory, file_title)
    try:
        with open(full_path, 'wb') as destination:
            destination.write(retrieved_data)
        print(f"Данные успешно записаны в файл: {full_path}")
        logging.info(f"Данные заархивированы в: {full_path}")
    except IOError as error_info:
        print(f"Ошибка ввода/вывода при сохранении: {error_info}")
        logging.error(f"Ошибка сохранения данных: {error_info}")

def interact_with_server(user_input):
    """Устанавливает связь с сервером, отправляет команду и обрабатывает ответ."""
    server_address = ('127.0.0.1', 12345)  # Статичный адрес и порт сервера

    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.settimeout(10.0)  # Устанавливаем таймаут для подключения
        try:
            connection.connect(server_address) # Пытаемся установить соединение
        except socket.timeout:
             print("Превышено время ожидания подключения к серверу.")
             return  # Выходим, если не удалось подключиться
        print(f"Передача команды на сервер: {user_input}")
        connection.sendall(user_input.encode('utf-8'))

        # Ожидаем ответ от сервера
        total_data = b''
        try:
            while True:
                data_block = connection.recv(4096)
                if not data_block:
                    break  # Сигнал о конце передачи данных
                total_data += data_block
        except socket.timeout:
            print("Превышен лимит ожидания ответа от сервера")
        except Exception as err:
            print(f"Ошибка при получении данных: {err}")
        finally:
            connection.close()

        if total_data:
            print("Информация получена от сервера.")
            destination_directory = make_log_directory()
            archive_data(total_data, destination_directory, user_input)
        else:
            print("Никакой информации не получено от сервера.")

    except socket.gaierror as lookup_error:
        print(f"Ошибка разрешения имени хоста: {lookup_error}")
        logging.error(f"Ошибка DNS: {lookup_error}")
    except ConnectionRefusedError:
        print("Сервер отклонил подключение. Убедитесь, что он запущен.")
        logging.error("Серверное соединение не установлено.")
    except Exception as master_error:
        print(f"Непредвиденная ошибка: {master_error}")
        logging.error(f"Непредвиденная ошибка: {master_error}")


def application_entry():
    """Главная функция клиента."""
    print("Клиент запущен, ожидание подключения к серверу...")
    while True:
        print("\nДоступные действия:")
        print("update - запрос информации о процессах")
        print("send_signal <pid> <sig> - отправка сигнала процессу (только root)")
        print("terminate - завершение работы")

        user_selection = input("Введите команду: ").strip()

        if user_selection == "terminate":
            print("Завершение работы клиентского приложения...")
            break
        elif user_selection == "update" or user_selection.startswith("send_signal"):
            interact_with_server(user_selection)
        else:
            print("Введена некорректная команда. Повторите попытку.")


if __name__ == "__main__":
    application_entry()
