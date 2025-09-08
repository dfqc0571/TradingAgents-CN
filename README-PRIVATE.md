# 私有配置保护分支

这个分支专门用于保护敏感配置信息，确保API密钥等敏感数据不会被上传到公共仓库。

## 安全措施

1. **.gitignore配置**：
   - 防止.env文件被提交
   - 防止其他敏感配置文件被提交

2. **敏感信息保护**：
   - API密钥存储在本地.env文件中
   - 不会上传到远程仓库

## 使用说明

1. 克隆此分支：
   ```bash
   git clone -b 私有配置保护 https://github.com/dfqc0571/TradingAgents-CN.git
   ```

2. 在本地创建.env文件：
   ```bash
   cp .env.example .env
   ```

3. 编辑.env文件，填入您的API密钥：
   ```env
   GOOGLE_API_KEY=your_google_api_key
   DASHSCOPE_API_KEY=your_dashscope_api_key
   FINNHUB_API_KEY=your_finnhub_api_key
   ```

## 注意事项

- 请勿将.env文件提交到仓库
- 定期检查.gitignore配置确保敏感文件被正确忽略
- 在团队协作时，通过安全渠道共享API密钥

## 分支维护

此分支将定期与主分支同步，以获取最新的功能更新和安全补丁。