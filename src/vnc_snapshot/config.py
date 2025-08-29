"""Configuration management"""
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from typing import List, Dict

load_dotenv()

def load_computers() -> List[Dict]:
    """Load computer list from JSON file"""
    # Попробуем получить путь из переменной окружения
    config_path_env = os.getenv('COMPUTERS_CONFIG_PATH')
    
    if config_path_env:
        config_path = Path(config_path_env)
    else:
        # По умолчанию ищем в data директории проекта
        config_path = Path(__file__).parent.parent.parent / "data" / "computers.json"
    
    # Проверка существования файла
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Current working directory: {Path.cwd()}\n"
            f"Looking for file at: {config_path.absolute()}"
        )
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['computers']

def get_password_path() -> str:
    """Get VNC password file path"""
    
    return os.path.expanduser(os.getenv('VNC_PASSWD_PATH', '~/.vnc/passwd'))

def get_base_directory() -> Path:
    """Get base directory for snapshots"""
    return Path(os.path.expanduser('~/py-snapshot-result'))

def get_time_interval() -> int:
    """Get time interval scan"""

    return int(os.getenv('TIME_INTERVAL', 3))

def get_ftp_config():
    """Get FTP configuration from environment variables"""    
    
    return {
        'server': os.getenv('FTP_SERVER', None),
        'username': os.getenv('FTP_USERNAME', 'admin'),
        'password': os.getenv('FTP_PASSWORD', 'anonimous'),
        'remote_path': os.getenv('FTP_REMOTE_PATH', '/BackUp/snapshot/by_python/'),
        'days_to_keep': int(os.getenv('DAYS_TO_KEEP', 2))
    }