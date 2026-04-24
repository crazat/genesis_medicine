# 1. 권장 베이스 이미지 (Ubuntu 22.04 기반)
FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04

# 2. 기본 패키지 및 Python 3.11 설치
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. pip 최신화
RUN python3.11 -m pip install --upgrade pip

# 4. 작업 디렉터리
WORKDIR /workspace

# 5. requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["/bin/bash"]