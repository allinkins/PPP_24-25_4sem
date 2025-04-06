import socket
import os
import datetime
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger("Client")


class Client:
    def __init__(self):
        self.host = Config.HOST
        self.port = Config.PORT

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        logger.info(f"Подключение к серверу {self.host}:{self.port}")

    def send_command(self, command: str):
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].upper()
        args = parts[1:]

        if cmd == "UPDATE":
            full_command = "UPDATE"
        elif cmd == "SIGNAL" and len(args) == 2:
            full_command = f"SIGNAL {args[0]} {args[1].upper()}"
        else:
            print("Неверная команда.")
            return

        try:
            self.sock.sendall(full_command.encode())
            logger.debug(f"Команда отправлена: {full_command}")

            if cmd == "UPDATE":
                self.receive_files()
            elif cmd == "SIGNAL":
                response = self.sock.recv(1024).decode()
                print(response)
        except Exception as e:
            logger.error(f"Ошибка при отправке команды: {e}")
            self.close()

    def receive_files(self):
        """
        Получает два файла от сервера: JSON и XML.
        """
        now = datetime.datetime.now()
        dir_name = now.strftime("%d-%m-%Y")  # Папка: дата
        filename_base = now.strftime("%H-%M-%S")  # Имя файла: только время
        os.makedirs(dir_name, exist_ok=True)

        for filetype in ("json", "xml"):
            # Получаем 4 байта с размером файла
            file_size_data = self.sock.recv(4)
            if not file_size_data:
                logger.error("Не удалось получить размер файла от сервера.")
                return
            file_size = int.from_bytes(file_size_data, byteorder='big')

            received_data = b""
            while len(received_data) < file_size:
                chunk = self.sock.recv(min(4096, file_size - len(received_data)))
                if not chunk:
                    break
                received_data += chunk

            file_path = os.path.join(dir_name, f"{filename_base}.{filetype}")
            with open(file_path, "wb") as f:
                f.write(received_data)
                logger.info(f"Файл {file_path} получен и сохранён.")

    def close(self):
        try:
            self.sock.close()
            logger.info("Соединение закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")
