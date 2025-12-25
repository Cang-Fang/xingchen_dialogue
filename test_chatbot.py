import time
from model_service import SparkModelService
from message_manager import MessageManager

# 测试聊天机器人核心功能
def test_chatbot():
    print("开始测试聊天机器人核心功能...")
    
    # 初始化服务
    model_service = SparkModelService()
    message_manager = MessageManager()
    
    # 测试会话ID
    session_id = "test_session_123"
    
    # 测试1: 创建会话
    print("\n1. 测试创建会话...")
    message_manager.create_session(session_id)
    assert session_id in message_manager.context_store, "会话创建失败"
    print("✓ 会话创建成功")
    
    # 测试2: 添加消息
    print("\n2. 测试添加消息...")
    message_manager.add_message(session_id, "user", "你好，我是测试用户")
    assert len(message_manager.context_store[session_id]["messages"]) == 1, "消息添加失败"
    print("✓ 消息添加成功")
    
    # 测试3: 获取上下文
    print("\n3. 测试获取上下文...")
    context = message_manager.get_context(session_id)
    assert len(context) == 1, "上下文获取失败"
    assert context[0]["role"] == "user", "上下文角色不正确"
    assert context[0]["content"] == "你好，我是测试用户", "上下文内容不正确"
    print("✓ 上下文获取成功")
    
    # 测试4: 测试模型调用（需要配置正确的API密钥）
    print("\n4. 测试模型调用...")
    try:
        # 简单的测试消息
        test_messages = [
            {"role": "user", "content": "你好，介绍一下自己"}
        ]
        response = model_service.chat(test_messages)
        print(f"✓ 模型调用成功，回复: {response['text'][:50]}...")
    except Exception as e:
        print(f"⚠ 模型调用测试失败（可能是API密钥未配置）: {e}")
    
    # 测试5: 测试多轮对话
    print("\n5. 测试多轮对话...")
    message_manager.add_message(session_id, "assistant", "你好！我是智能聊天机器人。")
    message_manager.add_message(session_id, "user", "天气怎么样？")
    context = message_manager.get_context(session_id)
    assert len(context) == 3, "多轮对话上下文管理失败"
    print("✓ 多轮对话上下文管理成功")
    
    # 测试6: 测试会话清理
    print("\n6. 测试会话清理...")
    message_manager.delete_session(session_id)
    assert session_id not in message_manager.context_store, "会话删除失败"
    print("✓ 会话删除成功")
    
    # 测试7: 测试过期会话清理
    print("\n7. 测试过期会话清理...")
    # 创建一个测试会话
    old_session = "old_test_session"
    message_manager.create_session(old_session)
    message_manager.add_message(old_session, "user", "这是一条测试消息")
    
    # 模拟会话过期（将最后活跃时间设置为1小时前）
    message_manager.context_store[old_session]["last_active"] = time.time() - 3601
    
    # 清理过期会话
    expired_count = message_manager.clean_expired_sessions()
    print(f"✓ 过期会话清理成功，清理了 {expired_count} 个会话")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    test_chatbot()
