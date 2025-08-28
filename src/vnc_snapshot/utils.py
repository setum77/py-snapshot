"""Utility functions"""
import socket
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict

def check_port(ip: str, port: int, timeout: int = 1) -> bool:
    """Check if port is open on IP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((str(ip), port))
            return result == 0
    except Exception:
        return False

def create_snapshot(comp_info: Dict, password_path: str, output_dir: Path, timestamp: str):
    """Create VNC snapshot"""
    ip = comp_info['ip']
    name = comp_info['name']
    
    snapshot_path = output_dir / f"{name}_{timestamp}.jpg"
    
    result = subprocess.run([
        'vncsnapshot', '-passwd', password_path, '-nocursor',
        '-compresslevel', '8', '-ignoreblank', '-quality', '55', '-quiet',
        f'{ip}:0', str(snapshot_path)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    
    return result