import os
import yt_dlp
from typing import Callable, Dict, List, Any, Optional, Tuple

# Importar módulo de configuração
from pytubegrabber.utils.config import get_default_options, get_fallback_formats


class VideoDownloader:
    """
    Classe responsável pelo download de vídeos do YouTube em formato MP3 ou MP4.
    """
    
    def __init__(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Inicializa o downloader.
        
        Args:
            progress_callback: Função callback para atualizar o progresso do download
        """
        self.progress_callback = progress_callback
        
    def _get_progress_hook(self) -> Callable:
        """
        Cria um hook de progresso para monitorar o download.
        
        Returns:
            Função hook para monitorar o progresso
        """
        def progress_hook(d: Dict[str, Any]) -> None:
            if self.progress_callback:
                self.progress_callback(d)
        
        return progress_hook
    
    def _get_ydl_opts(self, skip_download: bool = False) -> Dict[str, Any]:
        """
        Retorna as opções básicas para o yt-dlp.
        
        Args:
            skip_download: Se deve pular o download
            
        Returns:
            Dicionário com opções
        """
        # Usar as configurações padrão do módulo de configuração
        options = get_default_options().copy()
        
        # Adicionar/modificar opções específicas
        options.update({
            'skip_download': skip_download,
        })
        
        return options
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Obtém informações sobre o vídeo.
        
        Args:
            url: URL do vídeo
            
        Returns:
            Dicionário com informações do vídeo
            
        Raises:
            Exception: Se ocorrer erro ao obter informações
        """
        ydl_opts = self._get_ydl_opts(skip_download=True)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise Exception("Não foi possível obter informações do vídeo")
                return info
        except Exception as e:
            raise Exception(f"Erro ao obter informações do vídeo: {str(e)}")
    
    def get_available_formats(self, url: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Obtém os formatos disponíveis para o vídeo.
        
        Args:
            url: URL do vídeo
            
        Returns:
            Tupla com lista de formatos disponíveis e informações do vídeo
            
        Raises:
            Exception: Se ocorrer erro ao obter formatos
        """
        try:
            # Tentar obter informações do vídeo
            try:
                info = self.get_video_info(url)
                video_formats = [f for f in info.get('formats', []) 
                             if f.get('ext') == 'mp4' and f.get('height') is not None and f.get('acodec') != 'none']
                
                # Se conseguiu obter formatos, processá-los
                if video_formats:
                    formats = []
                    
                    # Ordenar por qualidade (altura) de forma decrescente
                    video_formats.sort(key=lambda x: (x.get('height', 0) or 0), reverse=True)
                    
                    # Adicionar apenas 5 opções de qualidade para não sobrecarregar
                    added_resolutions = set()
                    for fmt in video_formats:
                        height = fmt.get('height')
                        if height and len(formats) < 5:
                            resolution_key = str(height)
                            if resolution_key not in added_resolutions:
                                formats.append({
                                    'id': fmt['format_id'],
                                    'ext': 'mp4',
                                    'description': f"{height}p (MP4)",
                                    'format_note': fmt.get('format_note', ''),
                                    'format': fmt
                                })
                                added_resolutions.add(resolution_key)
                    
                    # Adicionar formato de áudio (MP3)
                    formats.append({
                        'id': 'bestaudio/best',
                        'ext': 'mp3',
                        'description': "Melhor qualidade (MP3)",
                        'format_note': 'Audio',
                        'format': None
                    })
                    
                    # Adicionar formato de áudio (WAV)
                    formats.append({
                        'id': 'bestaudio/best',
                        'ext': 'wav',
                        'description': "Alta fidelidade (WAV)",
                        'format_note': 'Audio',
                        'format': None
                    })
                    
                    return formats, info
                
                # Se não conseguiu formatos específicos, usar os padrões
                print("Usando formatos padrão porque não foi possível obter formatos específicos")
                formats = get_fallback_formats()
                return formats, info
                
            except Exception as e:
                print(f"Erro ao obter formatos específicos: {e}")
                print("Usando formatos padrão devido a erro")
                # Em caso de erro, usar formatos padrão
                formats = get_fallback_formats()
                
                # Tentar novamente apenas para obter informações básicas
                try:
                    info = self.get_video_info(url)
                except Exception:
                    # Se falhar novamente, criar um objeto info vazio
                    info = {'id': url, 'title': 'Vídeo do YouTube', 'uploader': 'Desconhecido'}
                
                return formats, info
                
        except Exception as e:
            raise Exception(f"Erro ao obter formatos disponíveis: {str(e)}")
    
    def download_video(self, url: str, output_path: str, format_id: str, 
                      ext: str = 'mp4', filename: Optional[str] = None) -> str:
        """
        Realiza o download do vídeo.
        
        Args:
            url: URL do vídeo
            output_path: Caminho para salvar o arquivo
            format_id: ID do formato selecionado
            ext: Extensão do arquivo (mp4 ou mp3)
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo baixado
            
        Raises:
            Exception: Se ocorrer erro durante o download
        """
        try:
            # Tentar obter informações do vídeo para o título
            try:
                info = self.get_video_info(url)
                video_title = info.get('title', 'video')
            except Exception:
                # Se não conseguir obter o título, usar um padrão
                video_title = f"youtube_video_{url.split('v=')[-1] if 'v=' in url else 'download'}"
            
            # Remover caracteres inválidos para nome de arquivo
            safe_title = "".join([c for c in video_title if c.isalnum() or c in ' -_.,()[]{}'])
            safe_title = safe_title.strip()
            
            if not filename:
                filename = f"{safe_title}.{ext}"
            
            output_file = os.path.join(output_path, filename)
            
            # Obter opções base do yt-dlp
            ydl_opts = self._get_ydl_opts(skip_download=False)
            
            # Adicionar opções específicas para o download
            ydl_opts.update({
                'format': format_id,
                'outtmpl': output_file,
                'progress_hooks': [self._get_progress_hook()],
                'noplaylist': True,
            })
            
            # Opções específicas para MP3
            if ext == 'mp3':
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'format': 'bestaudio/best',
                })
            
            # Opções específicas para WAV
            elif ext == 'wav':
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': 'best',  # WAV não tem compressão, então usamos a melhor qualidade
                    }],
                    'format': 'bestaudio/best',
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                error_code = ydl.download([url])
                if error_code != 0:
                    raise Exception(f"Erro ao baixar vídeo (código {error_code})")
            
            # Verificar se o arquivo foi criado
            if not os.path.exists(output_file):
                # Verificar se existe arquivo com extensão diferente (caso tenha sido processado)
                base_output = os.path.splitext(output_file)[0]
                potential_files = [
                    f for f in os.listdir(output_path) 
                    if f.startswith(os.path.basename(base_output))
                ]
                
                if potential_files:
                    # Retornar o primeiro arquivo encontrado
                    return os.path.join(output_path, potential_files[0])
                else:
                    raise Exception("Arquivo não foi criado após o download")
            
            return output_file
            
        except Exception as e:
            raise Exception(f"Erro ao baixar vídeo: {str(e)}")
    
    def download_multiple(self, urls: List[str], output_path: str, 
                         format_id: str, ext: str = 'mp4') -> List[str]:
        """
        Realiza download de múltiplos vídeos.
        
        Args:
            urls: Lista de URLs
            output_path: Caminho para salvar os arquivos
            format_id: ID do formato selecionado
            ext: Extensão do arquivo (mp4 ou mp3)
            
        Returns:
            Lista com caminhos dos arquivos baixados
            
        Raises:
            Exception: Se ocorrer erro durante o download
        """
        downloaded_files = []
        errors = []
        
        for url in urls:
            try:
                file_path = self.download_video(url, output_path, format_id, ext)
                downloaded_files.append(file_path)
            except Exception as e:
                errors.append(f"Erro ao baixar {url}: {str(e)}")
        
        if errors:
            error_msg = "\n".join(errors)
            raise Exception(f"Erros durante o download em lote:\n{error_msg}")
            
        return downloaded_files 