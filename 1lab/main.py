import os
import subprocess
import platform

HOST = '127.0.0.1'
PORT = 65432

def run_client():
    """Запускает клиент."""
    print("Запускаю клиент...")
    try:
        if platform.system() == "Windows":
            subprocess.run(["python", "client.py"], check=True, env=os.environ.copy())
        else:
            subprocess.run(["python3", "client.py"], check=True, env=os.environ.copy())
        print("Клиент завершил работу.") 
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске клиента: {e}")

def run_server():
    """Запускает сервер."""
    print("Запускаю сервер...")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["python", "server.py"], env=os.environ.copy()) 
        else:
            subprocess.Popen(["python3", "server.py"], env=os.environ.copy()) 
        print("Сервер запущен в фоновом режиме.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске сервера: {e}")


def main():
    """Основная функция программы."""
    while True:
        print("\nВыберите действие:")
        print("1. Запустить клиент")
        print("2. Запустить сервер")
        print("3. Выйти")

        choice = input("Введите номер действия: ")

        if choice == "1":
            run_client()
        elif choice == "2":
            run_server()
        elif choice == "3":
            break
        else:
            print("Неверный ввод. Попробуйте еще раз.")

if __name__ == "__main__":
    main()
