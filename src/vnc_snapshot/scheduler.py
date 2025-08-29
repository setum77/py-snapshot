"""Scheduler for VNC snapshots"""
import schedule
import time
import logging
import signal
import sys
from .main import main as run_snapshot
from .archiver import create_daily_archive
from .config import get_time_interval

# Настройка логирования
logging.basicConfig(
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vnc_snapshot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Флаг для остановки
should_stop = False

def signal_handler(signum, frame):
    """Обработчик сигналов завершения"""
    global should_stop
    logger.info(f"Получен сигнал завершения {signum}. Завершаю работу...")
    should_stop = True


def snapshot_job():
    """Задание для создания снимков"""
    if should_stop:
        return
        
    logger.info("Запуск VNC snapshot...")
    try:
        run_snapshot()
        logger.info("VNC snapshot завершен успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении VNC snapshot: {e}")

def archive_job():
    """Задание для создания архива"""
    if should_stop:
        return
        
    logger.info("Запуск создания архива...")
    try:
        success = create_daily_archive()
        if success:
            logger.info("Архив создан и загружен успешно")
        else:
            logger.error("Ошибка при создании архива")
    except Exception as e:
        logger.error(f"Ошибка при создании архива: {e}")

def main():
    """Основная функция планировщика"""
    global should_stop
    
    # интервал сканирования (минуты)
    time_interval = get_time_interval()
    
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # systemctl stop

    logger.info("Запуск планировщика VNC snapshot")
    
    # Запланировать создание снимков каждые 3 минуты
    schedule.every(time_interval).minutes.do(snapshot_job)
    
    # Запланировать создание архивов в 00:30 каждый день
    schedule.every().day.at("00:30:00").do(archive_job)
    
    # Отладка - покажем все запланированные задачи
    logger.info(f"Запланированные задачи: {len(schedule.jobs)} шт.")
    for job in schedule.jobs:
        logger.info(f"Задача: {job}")
    
    logger.info("Выполнение первого снимка...")
    snapshot_job()
    
    # Бесконечный цикл ожидания
    while not should_stop:
        schedule.run_pending()
        time.sleep(1)
   
    
    logger.info("Планировщик остановлен. До свидания!")
    sys.exit(0)

if __name__ == "__main__":
    main()