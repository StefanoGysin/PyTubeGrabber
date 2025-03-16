"""
Módulo main_window - Interface gráfica principal do PyTubeGrabber
"""

import os
import sys
import threading
import webbrowser
from typing import List, Dict, Any, Optional, Tuple, Union
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QComboBox, QProgressBar, 
    QMessageBox, QFileDialog, QStyle, QAction, QMenu, QSystemTrayIcon,
    QTabWidget, QListWidget, QListWidgetItem, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer, QObject
from PyQt5.QtGui import QIcon, QPixmap, QFont, QClipboard

# Importação dos módulos internos
from pytubegrabber.core.downloader import VideoDownloader
from pytubegrabber.utils.config import (
    get_download_dir, save_download_dir, load_config, 
    save_config, get_app_version
)

# Constantes
APP_NAME = "PyTubeGrabber"
APP_ICON = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600


class DownloadThread(QThread):
    """
    Thread para realizar download em segundo plano.
    """
    progress_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url: str, output_path: str, format_id: str, ext: str):
        """
        Inicializa a thread de download.
        
        Args:
            url: URL do vídeo
            output_path: Diretório de saída
            format_id: ID do formato selecionado
            ext: Extensão (mp3 ou mp4)
        """
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_id = format_id
        self.ext = ext
        self.downloader = VideoDownloader(self._progress_callback)
        
    def _progress_callback(self, progress_data: Dict[str, Any]) -> None:
        """Callback para atualizar o progresso."""
        self.progress_signal.emit(progress_data)
        
    def run(self) -> None:
        """Executa o download na thread."""
        try:
            output_file = self.downloader.download_video(
                self.url, self.output_path, self.format_id, self.ext
            )
            self.finished_signal.emit(output_file)
        except Exception as e:
            self.error_signal.emit(str(e))


class MainWindow(QMainWindow):
    """
    Janela principal do PyTubeGrabber.
    """
    
    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()
        
        # Configurar janela
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        
        # Tentar carregar o ícone
        try:
            self.setWindowIcon(QIcon(APP_ICON))
        except Exception:
            # Usar ícone padrão se não conseguir carregar
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        
        # Variáveis de estado
        self.download_thread = None
        self.current_formats = []
        self.current_video_info = {}
        self.is_downloading = False
        
        # Inicializar interface
        self._init_ui()
        
        # Aplicar tema (claro/escuro)
        self._apply_theme()
        
        # Carregar configurações
        self.config = load_config()
        
        # Definir diretório de download
        self.download_dir = get_download_dir()
        self.download_path_edit.setText(self.download_dir)
        
    def _init_ui(self) -> None:
        """Inicializa a interface do usuário."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title_label = QLabel(f"{APP_NAME} - v{get_app_version()}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Área de entrada de URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL do vídeo:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Cole aqui a URL do vídeo do YouTube...")
        self.url_edit.textChanged.connect(self._check_url)
        url_layout.addWidget(self.url_edit)
        
        # Botão para colar da área de transferência
        paste_button = QPushButton("Colar")
        paste_button.clicked.connect(self._paste_from_clipboard)
        url_layout.addWidget(paste_button)
        
        # Botão analisar URL
        self.fetch_button = QPushButton("Analisar URL")
        self.fetch_button.clicked.connect(self._fetch_video_info)
        url_layout.addWidget(self.fetch_button)
        main_layout.addLayout(url_layout)
        
        # Área de detalhes do vídeo
        self.video_details = QTextEdit()
        self.video_details.setReadOnly(True)
        self.video_details.setMaximumHeight(100)
        self.video_details.setPlaceholderText("Detalhes do vídeo aparecerão aqui...")
        main_layout.addWidget(self.video_details)
        
        # Área de seleção de formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        self.format_combo = QComboBox()
        self.format_combo.setEnabled(False)
        format_layout.addWidget(self.format_combo)
        main_layout.addLayout(format_layout)
        
        # Área de seleção de diretório
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Pasta de download:"))
        self.download_path_edit = QLineEdit()
        self.download_path_edit.setReadOnly(True)
        dir_layout.addWidget(self.download_path_edit)
        browse_button = QPushButton("Procurar...")
        browse_button.clicked.connect(self._browse_directory)
        dir_layout.addWidget(browse_button)
        main_layout.addLayout(dir_layout)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_status = QLabel("Aguardando download...")
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_status)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        # Botão download
        self.download_button = QPushButton("Download")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self._start_download)
        buttons_layout.addWidget(self.download_button)
        
        # Botão cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_download)
        buttons_layout.addWidget(self.cancel_button)
        
        # Botão limpar
        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(clear_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Status bar
        self.statusBar().showMessage("Pronto")
        
        # Menu
        self._create_menu()
        
    def _create_menu(self) -> None:
        """Cria o menu da aplicação."""
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")
        
        # Opção Abrir Local de Download
        open_dir_action = QAction("Abrir Local de Download", self)
        open_dir_action.triggered.connect(self._open_download_directory)
        file_menu.addAction(open_dir_action)
        
        # Separador
        file_menu.addSeparator()
        
        # Opção Sair
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Configurações
        settings_menu = menu_bar.addMenu("Configurações")
        
        # Tema
        theme_menu = QMenu("Tema", self)
        light_theme_action = QAction("Tema Claro", self)
        light_theme_action.triggered.connect(lambda: self._change_theme(False))
        dark_theme_action = QAction("Tema Escuro", self)
        dark_theme_action.triggered.connect(lambda: self._change_theme(True))
        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)
        settings_menu.addMenu(theme_menu)
        
        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")
        
        # Opção Sobre
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        # Opção Website
        website_action = QAction("Visitar Website", self)
        website_action.triggered.connect(lambda: webbrowser.open("https://github.com/pytubegrabber/pytubegrabber"))
        help_menu.addAction(website_action)
    
    def _apply_theme(self) -> None:
        """Aplica o tema (claro/escuro) à interface."""
        config = load_config()
        use_dark_theme = config.get("use_dark_theme", True)
        
        if use_dark_theme:
            self._set_dark_theme()
        else:
            self._set_light_theme()
    
    def _set_dark_theme(self) -> None:
        """Aplica o tema escuro."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D30;
                color: #F0F0F0;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1E1E1E;
                border: 1px solid #3F3F46;
                color: #F0F0F0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QProgressBar {
                border: 1px solid #3F3F46;
                background-color: #1E1E1E;
                color: white;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                width: 10px;
            }
            QMenuBar {
                background-color: #2D2D30;
                color: #F0F0F0;
            }
            QMenuBar::item:selected {
                background-color: #3E3E40;
            }
            QMenu {
                background-color: #2D2D30;
                color: #F0F0F0;
                border: 1px solid #3F3F46;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
            }
        """)
    
    def _set_light_theme(self) -> None:
        """Aplica o tema claro."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F5F5F5;
                color: #333333;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: white;
                border: 1px solid #C0C0C0;
                color: #333333;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
            QPushButton:disabled {
                background-color: #A0A0A0;
            }
            QProgressBar {
                border: 1px solid #C0C0C0;
                background-color: white;
                color: black;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                width: 10px;
            }
            QMenuBar {
                background-color: #F5F5F5;
                color: #333333;
            }
            QMenuBar::item:selected {
                background-color: #E0E0E0;
            }
            QMenu {
                background-color: white;
                color: #333333;
                border: 1px solid #C0C0C0;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
        """)
    
    def _change_theme(self, use_dark_theme: bool) -> None:
        """Muda o tema da aplicação.
        
        Args:
            use_dark_theme: Se deve usar o tema escuro
        """
        config = load_config()
        config["use_dark_theme"] = use_dark_theme
        save_config(config)
        
        if use_dark_theme:
            self._set_dark_theme()
        else:
            self._set_light_theme()
        
        QMessageBox.information(self, "Tema Atualizado", 
                               "O tema foi atualizado com sucesso.")
    
    def _paste_from_clipboard(self) -> None:
        """Cola texto da área de transferência no campo de URL."""
        clipboard = QApplication.clipboard()
        self.url_edit.setText(clipboard.text())
    
    def _check_url(self) -> None:
        """Verifica se a URL é válida."""
        url = self.url_edit.text().strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            self.fetch_button.setEnabled(True)
        else:
            self.fetch_button.setEnabled(False)
            self.download_button.setEnabled(False)
            self.format_combo.setEnabled(False)
    
    def _fetch_video_info(self) -> None:
        """Obtém informações do vídeo e os formatos disponíveis."""
        url = self.url_edit.text().strip()
        
        if not url:
            return
        
        self.statusBar().showMessage("Obtendo informações do vídeo...")
        self.fetch_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.format_combo.clear()
        self.video_details.clear()
        
        try:
            # Criar thread para não bloquear a interface
            self.thread = QThread()
            self.worker = VideoInfoWorker(url)
            self.worker.moveToThread(self.thread)
            
            # Conectar sinais
            self.thread.started.connect(self.worker.get_info)
            self.worker.formats_ready.connect(self._update_formats)
            self.worker.error.connect(self._show_error)
            self.worker.finished.connect(self.thread.quit)
            
            # Iniciar thread
            self.thread.start()
            
        except Exception as e:
            self._show_error(f"Erro ao obter informações: {str(e)}")
            self.fetch_button.setEnabled(True)
    
    def _update_formats(self, formats: List[Dict[str, Any]], info: Dict[str, Any]) -> None:
        """Atualiza a interface com os formatos disponíveis.
        
        Args:
            formats: Lista de formatos disponíveis
            info: Informações do vídeo
        """
        self.current_formats = formats
        self.current_video_info = info
        
        # Limpar e preencher combo
        self.format_combo.clear()
        for fmt in formats:
            self.format_combo.addItem(fmt['description'], fmt['id'])
        
        # Atualizar detalhes do vídeo
        title = info.get('title', 'Título desconhecido')
        uploader = info.get('uploader', 'Desconhecido')
        duration = info.get('duration', 0)
        
        # Formatando duração
        if duration:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
        else:
            duration_str = "Desconhecido"
        
        details = f"Título: {title}\nCanal: {uploader}\nDuração: {duration_str}"
        self.video_details.setText(details)
        
        # Habilitar controles
        self.format_combo.setEnabled(True)
        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)
        
        self.statusBar().showMessage("Informações do vídeo obtidas com sucesso")
    
    def _browse_directory(self) -> None:
        """Abre diálogo para selecionar diretório de download."""
        directory = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Download", 
            self.download_path_edit.text()
        )
        
        if directory:
            self.download_dir = directory
            self.download_path_edit.setText(directory)
            save_download_dir(directory)
    
    def _start_download(self) -> None:
        """Inicia o processo de download."""
        if self.is_downloading:
            return
        
        url = self.url_edit.text().strip()
        selected_format_idx = self.format_combo.currentIndex()
        
        if selected_format_idx < 0 or selected_format_idx >= len(self.current_formats):
            self._show_error("Selecione um formato válido")
            return
        
        selected_format = self.current_formats[selected_format_idx]
        format_id = selected_format['id']
        ext = selected_format['ext']
        
        # Configurar interface para download
        self.progress_bar.setValue(0)
        self.is_downloading = True
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.format_combo.setEnabled(False)
        self.fetch_button.setEnabled(False)
        self.statusBar().showMessage("Iniciando download...")
        
        # Criar e iniciar thread de download
        self.download_thread = DownloadThread(
            url, self.download_dir, format_id, ext
        )
        self.download_thread.progress_signal.connect(self._update_progress)
        self.download_thread.finished_signal.connect(self._download_finished)
        self.download_thread.error_signal.connect(self._download_error)
        self.download_thread.start()
    
    def _update_progress(self, progress_data: Dict[str, Any]) -> None:
        """Atualiza a barra de progresso.
        
        Args:
            progress_data: Dados de progresso do download
        """
        status = progress_data.get('status', '')
        
        if status == 'downloading':
            try:
                total = progress_data.get('total_bytes', 0)
                downloaded = progress_data.get('downloaded_bytes', 0)
                
                if total > 0:
                    percent = int((downloaded / total) * 100)
                    self.progress_bar.setValue(percent)
                    
                    # Calcular velocidade
                    speed = progress_data.get('speed', 0)
                    if speed:
                        speed_str = self._format_size(speed) + "/s"
                    else:
                        speed_str = "-- KB/s"
                    
                    # Calcular ETA
                    eta = progress_data.get('eta', 0)
                    if eta:
                        eta_str = self._format_time(eta)
                    else:
                        eta_str = "--:--"
                    
                    # Atualizar status
                    status_text = f"Baixando: {percent}% | Velocidade: {speed_str} | Tempo restante: {eta_str}"
                    self.progress_status.setText(status_text)
                    self.statusBar().showMessage(f"Baixando... {percent}%")
            except Exception as e:
                self.progress_status.setText(f"Baixando... {str(e)}")
        
        elif status == 'finished':
            self.progress_status.setText("Processando arquivo...")
            self.statusBar().showMessage("Finalizando download...")
    
    def _download_finished(self, output_file: str) -> None:
        """Callback quando o download é finalizado.
        
        Args:
            output_file: Caminho do arquivo baixado
        """
        self.is_downloading = False
        self.progress_bar.setValue(100)
        self.cancel_button.setEnabled(False)
        self.download_button.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.fetch_button.setEnabled(True)
        
        self.progress_status.setText(f"Download concluído: {os.path.basename(output_file)}")
        self.statusBar().showMessage("Download concluído com sucesso!")
        
        # Perguntar se quer abrir o arquivo
        reply = QMessageBox.question(
            self, "Download Concluído", 
            f"Download concluído com sucesso!\nDeseja abrir o arquivo?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Abrir arquivo com aplicativo padrão
                if sys.platform == 'win32':
                    os.startfile(output_file)
                elif sys.platform == 'darwin':
                    os.system(f'open "{output_file}"')
                else:
                    os.system(f'xdg-open "{output_file}"')
            except Exception as e:
                QMessageBox.warning(
                    self, "Erro", f"Não foi possível abrir o arquivo: {str(e)}"
                )
    
    def _download_error(self, error_msg: str) -> None:
        """Callback quando ocorre erro no download.
        
        Args:
            error_msg: Mensagem de erro
        """
        self.is_downloading = False
        self.progress_bar.setValue(0)
        self.cancel_button.setEnabled(False)
        self.download_button.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.fetch_button.setEnabled(True)
        
        self.progress_status.setText("Erro no download")
        self.statusBar().showMessage("Erro no download")
        
        QMessageBox.critical(self, "Erro no Download", f"Ocorreu um erro:\n{error_msg}")
    
    def _cancel_download(self) -> None:
        """Cancela o download em andamento."""
        if self.download_thread and self.is_downloading:
            # Terminar thread
            self.download_thread.terminate()
            self.download_thread.wait()
            
            # Atualizar interface
            self.is_downloading = False
            self.progress_bar.setValue(0)
            self.progress_status.setText("Download cancelado")
            self.statusBar().showMessage("Download cancelado pelo usuário")
            
            self.cancel_button.setEnabled(False)
            self.download_button.setEnabled(True)
            self.format_combo.setEnabled(True)
            self.fetch_button.setEnabled(True)
    
    def _clear_form(self) -> None:
        """Limpa o formulário e reseta o estado."""
        self.url_edit.clear()
        self.format_combo.clear()
        self.video_details.clear()
        self.progress_bar.setValue(0)
        self.progress_status.setText("Aguardando download...")
        
        self.format_combo.setEnabled(False)
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.fetch_button.setEnabled(False)
        
        self.current_formats = []
        self.current_video_info = {}
        self.is_downloading = False
        
        self.statusBar().showMessage("Pronto")
    
    def _open_download_directory(self) -> None:
        """Abre o diretório de download."""
        try:
            if sys.platform == 'win32':
                os.startfile(self.download_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.download_dir}"')
            else:
                os.system(f'xdg-open "{self.download_dir}"')
        except Exception as e:
            QMessageBox.warning(
                self, "Erro", f"Não foi possível abrir o diretório: {str(e)}"
            )
    
    def _show_about(self) -> None:
        """Exibe diálogo 'Sobre'."""
        QMessageBox.about(
            self, f"Sobre {APP_NAME}",
            f"""<h1>{APP_NAME} v{get_app_version()}</h1>
            <p>Aplicativo para download de vídeos do YouTube em formatos MP3 e MP4.</p>
            <p>Desenvolvido com Python e PyQt5.</p>
            <p>Licença: MIT</p>
            <p><a href="https://github.com/pytubegrabber/pytubegrabber">GitHub</a></p>"""
        )
    
    def _show_error(self, message: str) -> None:
        """Exibe mensagem de erro.
        
        Args:
            message: Mensagem de erro
        """
        QMessageBox.critical(self, "Erro", message)
        self.statusBar().showMessage("Erro: " + message)
        
        # Reabilitar controles
        self.fetch_button.setEnabled(True)
    
    def _format_size(self, size_bytes: float) -> str:
        """Formata tamanho em bytes para formato legível.
        
        Args:
            size_bytes: Tamanho em bytes
            
        Returns:
            String formatada
        """
        if size_bytes < 1024:
            return f"{size_bytes:.2f} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.2f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"
    
    def _format_time(self, seconds: int) -> str:
        """Formata tempo em segundos para formato legível.
        
        Args:
            seconds: Tempo em segundos
            
        Returns:
            String formatada
        """
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class VideoInfoWorker(QObject):
    """
    Worker para obter informações do vídeo em thread separada.
    """
    formats_ready = pyqtSignal(list, dict)
    error = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, url: str):
        """
        Inicializa o worker.
        
        Args:
            url: URL do vídeo
        """
        super().__init__()
        self.url = url
        self.downloader = VideoDownloader()
    
    def get_info(self) -> None:
        """Obtém informações do vídeo."""
        try:
            formats, info = self.downloader.get_available_formats(self.url)
            self.formats_ready.emit(formats, info)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


def run_app() -> None:
    """
    Função principal para iniciar o aplicativo.
    """
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Criar e exibir janela principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_()) 