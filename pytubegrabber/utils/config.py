"""
Módulo de configuração para o PyTubeGrabber.
Contém constantes e funções para controlar o comportamento do aplicativo.
"""

import os
import json
from typing import Dict, Any, List

# Diretório para armazenar arquivos de configuração
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".pytubegrabber")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Configurações padrão
DEFAULT_CONFIG = {
    "download_dir": os.path.join(os.path.expanduser("~"), "Downloads"),
    "preferred_format": "mp4",
    "preferred_quality": "best",
    "max_concurrent_downloads": 2,
    "show_terminal": False,
    "use_dark_theme": True,
    "history_limit": 100,
    "auto_check_updates": True,
    "language": "pt-BR"
}

# Formato para MP3
MP3_FORMAT = {
    'id': 'bestaudio/best',
    'ext': 'mp3',
    'description': 'Melhor qualidade (MP3)',
    'format_note': 'Audio',
}

# Formato para WAV
WAV_FORMAT = {
    'id': 'bestaudio/best',
    'ext': 'wav',
    'description': 'Alta fidelidade (WAV)',
    'format_note': 'Audio',
}

def ensure_config_dir() -> None:
    """
    Garante que o diretório de configuração existe.
    """
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_config() -> Dict[str, Any]:
    """
    Carrega as configurações do arquivo.
    
    Returns:
        Dicionário com as configurações
    """
    ensure_config_dir()
    
    # Se o arquivo de configuração não existir, criar com valores padrão
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Garantir que todas as chaves padrão estejam presentes
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                
        return config
    except Exception as e:
        print(f"Erro ao carregar configurações: {str(e)}")
        # Em caso de erro, retornar configurações padrão
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """
    Salva as configurações no arquivo.
    
    Args:
        config: Dicionário com configurações
    """
    ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configurações: {str(e)}")

def get_default_options() -> Dict[str, Any]:
    """
    Retorna as opções padrão para o yt-dlp.
    
    Returns:
        Dicionário de opções
    """
    return {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'windowsfilenames': True,
        'prefer_ffmpeg': True,
        'geo_bypass': True,
        'age_limit': 99,
        'nocheckcertificate': True
    }

def get_fallback_formats() -> List[Dict[str, Any]]:
    """
    Retorna formatos padrão para quando a API falha ao obter informações do vídeo.
    """
    formats = []
    
    # Adicionar formatos MP4
    for preset in MP4_QUALITY_PRESETS:
        formats.append({
            'id': preset['id'],
            'ext': 'mp4',
            'description': preset['description'],
            'format_note': 'Fallback',
            'format': None
        })
    
    # Adicionar formato MP3
    formats.append({
        'id': MP3_FORMAT['id'],
        'ext': 'mp3',
        'description': MP3_FORMAT['description'],
        'format_note': MP3_FORMAT['format_note'],
        'format': None
    })
    
    # Adicionar formato WAV
    formats.append({
        'id': WAV_FORMAT['id'],
        'ext': 'wav',
        'description': WAV_FORMAT['description'],
        'format_note': WAV_FORMAT['format_note'],
        'format': None
    })
    
    return formats

def get_download_dir() -> str:
    """
    Retorna o diretório de download configurado.
    
    Returns:
        Diretório de download
    """
    config = load_config()
    download_dir = config.get('download_dir', DEFAULT_CONFIG['download_dir'])
    
    # Garantir que o diretório existe
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
        except Exception:
            # Em caso de erro, usar o diretório padrão
            download_dir = DEFAULT_CONFIG['download_dir']
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
    
    return download_dir

def save_download_dir(directory: str) -> None:
    """
    Salva o diretório de download nas configurações.
    
    Args:
        directory: Caminho do diretório
    """
    config = load_config()
    config['download_dir'] = directory
    save_config(config)

def get_app_version() -> str:
    """
    Retorna a versão atual do aplicativo.
    
    Returns:
        String com versão do aplicativo
    """
    return "1.0.0" 