import time
from config import CONTEXT_CONFIG
from data_storage import DataStorage

class MessageManager:
    def __init__(self):
        self.context_store = {}
        self.max_history = CONTEXT_CONFIG["max_history"]
        self.expire_time = CONTEXT_CONFIG["expire_time"]
        self.data_storage = DataStorage()
    
    def create_session(self, session_id):
        """创建新会话"""
        if session_id not in self.context_store:
            self.context_store[session_id] = {
                "messages": [],
                "last_active": time.time()
            }
    
    def add_message(self, session_id, role, content):
        """添加消息到会话上下文"""
        if session_id not in self.context_store:
            self.create_session(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time()
        }
        
        self.context_store[session_id]["messages"].append(message)
        self.context_store[session_id]["last_active"] = time.time()
        
        # 限制历史消息数量
        if len(self.context_store[session_id]["messages"]) > self.max_history:
            self.context_store[session_id]["messages"] = self.context_store[session_id]["messages"][-self.max_history:]
        
        # 保存到持久化存储
        self.data_storage.save_conversation(session_id, self.context_store[session_id]["messages"])
    
    def get_context(self, session_id):
        """获取会话上下文"""
        if session_id not in self.context_store:
            # 从持久化存储加载对话历史
            saved_conversation = self.data_storage.load_conversation(session_id)
            self.context_store[session_id] = {
                "messages": saved_conversation["messages"],
                "last_active": time.time()
            }
        
        # 检查会话是否过期
        if time.time() - self.context_store[session_id]["last_active"] > self.expire_time:
            self.context_store[session_id] = {
                "messages": [],
                "last_active": time.time()
            }
        
        # 将消息格式化为模型所需的格式
        context_messages = []
        for msg in self.context_store[session_id]["messages"]:
            context_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return context_messages
    
    def update_last_active(self, session_id):
        """更新会话最后活跃时间"""
        if session_id in self.context_store:
            self.context_store[session_id]["last_active"] = time.time()
    
    def delete_session(self, session_id):
        """删除会话"""
        if session_id in self.context_store:
            del self.context_store[session_id]
        # 从持久化存储中删除对话历史
        self.data_storage.delete_conversation(session_id)
    
    def clean_expired_sessions(self):
        """清理过期会话"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.context_store.items():
            if current_time - session_data["last_active"] > self.expire_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.context_store[session_id]
        
        return len(expired_sessions)
    
    def get_session_count(self):
        """获取当前会话数量"""
        return len(self.context_store)
