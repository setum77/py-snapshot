"""Main application"""
import os
import logging
from datetime import datetime, date
from pathlib import Path
from .config import load_computers, get_password_path, get_base_directory, get_time_interval
from .utils import check_port, create_snapshot

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    try:
        # Load configuration
        computers = load_computers()
        password_path = get_password_path()
        base_dir = Path(get_base_directory()) / 'jpg'
                
        # Создаем директорию если их нет
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        
        # Create timestamp
        today = date.today()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Process each computer
        for comp in computers:
            name = comp['name']
            ip = comp['ip']
            port = comp.get('port', 5900)
            
            logger.info(f'Обработка компьютера: {name} ({ip})')

            
            if check_port(ip, port):
                logger.info('   ++++ Успех. Порт 5900 открыт ++++')
                
                # Create directory structure
                date_dir = base_dir / str(today)
                user_dir = date_dir / name
                
                date_dir.mkdir(parents=True, exist_ok=True)
                user_dir.mkdir(exist_ok=True)
                
                # Create snapshot
                result = create_snapshot(comp, password_path, user_dir, timestamp)
                
                if result.returncode == 0:
                    logger.info(f"Snapshot created: {user_dir / f'{name}_{timestamp}.jpg'}")
                else:
                    logger.error(f"Error creating snapshot: {result.stderr}")
            else:
                logger.warning(f'---      {ip} не доступен      ---')
                
        logger.info("Завершение создания снимков")
    
    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}")
        raise



if __name__ == "__main__":
    # Настройка логирования для прямого запуска
    logging.basicConfig(level=logging.INFO)
    main()