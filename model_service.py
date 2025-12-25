import time
import hmac
import hashlib
import base64
import json
import websocket
import threading
from config import XFYUN_CONFIG, WS_CONFIG

class SparkModelService:
    def __init__(self):
        self.app_id = XFYUN_CONFIG["app_id"]
        self.api_key = XFYUN_CONFIG["api_key"]
        self.api_secret = XFYUN_CONFIG["api_secret"]
        self.host = XFYUN_CONFIG["host"]
        self.path = XFYUN_CONFIG["path"]
        self.model_id = XFYUN_CONFIG["model_id"]
        self.ws = None
        self.response_buffer = []
        self.is_connected = False
        self.lock = threading.Lock()
        
    def generate_auth_url(self):
        """生成WebSocket鉴权URL"""
        # 生成RFC1123格式的时间戳
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        
        # 拼接签名字符串，确保host头正确使用
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        
        # 使用hmac-sha256算法生成签名
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'), 
                               digestmod=hashlib.sha256).digest()
        
        # 对签名进行base64编码
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        # 生成最终的authorization，注意引号格式
        authorization_origin = f"api_key=\"{self.api_key}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature}\""
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # 生成鉴权URL，确保参数正确编码
        import urllib.parse
        url = f"wss://{self.host}{self.path}?authorization={urllib.parse.quote(authorization)}&date={urllib.parse.quote(date)}&host={urllib.parse.quote(self.host)}"
        return url
    
    def on_message(self, ws, message):
        """WebSocket消息接收回调"""
        try:
            data = json.loads(message)
            print(f"收到模型响应: {json.dumps(data, ensure_ascii=False)}")
            with self.lock:
                self.response_buffer.append(data)
        except json.JSONDecodeError as e:
            print(f"解析WebSocket消息失败: {e}")
    
    def on_error(self, ws, error):
        """WebSocket错误回调"""
        print(f"WebSocket连接错误: {error}")
        self.is_connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭回调"""
        print(f"WebSocket连接关闭: {close_status_code} - {close_msg}")
        self.is_connected = False
    
    def on_open(self, ws):
        """WebSocket连接建立回调"""
        print("WebSocket连接已建立")
        self.is_connected = True
    
    def connect(self):
        """建立WebSocket连接"""
        if self.is_connected:
            return True
        
        url = self.generate_auth_url()
        self.ws = websocket.WebSocketApp(url, 
                                       on_open=self.on_open,
                                       on_message=self.on_message,
                                       on_error=self.on_error,
                                       on_close=self.on_close)
        
        # 启动WebSocket连接线程
        ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={"ping_interval": 30})
        ws_thread.daemon = True
        ws_thread.start()
        
        # 等待连接建立
        for _ in range(WS_CONFIG["timeout"]):
            if self.is_connected:
                return True
            time.sleep(1)
        
        return False
    
    def send_request(self, messages, temperature=0.5, top_k=4, max_tokens=2048, chat_id=None):
        """发送请求到模型"""
        # 确保WebSocket连接已建立
        if not self.connect():
            raise ConnectionError("无法建立WebSocket连接")
        
        # 构建请求参数
        request_data = {
            "header": {
                "app_id": self.app_id,
                "uid": chat_id or f"user_{int(time.time())}"
            },
            "parameter": {
                "chat": {
                    "domain": self.model_id,
                    "temperature": temperature,
                    "top_k": top_k,
                    "max_tokens": max_tokens,
                    "chat_id": chat_id,
                    "search_disable": False,
                    "show_ref_label": True,
                    "enable_thinking": True
                }
            },
            "payload": {
                "message": {
                    "text": messages
                }
            }
        }
        
        # 发送请求
        self.ws.send(json.dumps(request_data))
        
        # 清空之前的响应缓冲区
        with self.lock:
            self.response_buffer.clear()
    
    def get_response(self, timeout=60):
        """获取模型响应"""
        start_time = time.time()
        full_response = {"text": "", "ref_info": [], "is_finished": False}
        
        while time.time() - start_time < timeout:
            with self.lock:
                if self.response_buffer:
                    data = self.response_buffer.pop(0)
                    
                    # 处理响应
                    if "header" in data:
                        code = data["header"].get("code", 0)
                        if code != 0:
                            error_msg = data["header"].get("message", "未知错误")
                            raise Exception(f"模型调用错误: {code} - {error_msg}")
                    
                    # 检查响应格式并处理
                    if "payload" in data:
                        payload = data["payload"]
                        
                        # 处理choices字段
                        if "choices" in payload:
                            choices = payload["choices"]
                            if isinstance(choices, dict) and "text" in choices:
                                text_field = choices["text"]
                                if isinstance(text_field, list):
                                    for text_item in text_field:
                                        if isinstance(text_item, dict) and "content" in text_item:
                                            full_response["text"] += text_item["content"]
                    
                    # 处理search_info字段
                    if "payload" in data and "search_info" in data["payload"]:
                        search_info = data["payload"]["search_info"]
                        if isinstance(search_info, dict):
                            full_response["ref_info"].append(search_info)
                    
                    # 检查是否完成
                    if "header" in data and data["header"].get("status", 0) == 2:
                        full_response["is_finished"] = True
                        return full_response
            
            time.sleep(0.1)
        
        raise TimeoutError("模型响应超时")
    
    def chat(self, messages, temperature=0.5, top_k=4, max_tokens=2048, chat_id=None):
        """完整的聊天流程"""
        try:
            self.send_request(messages, temperature, top_k, max_tokens, chat_id)
            return self.get_response()
        except Exception as e:
            print(f"模型调用失败: {e}")
            raise
    
    def close(self):
        """关闭WebSocket连接"""
        if self.ws:
            self.ws.close()
            self.is_connected = False
