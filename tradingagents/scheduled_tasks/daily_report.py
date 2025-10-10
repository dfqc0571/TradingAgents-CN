#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日交易决策报告定时任务
在每天开盘前自动生成并发送详细的交易决策报告
"""

import sys
import os
from datetime import datetime, time, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import schedule
import time as time_module
import asyncio
import threading

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

# 手动确保关键环境变量被设置
required_env_vars = ['MODELSCOPE_API_KEY', 'DASHSCOPE_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        print(f"⚠️  警告: 环境变量 {var} 未设置")

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
# 确保日志目录存在
log_dir = os.path.join(project_root, 'tradingagents', 'scheduled_tasks', 'logs')
os.makedirs(log_dir, exist_ok=True)
logger = get_logger('scheduled_tasks.daily_report')

# 导入API模块
try:
    from tradingagents.api.main_api import get_comprehensive_stock_analysis
    SCHEDULER_AVAILABLE = True
except ImportError as e:
    logger.error(f"定时任务模块导入失败: {e}")
    SCHEDULER_AVAILABLE = False

# 邮件配置
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'sender_email': os.getenv('SENDER_EMAIL', ''),
    'sender_password': os.getenv('SENDER_PASSWORD', ''),
    'recipient_emails': os.getenv('RECIPIENT_EMAILS', '').split(','),
}

# 默认关注的股票列表
DEFAULT_STOCKS = os.getenv('DEFAULT_STOCKS', '000001,000002,600000,600036').split(',')

# 添加防止重复执行的机制
_last_execution_time = None
_min_interval_minutes = 30  # 最小间隔30分钟

def generate_stock_report(stock_code: str) -> dict:
    """
    生成单个股票的详细分析报告
    
    Args:
        stock_code: 股票代码
    
    Returns:
        dict: 股票分析报告
    """
    try:
        logger.info(f"开始生成股票 {stock_code} 的分析报告")
        
        # 确保使用魔搭社区配置
        import os
        os.environ["DEFAULT_LLM_PROVIDER"] = "modelscope"
        os.environ["DEEP_THINK_LLM"] = "ZhipuAI/GLM-4.5"
        os.environ["QUICK_THINK_LLM"] = "ZhipuAI/GLM-4.5"
        
        # 重新导入以确保使用最新配置
        import importlib
        import tradingagents.api.main_api
        importlib.reload(tradingagents.api.main_api)
        from tradingagents.api.main_api import get_comprehensive_stock_analysis
        
        report = get_comprehensive_stock_analysis(stock_code)
        logger.info(f"股票 {stock_code} 的分析报告生成完成")
        return report
    except Exception as e:
        logger.error(f"生成股票 {stock_code} 的分析报告时发生错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return {
            'error': str(e),
            'code': stock_code,
            'generated_at': datetime.now().isoformat()
        }

def format_report_as_html(reports: list) -> str:
    """
    将报告格式化为HTML格式
    
    Args:
        reports: 股票分析报告列表
    
    Returns:
        str: HTML格式的报告
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>每日交易决策报告</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
            .stock-report { margin-bottom: 30px; padding: 15px; border: 1px solid #bdc3c7; border-radius: 5px; }
            .error { color: #e74c3c; }
            .info { background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .decision { background-color: #d5f5e3; padding: 15px; border-left: 5px solid #27ae60; margin: 15px 0; }
            .risk { background-color: #fadbd8; padding: 15px; border-left: 5px solid #e74c3c; margin: 15px 0; }
            pre { background-color: #f8f9fa; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>📈 每日交易决策报告</h1>
        <div class="info">
            <p><strong>报告生成时间:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p><strong>报告类型:</strong> 深度分析报告</p>
        </div>
    """
    
    for i, report in enumerate(reports):
        logger.info(f"处理第 {i+1} 个报告: {report.get('code', 'Unknown')}")
        if 'error' in report:
            html += f"""
            <div class="stock-report">
                <h2>❌ 股票 {report.get('code', 'Unknown')} 分析报告生成失败</h2>
                <p class="error">错误信息: {report['error']}</p>
                <p>生成时间: {report.get('generated_at', 'N/A')}</p>
            </div>
            """
        else:
            # 处理港股"非交易日"情况，降级处理显示为"N/A"
            def format_value(value):
                if isinstance(value, str) and "Not a trading day" in value:
                    return "N/A"
                # 检查是否为None或者空字符串
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    return "N/A"
                # 特殊处理价格字段，如果为0则显示为"0"
                if isinstance(value, (int, float)) and value == 0:
                    return "0"
                return value
            
            # 获取股票基本信息
            basic_info = report.get('basic_info', {})
            risk_assessment = report.get('risk_assessment', {})
            market_risk = risk_assessment.get('market_risk', {}) if isinstance(risk_assessment, dict) else {}
            news_sentiment = risk_assessment.get('news_sentiment', {}) if isinstance(risk_assessment, dict) else {}
            
            # 获取技术分析信息
            technical_analysis = report.get('technical_analysis', {})
            indicators = technical_analysis.get('indicators', {}) if isinstance(technical_analysis, dict) else {}
            
            # 获取交易信号
            trading_signals = report.get('trading_signals', {})
            
            # 获取趋势预测
            trend_prediction = report.get('trend_prediction', {})
            
            # 获取投资建议
            investment_suggestion = report.get('investment_suggestion', {})
            
            # 获取投资辩论和风险辩论过程
            investment_debate_state = report.get('investment_debate_state', {})
            risk_debate_state = report.get('risk_debate_state', {})
            
            # 获取市场报告、新闻报告和基本面报告
            market_report = report.get('market_report', '')
            news_report = report.get('news_report', '')
            fundamentals_report = report.get('fundamentals_report', '')
            
            html += f"""
            <div class="stock-report">
                <h2>📊 股票 {basic_info.get('name', report.get('code', 'N/A'))} ({report.get('code', 'N/A')}) 分析报告</h2>
                
                <h3>基本信息</h3>
                <div class="info">
                    <p><strong>股票名称:</strong> {format_value(basic_info.get('name', 'N/A'))}</p>
                    <p><strong>股票代码:</strong> {format_value(report.get('code', 'N/A'))}</p>
                    <p><strong>市场:</strong> {format_value(basic_info.get('market', 'N/A'))}</p>
                    <p><strong>类别:</strong> {format_value(basic_info.get('category', 'N/A'))}</p>
                </div>
                
                <h3>当前价格信息</h3>
                <div class="info">
                    <p><strong>RSI指标:</strong> {format_value(indicators.get('rsi_14', 'N/A'))}</p>
                    <p><strong>MACD指标:</strong> {format_value(indicators.get('macd', 'N/A'))}</p>
                    <p><strong>布林带上轨:</strong> {format_value(indicators.get('boll_ub', 'N/A'))}</p>
                    <p><strong>布林带下轨:</strong> {format_value(indicators.get('boll_lb', 'N/A'))}</p>
                </div>
                
                <h3>投资决策</h3>
                <div class="decision">
                    <p><strong>交易信号:</strong> {format_value(trading_signals.get('recommendation', 'N/A'))}</p>
                    <p><strong>投资建议:</strong> {format_value(investment_suggestion.get('action', 'N/A'))}</p>
                    <p><strong>建议理由:</strong> {format_value(investment_suggestion.get('reason', 'N/A'))}</p>
                </div>
                
                <h3>风险评估</h3>
                <div class="risk">
                    <p><strong>风险等级:</strong> {format_value(market_risk.get('risk_level', 'N/A'))}</p>
                    <p><strong>风险描述:</strong> {format_value(market_risk.get('description', 'N/A'))}</p>
                    <p><strong>新闻情绪:</strong> {format_value(news_sentiment.get('sentiment', 'N/A'))}</p>
                </div>
                
                <h3>趋势预测</h3>
                <div class="info">
                    <p><strong>整体趋势:</strong> {format_value(trend_prediction.get('overall_trend', 'N/A'))}</p>
                    <p><strong>预测建议:</strong> {format_value(trend_prediction.get('recommendation', 'N/A'))}</p>
                </div>
                
                <h3>市场分析报告</h3>
                <pre>{format_value(market_report)}</pre>
                
                <h3>新闻分析报告</h3>
                <pre>{format_value(news_report)}</pre>
                
                <h3>基本面分析报告</h3>
                <pre>{format_value(fundamentals_report)}</pre>
                
                <h3>投资辩论过程</h3>
                <pre>{json.dumps(investment_debate_state, ensure_ascii=False, indent=2)}</pre>
                
                <h3>风险辩论过程</h3>
                <pre>{json.dumps(risk_debate_state, ensure_ascii=False, indent=2)}</pre>
            </div>
            """
    
    html += """
    </body>
    </html>
    """
    
    return html

def send_email(subject: str, content: str, content_type: str = 'html') -> bool:
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        content: 邮件内容
        content_type: 内容类型 (plain 或 html)
    
    Returns:
        bool: 发送是否成功
    """
    try:
        if not EMAIL_CONFIG['sender_email'] or not EMAIL_CONFIG['sender_password']:
            logger.warning("邮件配置不完整，跳过发送邮件")
            return False
        
        # 检查收件人列表
        if not EMAIL_CONFIG['recipient_emails'] or not any(EMAIL_CONFIG['recipient_emails']):
            logger.warning("未配置收件人邮箱，跳过发送邮件")
            return False
            
        # 创建邮件对象
        message = MIMEMultipart()
        # 使用标准格式设置发件人信息，避免QQ邮箱拒绝
        message['From'] = f'"Trading Agents" <{EMAIL_CONFIG["sender_email"]}>'
        message['To'] = ', '.join([email.strip() for email in EMAIL_CONFIG['recipient_emails'] if email.strip()])
        message['Subject'] = subject
        
        # 添加邮件正文
        message.attach(MIMEText(content, content_type, 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        logger.info(f"正在连接到SMTP服务器: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.set_debuglevel(1)  # 启用调试模式
        logger.info("正在启动TLS加密...")
        server.starttls()
        logger.info("正在进行身份验证...")
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        logger.info("正在发送邮件...")
        server.sendmail(
            EMAIL_CONFIG['sender_email'], 
            [email.strip() for email in EMAIL_CONFIG['recipient_emails'] if email.strip()], 
            message.as_string()
        )
        server.quit()
        
        logger.info("✅ 邮件发送成功")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP认证失败: {e}")
        logger.error("请检查邮箱账号和密码/授权码是否正确")
        return False
    except smtplib.SMTPConnectError as e:
        logger.error(f"❌ 无法连接到SMTP服务器: {e}")
        logger.error("请检查SMTP服务器地址和端口配置")
        return False
    except smtplib.SMTPSenderRefused as e:
        logger.error(f"❌ 发件人邮箱被拒绝: {e}")
        logger.error("请检查发件人邮箱地址是否正确且已通过验证")
        return False
    except Exception as e:
        logger.error(f"❌ 发送邮件时发生未知错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

def generate_and_send_daily_report():
    """
    生成并发送每日交易决策报告
    """
    global _last_execution_time, _min_interval_minutes
    
    # 检查是否在最小间隔时间内重复执行
    current_time = datetime.now()
    if _last_execution_time:
        time_diff = (current_time - _last_execution_time).total_seconds() / 60
        if time_diff < _min_interval_minutes:
            logger.info(f"跳过执行，距离上次执行仅 {time_diff:.1f} 分钟，最小间隔 {_min_interval_minutes} 分钟")
            return True
    
    try:
        logger.info("开始执行每日交易决策报告任务")
        logger.info(f"关注的股票列表: {DEFAULT_STOCKS}")
        
        # 更新最后执行时间
        _last_execution_time = current_time
        
        # 生成所有关注股票的报告
        reports = []
        for stock_code in DEFAULT_STOCKS:
            logger.info(f"正在处理股票: {stock_code.strip()}")
            report = generate_stock_report(stock_code.strip())
            reports.append(report)
        
        # 格式化报告为HTML
        html_content = format_report_as_html(reports)
        
        # 发送邮件
        subject = f"📈 每日交易决策报告 - {datetime.now().strftime('%Y-%m-%d')}"
        send_email(subject, html_content, 'html')
        
        logger.info("每日交易决策报告任务执行完成")
        return True
    except Exception as e:
        logger.error(f"执行每日交易决策报告任务时发生错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False

def schedule_daily_task():
    """
    安排每日任务
    """
    # 从环境变量获取执行时间，默认为09:25
    execution_times_str = os.getenv('DAILY_REPORT_TIMES', '09:25')
    
    # 支持配置多个执行时间，用逗号分隔
    execution_times = [t.strip() for t in execution_times_str.split(',') if t.strip()]
    
    # 设置每天执行任务的时间
    for exec_time in execution_times:
        schedule.every().day.at(exec_time).do(generate_and_send_daily_report)
        logger.info(f"每日交易决策报告任务已安排，将在每天{exec_time}执行")
    
    while True:
        schedule.run_pending()
        time_module.sleep(60)  # 每分钟检查一次

def run_scheduler():
    """
    运行定时任务调度器
    """
    if not SCHEDULER_AVAILABLE:
        logger.error("定时任务模块不可用")
        return
    
    logger.info("启动每日交易决策报告定时任务调度器")
    
    # 在单独的线程中运行调度器
    scheduler_thread = threading.Thread(target=schedule_daily_task)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    return scheduler_thread

# 提供手动执行的接口
def manual_generate_report():
    """
    手动生成报告（用于测试）
    """
    return generate_and_send_daily_report()

if __name__ == "__main__":
    # 直接运行定时任务
    schedule_daily_task()