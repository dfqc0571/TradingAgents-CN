# 使用官方Python镜像替代GitHub Container Registry
FROM python:3.10-slim-bookworm

# 安装uv包管理器
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

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

# 升级pip
RUN pip install --no-cache-dir pip -U

# 使用多源轮询方式安装依赖，解决依赖冲突问题
# 先尝试宽松的安装方式，不指定版本
RUN set -e; \
    for src in \
    https://docker.xuanyuan.me \
    https://dockerproxy.net \
    https://docker.m.daocloud.io \
    https://mirror.ccs.tencentyun.com \
    https://pypi.tuna.tsinghua.edu.cn/simple \
    https://mirrors.aliyun.com/pypi/simple \
    https://pypi.doubanio.com/simple \
    https://pypi.org/simple; do \
    echo "Try installing from $src"; \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt -i $src && break || \
    pip install --no-cache-dir --use-deprecated=legacy-resolver --no-deps -r requirements.txt -i $src && break || \
    echo "Failed to install with $src, trying next source..."; \
    done

# 如果上面的安装方式都失败，则尝试逐个安装依赖
RUN echo "If batch installation failed, installing packages individually..." && \
    pip install --no-cache-dir streamlit plotly pandas numpy requests python-dotenv pyyaml pydantic && \
    echo "Installing data sources..." && \
    pip install --no-cache-dir tushare akshare yfinance finnhub-python baostock && \
    echo "Installing AI related packages..." && \
    pip install --no-cache-dir openai dashscope langchain langchain-openai langchain-google-genai langchain-anthropic langgraph && \
    echo "Installing database packages..." && \
    pip install --no-cache-dir chromadb pymongo redis && \
    echo "Installing web packages..." && \
    pip install --no-cache-dir beautifulsoup4 lxml fake-useragent pytesseract pillow psutil stockstats && \
    echo "Installing utility packages..." && \
    pip install --no-cache-dir python-dateutil pytz tzdata urllib3 certifi charset-normalizer idna six click && \
    echo "Installing other packages..." && \
    pip install --no-cache-dir altair blinker cachetools gitdb gitpython jsonschema markdown-it-py mdurl && \
    pip install --no-cache-dir packaging protobuf pyarrow pydeck rich smmap tenacity toml tornado typing-extensions watchdog && \
    pip install --no-cache-dir fastapi uvicorn google-generativeai google-genai

# 显式安装关键依赖包以确保正确安装
RUN pip install --no-cache-dir plotly fastapi uvicorn streamlit python-dotenv

# 复制日志配置文件
COPY config/ ./config/

COPY . .

EXPOSE 8501
EXPOSE 8000

CMD ["python", "web/run_web.py"]