#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de instalação do PyTubeGrabber.
"""

import os
import re
from setuptools import setup, find_packages

# Caminho do diretório atual
here = os.path.abspath(os.path.dirname(__file__))

# Obter a versão do pacote
def get_version():
    """
    Extrai a versão do pacote do arquivo __init__.py
    """
    init_py = open(os.path.join(here, 'pytubegrabber', '__init__.py')).read()
    return re.search(r"__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

# Ler o conteúdo do README.md
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Requisitos do pacote
requirements = [
    'PyQt5>=5.15.0',
    'yt-dlp>=2023.3.4',
    'Pillow>=10.0.0',
]

# Configuração do setup
setup(
    name='pytubegrabber',
    version=get_version(),
    description='Aplicativo para download de vídeos do YouTube em MP3 e MP4',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Stefano Gysin',
    author_email='pytubegrabber@example.com',
    url='https://github.com/StefanoGysin/PyTubeGrabber',
    packages=find_packages(include=['pytubegrabber', 'pytubegrabber.*']),
    entry_points={
        'console_scripts': [
            'pytubegrabber=pytubegrabber.__main__:main',
        ],
        'gui_scripts': [
            'pytubegrabber-gui=pytubegrabber.__main__:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.6',
    keywords='youtube, download, mp3, mp4, vídeo, áudio',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
    ],
)