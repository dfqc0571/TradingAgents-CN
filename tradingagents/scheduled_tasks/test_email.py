#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件配置测试脚本
用于验证SMTP配置是否正确，包括服务器连接、身份验证和邮件发送功能
"""

import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 自动加载.env文件
env_file = os.path.join(project_root, '.env')
if os.path.exists(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print("✅ .env文件加载成功")

# 邮件配置
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL', ''),
    'sender_password': os.getenv('SENDER_PASSWORD', ''),
    'recipient_emails': os.getenv('RECIPIENT_EMAILS', '').split(','),
}

def test_email_configuration():
    """
    测试邮件配置
    """
    print("📧 开始测试邮件配置...")
    
    # 检查必要配置
    if not EMAIL_CONFIG['sender_email']:
        print("❌ 错误: 未配置发件人邮箱 (SENDER_EMAIL)")
        return False
        
    if not EMAIL_CONFIG['sender_password']:
        print("❌ 错误: 未配置邮箱密码或授权码 (SENDER_PASSWORD)")
        return False
        
    if not EMAIL_CONFIG['recipient_emails'] or not any(email.strip() for email in EMAIL_CONFIG['recipient_emails']):
        print("❌ 错误: 未配置收件人邮箱 (RECIPIENT_EMAILS)")
        return False
    
    print(f"📧 发件人邮箱: {EMAIL_CONFIG['sender_email']}")
    print(f"📧 收件人邮箱: {', '.join([email.strip() for email in EMAIL_CONFIG['recipient_emails'] if email.strip()])}")
    print(f"📧 SMTP服务器: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
    
    try:
        # 创建测试邮件
        message = MIMEMultipart()
        # 使用标准格式设置发件人信息
        message['From'] = f'"Trading Agents" <{EMAIL_CONFIG["sender_email"]}>'
        message['To'] = ', '.join([email.strip() for email in EMAIL_CONFIG['recipient_emails'] if email.strip()])
        message['Subject'] = 'Trading Agents 邮件配置测试'
        
        body = '''
        <html>
        <body>
        <h2>📈 Trading Agents 邮件配置测试</h2>
        <p>恭喜！您的邮件配置已成功通过测试。</p>
        <p>此邮件用于验证SMTP服务器连接、身份验证和邮件发送功能是否正常工作。</p>
        <br>
        <p>--- Trading Agents 团队</p>
        </body>
        </html>
        '''
        
        message.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 连接SMTP服务器
        print("🔌 正在连接到SMTP服务器...")
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.set_debuglevel(1)
        
        # 启动TLS加密
        print("🔒 正在启动TLS加密...")
        server.starttls()
        
        # 身份验证
        print("🔐 正在进行身份验证...")
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        
        # 发送邮件
        print("📤 正在发送测试邮件...")
        server.sendmail(
            EMAIL_CONFIG['sender_email'],
            [email.strip() for email in EMAIL_CONFIG['recipient_emails'] if email.strip()],
            message.as_string()
        )
        
        # 断开连接
        server.quit()
        
        print("✅ 邮件发送成功！配置正确。")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP认证失败: {e}")
        print("请检查邮箱账号和密码/授权码是否正确")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ 无法连接到SMTP服务器: {e}")
        print("请检查SMTP服务器地址和端口配置")
        return False
    except smtplib.SMTPSenderRefused as e:
        print(f"❌ 发件人邮箱被拒绝: {e}")
        print("请检查发件人邮箱地址是否正确且已通过验证")
        return False
    except Exception as e:
        print(f"❌ 发送邮件时发生未知错误: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_email_configuration()
    if success:
        print("\n🎉 邮件配置测试通过！")
        sys.exit(0)
    else:
        print("\n💥 邮件配置测试失败！")
        sys.exit(1)