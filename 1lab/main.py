import os
import platform
import subprocess

def refresh_display():
    """Очищает содержимое терминального окна."""
    operating_system = platform.system().lower()
    if operating_system == "windows":
        os.system('cls')
    else:
        os.system('clear')

def display_options():
    """Отображает интерактивное меню пользователю."""
    print("=" * 50)
    print("Система управления файлами (клиент/сервер)")
    print("""Для корректной работы системы необходимо запустить
          сервер и клиент в отдельных окнах терминала""")
    print("=" * 50)
    print("1) Запустить компонент сервера")
    print("2) Запустить компонент клиента")
    print("3) Завершить работу приложения")
    print("=" * 50)

def execute_program():
    """Обеспечивает выбор и запуск сервера или клиента."""
    while True:
        refresh_display()
        display_options()
        user_choice = input("Введите номер опции (1-3): ").strip()

        if user_choice == "1":
            print("Инициализация серверного компонента...")
            print("Сервер будет активен по адресу: 127.0.0.1:12345.")
            print("Для принудительной остановки используйте сочетание клавиш Ctrl+C.")
            input("Нажмите клавишу Enter для продолжения...")
            subprocess.run(["python3", "server.py"])  # Указываем python3 явно
        elif user_choice == "2":
            print("Активация клиентского компонента...")
            print("Подключение к серверу, размещенному на 127.0.0.1:12345.")
            input("Нажмите клавишу Enter для перехода к работе с клиентом...")
            subprocess.run(["python3", "client.py"])  # Указываем python3 явно
        elif user_choice == "3":
            print("Завершение сеанса...")
            break
        else:
            input("Введен некорректный символ. Нажмите Enter для повторной попытки...")

if __name__ == "__main__":
    execute_program()
