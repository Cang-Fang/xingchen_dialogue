# 注意
本程序是利用TRAE创作的

# 智能聊天机器人系统

一个基于讯飞星辰MaaS平台的模型API的半成品对话框，具备自然语言对话交互的能力。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户交互界面                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  Web前端                        │    │
│  │  - HTML/CSS/JavaScript                         │    │
│  │  - 响应式设计                                   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                     消息处理模块                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  Flask后端                       │    │
│  │  - 路由管理                                     │    │
│  │  - 请求处理                                     │    │
│  │  - 响应生成                                     │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                     上下文管理模块                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  MessageManager                  │    │
│  │  - 会话创建与管理                                │    │
│  │  - 消息添加与存储                                │    │
│  │  - 上下文获取与格式化                             │    │
│  │  - 过期会话清理                                   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                     模型调用服务                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 SparkModelService                │    │
│  │  - WebSocket鉴权URL生成                           │    │
│  │  - 模型API调用                                    │    │
│  │  - 响应数据解析                                   │    │
│  │  - 错误处理与重试                                 │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                     数据存储单元                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  DataStorage                    │    │
│  │  - 对话历史保存                                  │    │
│  │  - 对话历史加载                                  │    │
│  │  - 旧对话清理                                    │    │
│  │  - 数据导出                                      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

- **后端框架**：Flask 2.3.3
- **前端技术**：HTML5, CSS3, JavaScript (ES6+)
- **WebSocket客户端**：websocket-client 1.6.3
- **数据存储**：JSON文件存储
- **模型服务**：讯飞星辰MaaS平台 ChatQwen3-1.7B

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd bot
```

### 2. 安装依赖

使用pip安装项目所需的依赖包：

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

编辑 `config.py` 文件，配置讯飞星辰API的相关信息：

```python
XFYUN_CONFIG = {
    "app_id": "your_app_id",  # 替换为实际的app_id
    "api_key": "your_api_key",  # 替换为实际的api_key
    "api_secret": "your_api_secret",  # 替换为实际的api_secret
    "model_id": "ChatQwen3-1.7B",  # 模型ID
    "host": "maas-api.cn-huabei-1.xf-yun.com",  # API主机地址
    "path": "/v1.1/chat"  # API路径
}
```

### 4. 启动服务

```bash
python app.py
```

服务将在 `http://0.0.0.0:8000` 启动，您可以通过浏览器访问该地址使用聊天机器人。

## 配置说明

### 主要配置项

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `app_id` | 讯飞星辰API的应用ID | `your_app_id` |
| `api_key` | 讯飞星辰API的API Key | `your_api_key` |
| `api_secret` | 讯飞星辰API的API Secret | `your_api_secret` |
| `model_id` | 调用的模型ID | `your_model_id` |
| `host` | API主机地址 | `maas-api.cn-huabei-1.xf-yun.com` |
| `path` | API路径 | `/v1.1/chat` |
| `debug` | 调试模式 | `True` |
| `host` | 应用监听地址 | `0.0.0.0` |
| `port` | 应用监听端口 | `8000` |
| `max_history` | 最大历史消息数 | `10` |
| `expire_time` | 上下文过期时间（秒） | `3600` |

### 配置文件

- `config.py`：主配置文件，包含API密钥、应用配置、上下文配置等

## API文档

### 1. 聊天接口

**URL**：`/api/chat`

**方法**：`POST`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| `session_id` | `string` | 否 | 会话ID，不提供则自动生成 |
| `message` | `string` | 是 | 用户输入的消息 |

**响应示例**：

```json
{
    "session_id": "test_session_123",
    "response": "你好！我是智能聊天机器人，很高兴为你服务。",
    "ref_info": [],
    "success": true
}
```

### 2. 清理上下文接口

**URL**：`/api/clear_context`

**方法**：`POST`

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| `session_id` | `string` | 是 | 要清理的会话ID |

**响应示例**：

```json
{
    "success": true
}
```

### 3. 会话信息接口

**URL**：`/api/session_info`

**方法**：`GET`

**响应示例**：

```json
{
    "session_count": 5,
    "success": true
}
```

## 部署指南

### 开发环境部署

1. 安装Python 3.8+和pip
2. 克隆项目并安装依赖
3. 配置API密钥
4. 启动开发服务器

### 生产环境部署

#### 使用Gunicorn部署

1. 安装Gunicorn：

```bash
pip install gunicorn
```

2. 使用Gunicorn启动服务：

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### 使用Docker部署

1. 创建Dockerfile：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

2. 构建Docker镜像：

```bash
docker build -t chatbot .
```

3. 运行Docker容器：

```bash
docker run -p 8000:8000 chatbot
```

### 反向代理配置

建议使用Nginx或Apache作为反向代理，以提高性能和安全性：

**Nginx配置示例**：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 测试说明

### 功能测试

运行测试脚本验证核心功能：

```bash
python test_chatbot.py
```

测试内容包括：
- 会话创建与管理
- 消息添加与存储
- 上下文获取与格式化
- 模型调用（需要配置正确的API密钥）
- 多轮对话管理
- 会话清理与过期处理

### 性能测试

1. 使用Apache Bench进行并发测试：

```bash
ab -n 100 -c 10 http://localhost:8000/
```

2. 使用wrk进行更详细的性能测试：

```bash
wrk -t12 -c400 -d30s http://localhost:8000/
```

### 安全测试

- 检查API密钥是否安全存储
- 验证用户数据是否得到保护
- 测试输入验证和输出编码
- 检查是否存在常见的Web漏洞

### 兼容性测试

在以下环境中测试系统：
- 主流浏览器：Chrome, Firefox, Safari, Edge
- 不同设备：桌面端, 平板, 手机
- 不同操作系统：Windows, macOS, Linux, iOS, Android

## 项目结构

```
bot/
├── app.py                 # 主应用入口，Flask后端
├── config.py              # 配置文件
├── model_service.py       # 模型调用服务，WebSocket通信
├── message_manager.py     # 消息处理和上下文管理
├── data_storage.py        # 数据存储单元
├── requirements.txt       # 项目依赖
├── test_chatbot.py        # 测试脚本
├── README.md              # 项目文档
├── templates/             # HTML模板
│   └── index.html         # 主页面模板
└── static/                # 静态文件
    ├── css/               # CSS样式
    │   └── style.css      # 主样式文件
    └── js/                # JavaScript脚本
        └── main.js        # 前端逻辑
```

## 开发说明

### 代码规范

- 遵循PEP 8编码规范（Python）
- 使用ES6+语法（JavaScript）
- 代码注释清晰，便于维护
- 函数和方法职责单一

### 扩展建议

1. **添加更多模型支持**：支持多种大语言模型
2. **增强搜索功能**：集成更多搜索引擎
3. **添加语音交互**：支持语音输入和输出
4. **添加多语言支持**：支持多种语言对话
5. **添加情感分析**：分析用户情感并调整回复
6. **添加知识库管理**：支持自定义知识库
7. **添加用户管理**：支持用户注册和登录
8. **添加对话历史导出**：支持导出对话记录

## 故障排除

### 常见问题

1. **模型调用失败**：
   - 检查API密钥是否正确配置
   - 检查网络连接是否正常
   - 检查防火墙设置

2. **会话管理问题**：
   - 检查会话过期时间设置
   - 检查会话清理机制是否正常工作

3. **性能问题**：
   - 调整工作进程数量
   - 优化数据库查询
   - 使用缓存机制

4. **兼容性问题**：
   - 检查浏览器版本
   - 检查CSS和JavaScript语法
   - 测试不同设备和操作系统

### 日志查看

- 开发模式下，日志会直接输出到控制台
- 生产模式下，建议配置日志文件

## 更新日志

### v1.0.0 (2025-12-25)

- 初始版本发布
- 实现基本的聊天功能
- 集成讯飞星辰模型API
- 实现对话上下文管理
- 实现数据持久化存储
- 开发响应式用户界面

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目维护者：[Cang-Fang]
- 邮箱：[1753013007@qq.com]
- 项目地址：[https://github.com/Cang-Fang/xingchen_dialogue]

## 致谢

- 感谢讯飞星辰MaaS平台提供的强大模型API
- 感谢所有为项目做出贡献的开发者
- 感谢社区的支持和反馈
