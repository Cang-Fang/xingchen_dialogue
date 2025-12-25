from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
import threading
import time
from model_service import SparkModelService
from message_manager import MessageManager
from config import APP_CONFIG

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # 用于会话管理
CORS(app)  # 允许跨域请求

# 初始化服务
model_service = SparkModelService()
message_manager = MessageManager()

# 定期清理过期会话的线程
class SessionCleaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
    
    def run(self):
        while self.running:
            expired_count = message_manager.clean_expired_sessions()
            if expired_count > 0:
                print(f"清理了 {expired_count} 个过期会话")
            time.sleep(300)  # 每5分钟清理一次

@app.route('/')
def index():
    # 为每个用户生成唯一的会话ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html', session_id=session['session_id'])

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        session_id = data.get('session_id', str(uuid.uuid4()))
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "消息不能为空"}), 400
        
        # 添加用户消息到上下文
        message_manager.add_message(session_id, "user", message)
        
        # 获取对话上下文
        context = message_manager.get_context(session_id)
        
        # 调用模型生成回复
        response = model_service.chat(context)
        
        # 添加模型回复到上下文
        message_manager.add_message(session_id, "assistant", response["text"])
        
        return jsonify({
            "session_id": session_id,
            "response": response["text"],
            "ref_info": response["ref_info"],
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/clear_context', methods=['POST'])
def clear_context():
    """清理对话上下文"""
    try:
        session_id = request.json.get('session_id')
        if session_id:
            message_manager.delete_session(session_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/session_info', methods=['GET'])
def session_info():
    """获取会话信息"""
    return jsonify({
        "session_count": message_manager.get_session_count(),
        "success": True
    })

if __name__ == '__main__':
    # 启动会话清理线程
    cleaner = SessionCleaner()
    cleaner.start()
    
    print(f"聊天机器人服务启动在 http://{APP_CONFIG['host']}:{APP_CONFIG['port']}")
    app.run(
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port'],
        debug=APP_CONFIG['debug']
    )
