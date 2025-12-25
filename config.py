# 讯飞星辰API配置
XFYUN_CONFIG = {
    "app_id": "your_app_id",  # 请替换为实际的app_id
    "api_key": "your_api_key",  # 请替换为实际的api_key
    "api_secret": "your_api_secret",  # 请替换为实际的api_secret
    "model_id": "your_model_id",  # 模型ID
    "host": "maas-api.cn-huabei-1.xf-yun.com",  # API主机地址
    "path": "/v1.1/chat"  # API路径
}

# WebSocket配置
WS_CONFIG = {
    "timeout": 30,  # 连接超时时间（秒）
    "retry_times": 3  # 重试次数
}

# 应用配置
APP_CONFIG = {
    "debug": True,  # 调试模式
    "host": "0.0.0.0",  # 应用监听地址
    "port": 8000  # 应用监听端口
}

# 上下文配置
CONTEXT_CONFIG = {
    "max_history": 10,  # 最大历史消息数
    "expire_time": 3600  # 上下文过期时间（秒）
}
