import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
project_root = Path(__file__).parent
load_dotenv(project_root / ".env", override=True)

def test_google_ai():
    print("🧪 Google AI功能测试")
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
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain-google-genai库导入成功")
    except ImportError as e:
        print(f"❌ langchain-google-genai库导入失败: {e}")
        return False
    
    # 配置Google AI
    try:
        genai.configure(api_key=google_api_key)
        print("✅ Google AI配置成功")
    except Exception as e:
        print(f"❌ Google AI配置失败: {e}")
        return False
    
    # 测试模型列表
    try:
        print("🔍 获取可用模型列表...")
        models = genai.list_models()
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        print(f"✅ 找到 {len(gemini_models)} 个Gemini模型")
        for model in gemini_models[:5]:  # 显示前5个
            print(f"   - {model.name}")
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return False
    
    # 测试具体模型
    test_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash", 
        "gemini-1.5-pro"
    ]
    
    for model_name in test_models:
        try:
            print(f"\n🔍 测试模型: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("请用中文简单介绍一下自己")
            if response and response.text:
                print(f"✅ {model_name} 调用成功")
                print(f"   响应长度: {len(response.text)} 字符")
                return True
        except Exception as e:
            print(f"❌ {model_name} 调用失败: {e}")
    
    return False

if __name__ == "__main__":
    success = test_google_ai()
    if success:
        print("\n🎉 Google AI测试成功！")
    else:
        print("\n💥 Google AI测试失败！")