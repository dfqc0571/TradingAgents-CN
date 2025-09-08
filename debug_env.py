import os
from dotenv import load_dotenv
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent
print(f"项目根目录: {project_root}")

# 尝试加载.env文件
env_path = project_root / ".env"
print(f".env文件路径: {env_path}")
print(f".env文件是否存在: {env_path.exists()}")

# 加载环境变量
load_dotenv(env_path, override=True)

# 检查API密钥
print("\n=== API密钥检查 ===")
google_api_key = os.getenv("GOOGLE_API_KEY")
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
finnhub_api_key = os.getenv("FINNHUB_API_KEY")

if google_api_key:
    print(f"✅ Google API密钥已配置: {google_api_key[:10]}...{google_api_key[-5:]}")
else:
    print("❌ Google API密钥未配置")

if dashscope_api_key:
    print(f"✅ 阿里百炼API密钥已配置: {dashscope_api_key[:10]}...{dashscope_api_key[-5:]}")
else:
    print("❌ 阿里百炼API密钥未配置")

if finnhub_api_key:
    print(f"✅ FinnHub API密钥已配置: {finnhub_api_key[:10]}...{finnhub_api_key[-5:]}")
else:
    print("❌ FinnHub API密钥未配置")