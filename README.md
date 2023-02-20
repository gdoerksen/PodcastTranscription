# PodcastTranscription
A podcast transcription utility using Whisper, WhisperX and Nvidia NeMo 

## External Requirements
* FFMPEG is required to use this repository 
* CUDA and PyTorch are required 

## Installation on WSL 2


CUDA is required, see: https://docs.nvidia.com/cuda/wsl-user-guide/index.html or https://developer.nvidia.com/cuda-11-7-1-download-archive?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0&target_type=deb_local

PyTorch is required, 

### Install Python 3.10 with pyenv 
See https://github.com/pyenv/pyenv

```
sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

```
env PYTHON_CONFIGURE_OPTS='--enable-optimizations --with-lto' PYTHON_CFLAGS='-march=native -mtune=native' pyenv install 3.10.10
```

### Install Python 3.10 from Source

1. Update package lists 
```
sudo apt update
```
2. Install dependancies 
```
sudo apt install build-essential checkinstall
sudo apt install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
```
3. Download the Python binary
```
wget https://www.python.org/ftp/python/3.10.10/Python-3.10.10.tgz
```
4. Unzip
```
tar -xzf Python-3.10.10.tgz
```
5. Configure python with optimizations (best for Development setups) 
```
cd Python-3.10.10/

./configure --enable-optimizations
```
6. Compile python with altinstall option to avoid replacing the feault python binary file in /usr/bin/python
```
sudo make altinstall
```
7. Check that installion
```
$ python3.10 -V

Python 3.10.X
```

