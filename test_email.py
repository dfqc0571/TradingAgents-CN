#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件配置测试脚本
用于测试.env文件中的邮件配置是否正确
"""

import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

def load_env_file():
    """加载.env文件中的环境变量"""
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")
        print("✅ .env文件加载成功")
    else:
        print("⚠️ .env文件未找到，请确保已创建并配置")

def test_email_config():
    """测试邮件配置"""
    # 从环境变量获取配置
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SENDER_EMAIL', '')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')
    
    # 检查必要配置
    if not sender_email or not sender_password:
        print("❌ 邮件配置不完整，请检查.env文件中的SENDER_EMAIL和SENDER_PASSWORD配置")
        return False
    
    if not recipient_emails or not recipient_emails[0]:
        print("❌ 请配置收件人邮箱RECIPIENT_EMAILS")
        return False
    
    print(f"📧 邮件配置信息:")
    print(f"   SMTP服务器: {smtp_server}")
    print(f"   SMTP端口: {smtp_port}")
    print(f"   发件人邮箱: {sender_email}")
    print(f"   收件人邮箱: {', '.join(recipient_emails)}")
    
    try:
        # 创建测试邮件
        message = MIMEMultipart()
        message['From'] = Header(f"Trading Agents <{sender_email}>")
        message['To'] = Header(','.join(recipient_emails))
        message['Subject'] = Header("📈 TradingAgents-CN 邮件配置测试", 'utf-8')
        
        # 邮件正文
        body = """
        <h2>TradingAgents-CN 邮件配置测试</h2>
        <p>恭喜！您的邮件配置已经成功。</p>
        <p>这是一封测试邮件，用于验证TradingAgents-CN系统的邮件发送功能是否正常工作。</p>
        <p>如果您收到此邮件，说明系统可以正常发送分析报告。</p>
        <br>
        <p>TradingAgents-CN 团队</p>
        """
        message.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        print("🔄 正在连接SMTP服务器...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 启用TLS加密
        print("🔒 正在进行身份验证...")
        server.login(sender_email, sender_password)
        print("📤 正在发送邮件...")
        server.sendmail(sender_email, recipient_emails, message.as_string())
        server.quit()
        
        print("✅ 邮件发送成功！请检查您的收件箱。")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP认证失败，请检查邮箱账号和密码是否正确")
        return False
    except smtplib.SMTPConnectError:
        print("❌ 无法连接到SMTP服务器，请检查服务器地址和端口配置")
        return False
    except Exception as e:
        print(f"❌ 发送邮件时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("📧 TradingAgents-CN 邮件配置测试工具")
    print("=" * 50)
    
    # 加载环境变量
    load_env_file()
    
    # 测试邮件配置
    success = test_email_config()
    
    if success:
        print("\n🎉 邮件配置测试完成！")
        print("您的邮件配置已通过测试，系统可以正常发送分析报告。")
    else:
        print("\n❌ 邮件配置测试失败！")
        print("请检查您的邮件配置，确保以下信息正确：")
        print("1. SMTP服务器地址和端口")
        print("2. 发件人邮箱账号和密码（或授权码）")
        print("3. 收件人邮箱地址")
        print("\n💡 常见问题解决方法：")
        print("- 检查邮箱是否开启了SMTP服务")
        print("- 检查是否使用了正确的授权码而非登录密码")
        print("- 检查防火墙或网络设置是否阻止了SMTP连接")

if __name__ == "__main__":
    main()