import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
project_root = Path(__file__).parent
load_dotenv(project_root / ".env", override=True)

def check_proxy_settings():
    """检查代理设置"""
    print("🔍 检查代理设置")
    print("=" * 50)
    
    http_proxy = os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("HTTPS_PROXY")
    all_proxy = os.getenv("ALL_PROXY")
    
    if http_proxy:
        print(f"✅ HTTP_PROXY: {http_proxy}")
    else:
        print("⚠️ HTTP_PROXY 未设置")
        
    if https_proxy:
        print(f"✅ HTTPS_PROXY: {https_proxy}")
    else:
        print("⚠️ HTTPS_PROXY 未设置")
        
    if all_proxy:
        print(f"✅ ALL_PROXY: {all_proxy}")
    else:
        print("⚠️ ALL_PROXY 未设置")
        
    # 检查小写的代理设置
    http_proxy_lower = os.getenv("http_proxy")
    https_proxy_lower = os.getenv("https_proxy")
    all_proxy_lower = os.getenv("all_proxy")
    
    if http_proxy_lower and not http_proxy:
        print(f"ℹ️ http_proxy (小写): {http_proxy_lower}")
    if https_proxy_lower and not https_proxy:
        print(f"ℹ️ https_proxy (小写): {https_proxy_lower}")
    if all_proxy_lower and not all_proxy:
        print(f"ℹ️ all_proxy (小写): {all_proxy_lower}")

def test_google_ai_with_proxy():
    """测试Google AI连通性（使用代理）"""
    print("\n🧪 测试Google AI连通性（使用代理）")
    print("=" * 50)
    
    # 检查API密钥
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ Google API密钥未配置")
        return False
    
    print(f"✅ Google API密钥已配置: {google_api_key[:10]}...")
    
    # 尝试导入必要的库
    try:
        import google.generativeai as genai
        print("✅ google-generativeai库导入成功")
    except ImportError as e:
        print(f"❌ google-generativeai库导入失败: {e}")
        return False
    
    # 配置Google AI
    try:
        genai.configure(api_key=google_api_key)
        print("✅ Google AI配置成功")
    except Exception as e:
        print(f"❌ Google AI配置失败: {e}")
        return False
    
    # 测试具体模型
    test_models = [
        "gemini-2.0-flash",  # 推荐使用的稳定模型
        "gemini-2.5-flash", 
        "gemini-1.5-pro"
    ]
    
    for model_name in test_models:
        try:
            print(f"\n🔍 测试模型: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # 生成内容测试
            response = model.generate_content(
                "请用中文简单介绍一下自己",
                generation_config=genai.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.1
                )
            )
            
            if response and response.text:
                print(f"✅ {model_name} 调用成功")
                print(f"   响应长度: {len(response.text)} 字符")
                print(f"   响应预览: {response.text[:100]}...")
                return True
            else:
                print(f"❌ {model_name} 调用失败：无响应内容")
                
        except Exception as e:
            print(f"❌ {model_name} 调用失败: {e}")
            # 不返回False，继续测试其他模型
    
    return False

def test_network_connectivity():
    """测试网络连通性"""
    print("\n🌐 测试网络连通性")
    print("=" * 50)
    
    import urllib.request
    import urllib.error
    import socket
    
    # 测试Google域名连通性
    test_urls = [
        "https://generativelanguage.googleapis.com",
        "https://ai.google.dev"
    ]
    
    for url in test_urls:
        try:
            print(f"🔍 测试连接: {url}")
            urllib.request.urlopen(url, timeout=10)
            print(f"✅ 可以访问 {url}")
        except urllib.error.URLError as e:
            print(f"❌ 无法访问 {url}: {e}")
        except socket.timeout:
            print(f"❌ 连接 {url} 超时")

if __name__ == "__main__":
    print("开始测试代理设置和Google AI连通性...")
    
    # 检查代理设置
    check_proxy_settings()
    
    # 测试网络连通性
    test_network_connectivity()
    
    # 测试Google AI
    success = test_google_ai_with_proxy()
    
    if success:
        print("\n🎉 Google AI测试成功！")
        print("💡 你现在可以尝试在Web界面中使用Google AI模型分析股票")
    else:
        print("\n💥 Google AI测试失败！")
        print("\n💡 建议:")
        print("   1. 检查代理设置是否正确")
        print("   2. 确保代理服务器可以访问Google服务")
        print("   3. 考虑使用阿里百炼模型进行A股分析")