import json
import os
import time
from datetime import datetime

class DataStorage:
    def __init__(self, storage_dir="data"):
        self.storage_dir = storage_dir
        self.conversations_file = os.path.join(storage_dir, "conversations.json")
        self.init_storage()
    
    def init_storage(self):
        """初始化存储目录和文件"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        if not os.path.exists(self.conversations_file):
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def save_conversation(self, session_id, messages):
        """保存对话历史"""
        conversations = self.load_all_conversations()
        
        conversations[session_id] = {
            "messages": messages,
            "last_updated": time.time(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    def load_conversation(self, session_id):
        """加载特定会话的对话历史"""
        conversations = self.load_all_conversations()
        return conversations.get(session_id, {
            "messages": [],
            "last_updated": time.time(),
            "updated_at": datetime.now().isoformat()
        })
    
    def load_all_conversations(self):
        """加载所有对话历史"""
        try:
            with open(self.conversations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def delete_conversation(self, session_id):
        """删除特定会话的对话历史"""
        conversations = self.load_all_conversations()
        
        if session_id in conversations:
            del conversations[session_id]
            
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
            return True
        
        return False
    
    def clean_old_conversations(self, days=7):
        """清理指定天数前的对话历史"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        conversations = self.load_all_conversations()
        
        old_conversations = []
        for session_id, data in conversations.items():
            if data.get("last_updated", 0) < cutoff_time:
                old_conversations.append(session_id)
        
        for session_id in old_conversations:
            del conversations[session_id]
        
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
        
        return len(old_conversations)
    
    def get_conversation_count(self):
        """获取对话历史数量"""
        conversations = self.load_all_conversations()
        return len(conversations)
    
    def save_message(self, session_id, role, content):
        """保存单条消息"""
        conversation = self.load_conversation(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "created_at": datetime.now().isoformat()
        }
        
        conversation["messages"].append(message)
        conversation["last_updated"] = time.time()
        conversation["updated_at"] = datetime.now().isoformat()
        
        conversations = self.load_all_conversations()
        conversations[session_id] = conversation
        
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    def export_conversations(self, format="json"):
        """导出对话历史"""
        conversations = self.load_all_conversations()
        
        if format == "json":
            return json.dumps(conversations, ensure_ascii=False, indent=2)
        elif format == "txt":
            txt_content = ""
            for session_id, data in conversations.items():
                txt_content += f"=== 会话 {session_id} ===\n"
                txt_content += f"最后更新: {data['updated_at']}\n\n"
                for msg in data['messages']:
                    txt_content += f"[{msg['role']}] {msg['content']}\n\n"
                txt_content += "\n"
            return txt_content
        else:
            raise ValueError(f"不支持的导出格式: {format}")
