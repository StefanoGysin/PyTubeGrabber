#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo principal para execução do PyTubeGrabber.
Este é o ponto de entrada principal do aplicativo quando executado como pacote.
"""

import sys
import os
import argparse

# Adicionar o diretório atual ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from pytubegrabber.gui.main_window import run_app
from pytubegrabber.utils.config import get_app_version
from pytubegrabber.core.downloader import VideoDownloader


def parse_arguments():
    """
    Analisa os argumentos de linha de comando.
    
    Returns:
        Argumentos analisados
    """
    parser = argparse.ArgumentParser(description='PyTubeGrabber - Download de vídeos do YouTube')
    parser.add_argument('--url', help='URL do vídeo para download')
    parser.add_argument('--dir', help='Diretório de saída para o download')
    parser.add_argument('--format', choices=['mp3', 'mp4'], default='mp4',
                       help='Formato de saída (mp3 ou mp4)')
    parser.add_argument('--quality', choices=['best', 'high', 'medium', 'low'], 
                       default='best', help='Qualidade do vídeo')
    parser.add_argument('--version', action='store_true', 
                       help='Exibe a versão do aplicativo')
    
    return parser.parse_args()


def process_command_line(args):
    """
    Processa os argumentos de linha de comando.
    
    Args:
        args: Argumentos analisados
        
    Returns:
        True se a execução deve continuar, False caso contrário
    """
    if args.version:
        print(f"PyTubeGrabber v{get_app_version()}")
        return False
    
    # Se uma URL foi fornecida, tenta baixar diretamente
    if args.url:
        try:
            output_dir = args.dir or os.path.expanduser("~/Downloads")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            downloader = VideoDownloader()
            
            # Mapear qualidade para formato
            quality_map = {
                'best': 'bestvideo+bestaudio/best',
                'high': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'medium': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                'low': 'bestvideo[height<=480]+bestaudio/best[height<=480]'
            }
            
            format_id = quality_map.get(args.quality, 'best')
            if args.format == 'mp3':
                format_id = 'bestaudio/best'
            
            # Fazer o download
            print(f"Baixando {args.url} em formato {args.format}...")
            output_file = downloader.download_video(
                args.url, output_dir, format_id, args.format
            )
            
            print(f"Download concluído: {output_file}")
            return False
            
        except Exception as e:
            print(f"Erro ao baixar vídeo: {str(e)}")
            return True
    
    return True


def main():
    """
    Função principal.
    """
    args = parse_arguments()
    
    # Processar argumentos de linha de comando
    if not process_command_line(args):
        return
    
    # Iniciar aplicação gráfica
    run_app()


if __name__ == "__main__":
    main() 