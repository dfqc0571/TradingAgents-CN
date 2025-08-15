#!/usr/bin/env python3
"""
TradingAgents-CN Web应用启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path
import signal
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

def check_dependencies():
    """检查必要的依赖是否已安装"""

    required_packages = ['streamlit', 'plotly', 'fastapi', 'uvicorn']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'streamlit':
                import streamlit
            elif package == 'plotly':
                import plotly
            elif package == 'fastapi':
                import fastapi
            elif package == 'uvicorn':
                import uvicorn
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"❌ 缺少必要的依赖包: {', '.join(missing_packages)}")
        logger.info(f"请运行以下命令安装:")
        logger.info(f"pip install {' '.join(missing_packages)}")
        return False

    logger.info(f"✅ 依赖包检查通过")
    return True

def clean_cache_files(force_clean=False):
    """
    清理Python缓存文件，避免Streamlit文件监控错误

    Args:
        force_clean: 是否强制清理，默认False（可选清理）
    """

    project_root = Path(__file__).parent.parent
    cache_patterns = ["**/__pycache__", "**/*.pyc", "**/*.pyo", "**/*~"]

    cleaned_count = 0
    for pattern in cache_patterns:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    cleaned_count += 1
                    if force_clean:
                        logger.debug(f"🧹 清理缓存文件: {file_path}")
                except Exception as e:
                    if force_clean:
                        logger.warning(f"⚠️ 无法清理文件 {file_path}: {e}")
            elif file_path.is_dir():
                try:
                    file_path.rmdir()
                    cleaned_count += 1
                    if force_clean:
                        logger.debug(f"🧹 清理缓存目录: {file_path}")
                except Exception as e:
                    if force_clean:
                        logger.warning(f"⚠️ 无法清理目录 {file_path}: {e}")

    if cleaned_count > 0:
        logger.info(f"🧹 总共清理了 {cleaned_count} 个缓存文件/目录")
    else:
        logger.info("✅ 无缓存文件需要清理")

def start_streamlit():
    """启动Streamlit应用"""
    logger.info("🚀 启动Streamlit应用...")
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(project_root / "web" / "app.py"),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--logger.level", "info"
    ]
    
    # 启动Streamlit
    process = subprocess.Popen(cmd)
    logger.info(f"📊 Streamlit应用已启动 (PID: {process.pid})")
    return process

def start_fastapi():
    """启动FastAPI服务"""
    logger.info("🚀 启动FastAPI服务...")
    
    # 构建命令
    cmd = [
        sys.executable, "-m", "uvicorn",
        "web.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    # 更改工作目录到项目根目录
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        # 启动FastAPI
        process = subprocess.Popen(cmd)
        logger.info(f"🔌 FastAPI服务已启动 (PID: {process.pid})")
        return process
    finally:
        # 恢复工作目录
        os.chdir(original_cwd)

def main():
    """主函数"""
    logger.info("🚀 启动TradingAgents-CN Web应用")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 清理缓存文件
    clean_cache_files()
    
    # 启动服务
    try:
        # 启动Streamlit和FastAPI
        streamlit_process = start_streamlit()
        fastapi_process = start_fastapi()
        
        logger.info("✅ 所有服务已启动:")
        logger.info("   📊 Web界面: http://localhost:8501")
        logger.info("   🔌 API接口: http://localhost:8000")
        logger.info("   📖 API文档: http://localhost:8000/api/docs")
        
        # 等待进程结束
        def signal_handler(sig, frame):
            logger.info("🛑 正在关闭服务...")
            streamlit_process.terminate()
            fastapi_process.terminate()
            streamlit_process.wait()
            fastapi_process.wait()
            logger.info("✅ 所有服务已关闭")
            sys.exit(0)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 等待进程
        while True:
            try:
                streamlit_process.wait(timeout=1)
                break
            except subprocess.TimeoutExpired:
                continue
                
    except KeyboardInterrupt:
        logger.info("🛑 用户中断，正在关闭服务...")
    except Exception as e:
        logger.error(f"❌ 启动服务时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
