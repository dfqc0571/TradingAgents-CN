import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
project_root = Path(__file__).parent
load_dotenv(project_root / ".env", override=True)

def test_google_ai_enhanced():
    print("🧪 增强版Google AI功能测试")
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
    
    # 配置Google AI（增加超时时间）
    try:
        # 配置transport以支持代理和增加超时
        genai.configure(
            api_key=google_api_key,
        )
        print("✅ Google AI配置成功")
    except Exception as e:
        print(f"❌ Google AI配置失败: {e}")
        return False
    
    # 测试具体模型（直接测试而不获取模型列表）
    test_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash", 
        "gemini-1.5-pro"
    ]
    
    for model_name in test_models:
        try:
            print(f"\n🔍 直接测试模型: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # 生成内容测试
            print("📝 测试内容生成...")
            response = model.generate_content(
                "请用中文简单介绍一下自己",
                generation_config=genai.GenerationConfig(
                    max_output_tokens=1000,
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
            import traceback
            print(f"   详细错误: {traceback.format_exc()}")
    
    return False

def test_with_langchain():
    """测试LangChain集成"""
    print("\n🧪 测试LangChain集成")
    print("=" * 50)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain-google-genai库导入成功")
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=google_api_key,
            temperature=0.1,
            max_tokens=1000
        )
        print("✅ LangChain模型实例创建成功")
        
        # 测试调用
        response = model.invoke("请用中文简单介绍一下人工智能")
        if response and response.content:
            print("✅ LangChain调用成功")
            print(f"   响应长度: {len(response.content)} 字符")
            print(f"   响应预览: {response.content[:100]}...")
            return True
        else:
            print("❌ LangChain调用失败：无响应内容")
            
    except Exception as e:
        print(f"❌ LangChain测试失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
    
    return False

if __name__ == "__main__":
    print("开始测试Google AI功能...")
    
    # 测试直接API调用
    direct_success = test_google_ai_enhanced()
    
    # 测试LangChain集成
    langchain_success = test_with_langchain()
    
    if direct_success or langchain_success:
        print("\n🎉 Google AI测试部分成功！")
        if direct_success:
            print("✅ 直接API调用成功")
        if langchain_success:
            print("✅ LangChain集成成功")
    else:
        print("\n💥 Google AI测试完全失败！")
        print("\n💡 建议:")
        print("   1. 检查网络连接，确保可以访问Google服务")
        print("   2. 考虑使用阿里百炼模型进行A股分析")
        print("   3. 如果有代理，请在环境变量中配置HTTP_PROXY和HTTPS_PROXY")