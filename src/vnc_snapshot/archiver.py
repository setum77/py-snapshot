"""Module for archiving and uploading snapshots"""
import os
from pathlib import Path
from ftplib import FTP
from datetime import datetime, date, timedelta
import shutil
import logging
from typing import Optional
from .config import get_ftp_config

logger = logging.getLogger(__name__)


def upload_file_ftp(server: str, username: str, password: str, 
                   remote_path: str, local_file_path: str, remote_file_name: str) -> bool:
    """Upload file to FTP server"""
    try:
        # Подключаемся к FTP-серверу
        ftp = FTP(server)
        ftp.login(user=username, passwd=password)
        logger.info(f"Подключено к {server}")
        
        # Переходим в нужную директорию
        ftp.cwd(remote_path)
        
        # Открываем локальный файл в бинарном режиме для чтения
        with open(local_file_path, 'rb') as file:
            # Загружаем файл на сервер под именем remote_file_name
            ftp.storbinary(f'STOR {remote_file_name}', file)
            logger.info(f"Файл {local_file_path} успешно загружен как {remote_file_name}")

        # Закрываем соединение
        ftp.quit()
        logger.info("Соединение закрыто")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла на FTP: {e}")
        return False

def delete_old_files_and_dirs(path: str, days: int = 2) -> None:
    """Delete files and empty directories older than specified days"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        p = Path(path)

        if not p.exists():
            logger.warning(f"Путь не существует: {path}")
            return

        for item in p.rglob('*'):  # рекурсивно все файлы и папки
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)  # время последней модификации
                if mtime < cutoff:
                    if item.is_file():
                        item.unlink()
                        logger.info(f"Удалён файл: {item}")
                    elif item.is_dir():
                        # Удаляем папку только если она пустая (после удаления файлов)
                        try:
                            item.rmdir()
                            logger.info(f"Удалена папка: {item}")
                        except OSError:
                            # Папка не пуста, пропускаем
                            pass
            except Exception as e:
                logger.error(f"Ошибка при обработке {item}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при очистке директории {path}: {e}")

def create_daily_archive() -> bool:
    """Create daily archive of yesterday's snapshots"""
    try:
        # Получаем конфигурацию
        config = get_ftp_config()
        
        backup_dir = os.path.expanduser('~/py_zip_snpsht/')
        source_dir = os.path.expanduser('~/py_snapshot/')
        ftp_server = config['server']
        ftp_username = config['username']
        ftp_password = config['password']
        ftp_dir = config['remote_path']
        days_to_keep = config['days_to_keep']
        
        logger.info(f"Конфигурация FTP: сервер={ftp_server}, пользователь={ftp_username}, путь={ftp_dir}")
        logger.info(f"Количество дней хранения: {days_to_keep}")
        
        # Создаем директории если их нет
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        yesterday = date.today() - timedelta(days=1)
        yesterday_dir = os.path.join(source_dir, str(yesterday))
        
        if not os.path.exists(yesterday_dir):
            logger.warning(f"Директория за вчера не найдена: {yesterday_dir}")
            return False
            
        backup_file = f'py_snapshot_{str(yesterday)}.zip'
        backup_path = os.path.join(backup_dir, backup_file)
        
        logger.info(f"Создание архива: {backup_path}")
        
        # Создание резервной копии
        shutil.make_archive(backup_path.replace('.zip', ''), 'zip', yesterday_dir)
        logger.info(f"Архив создан: {backup_path}")
        
        # Отправляем по ФТП
        logger.info("Начало загрузки архива на FTP...")
        success = upload_file_ftp(ftp_server, ftp_username, ftp_password, ftp_dir, backup_path, backup_file)
        
        if success:
            logger.info("Архив успешно загружен на FTP")
        else:
            logger.error("Ошибка при загрузке архива на FTP")
            
        # Удаляем скриншоты старше указанного количества дней из основной папки
        logger.info(f"Очистка старых файлов (старше {days_to_keep} дней)...")
        delete_old_files_and_dirs(source_dir, days_to_keep)
        
        # Удаляем архивы старше указанного количества дней
        delete_old_files_and_dirs(backup_dir, days_to_keep)
        
        return success
        
    except Exception as e:
        logger.error(f"Ошибка при создании архива: {e}")
        return False

def main():
    """Main function for manual archive creation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    success = create_daily_archive()
    if success:
        logger.info("Архивация завершена успешно")
    else:
        logger.error("Архивация завершена с ошибками")

if __name__ == "__main__":
    main()