# 使用官方Python镜像替代GitHub Container Registry
FROM python:3.10-slim-bookworm

# 安装uv包管理器
RUN pip install -i https://docker.1ms.run https://dytt.online https://lispy.org https://docker.xiaogenban1993.com https://hub.rat.dev https://docker.m.daocloud.io https://mirror.ccs.tencentyun.com

WORKDIR /app

RUN mkdir -p /app/data /app/logs

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN echo 'deb http://mirrors.aliyun.com/debian/ bookworm main' > /etc/apt/sources.list && \
    echo 'deb-src http://mirrors.aliyun.com/debian/ bookworm main' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian/ bookworm-updates main' >> /etc/apt/sources.list && \
    echo 'deb-src http://mirrors.aliyun.com/debian/ bookworm-updates main' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.aliyun.com/debian-security bookworm-security main' >> /etc/apt/sources.list && \
    echo 'deb-src http://mirrors.aliyun.com/debian-security bookworm-security main' >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wkhtmltopdf \
    xvfb \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-liberation \
    pandoc \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 启动Xvfb虚拟显示器
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 -ac +extension GLX +extension RANDR &\nexport DISPLAY=:99\nexec "$@"' > /usr/local/bin/start-xvfb.sh \
    && chmod +x /usr/local/bin/start-xvfb.sh

COPY requirements.txt .

#多源轮询安装依赖
RUN set -e; \
    for src in \
        https://docker.1ms.run \
        https://dytt.online \
        https://lispy.org \
        https://docker.xiaogenban1993.com \
        https://hub.rat.dev \
        https://docker.m.daocloud.io \
        https://mirror.ccs.tencentyun.com; do \
      echo "Try installing from $src"; \
      pip install --no-cache-dir -r requirements.txt -i $src && break; \
      echo "Failed at $src, try next"; \
    done

# 复制日志配置文件
COPY config/ ./config/

COPY . .

EXPOSE 8501
EXPOSE 8000

CMD ["python", "web/run_web.py"]