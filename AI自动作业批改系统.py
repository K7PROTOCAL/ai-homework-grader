#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易 AI 自动作业批改系统

依赖库：
pip install streamlit requests

运行命令：
streamlit run AI自动作业批改系统.py

配置说明：
1. 直接在代码中修改 API_KEY 变量为您的 DeepSeek API 密钥
"""

import streamlit as st
import json
import os
import time
import requests

# 设置页面配置
st.set_page_config(
    page_title="AI 自动作业批改系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)
# 配置API密钥
API_KEY = os.environ.get("API_KEY", "default_value")

# 获取脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储文件（使用绝对路径）
HOMEWORK_FILE = os.path.join(BASE_DIR, "homework_data.json")
SUBMISSION_FILE = os.path.join(BASE_DIR, "submission_data.json")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts_data.json")
DATABASE_FILE = os.path.join(BASE_DIR, "homework_system.db")

# 初始化SQLite数据库
def init_database():
    """初始化SQLite数据库"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # 创建账户表
    c.execute('''CREATE TABLE IF NOT EXISTS accounts
                 (id TEXT PRIMARY KEY, username TEXT, password TEXT, role TEXT, identifier TEXT, created_at TEXT)''')
    
    # 创建作业表
    c.execute('''CREATE TABLE IF NOT EXISTS homework
                 (id TEXT PRIMARY KEY, title TEXT, content TEXT, deadline TEXT, standard_answer TEXT, images TEXT, files TEXT, created_at TEXT, teacher_id TEXT, teacher_name TEXT)''')
    
    # 创建提交表
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id TEXT PRIMARY KEY, homework_id TEXT, homework_title TEXT, student_name TEXT, student_answer TEXT, grading_result TEXT, is_late INTEGER, submitted_at TEXT)''')
    
    # 创建好友关系表
    c.execute('''CREATE TABLE IF NOT EXISTS friend_relationships
                 (id TEXT PRIMARY KEY, sender_id TEXT, receiver_id TEXT, status TEXT, created_at TEXT)''')
    
    # 创建消息表
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id TEXT PRIMARY KEY, sender_id TEXT, receiver_id TEXT, content TEXT, status TEXT, created_at TEXT)''')
    
    # 检查是否需要初始化管理员账户
    c.execute("SELECT COUNT(*) FROM accounts WHERE role = '管理员'")
    if c.fetchone()[0] == 0:
        admin_account = (
            "admin", "管理员", "123456", "管理员", None, time.strftime("%Y-%m-%d %H:%M:%S")
        )
        c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)", admin_account)
    
    conn.commit()
    conn.close()

# 初始化数据文件（兼容旧数据）
def init_data_files():
    """初始化数据文件"""
    # 初始化SQLite数据库
    init_database()
    
    # 兼容旧数据 - 如果存在JSON文件，导入到数据库
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    
    # 导入账户数据
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        for account in accounts:
            c.execute("SELECT COUNT(*) FROM accounts WHERE id = ?", (account['id'],))
            if c.fetchone()[0] == 0:
                c.execute(
                    "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)",
                    (account['id'], account['username'], account['password'], account['role'], 
                     account.get('identifier'), account['created_at'])
                )
    
    # 导入作业数据
    if os.path.exists(HOMEWORK_FILE):
        with open(HOMEWORK_FILE, 'r', encoding='utf-8') as f:
            homework_list = json.load(f)
        for hw in homework_list:
            c.execute("SELECT COUNT(*) FROM homework WHERE id = ?", (hw['id'],))
            if c.fetchone()[0] == 0:
                c.execute(
                    "INSERT INTO homework VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (hw['id'], hw['title'], hw['content'], hw.get('deadline'), 
                     hw.get('standard_answer'), str(hw.get('images', [])), 
                     str(hw.get('files', [])), hw['created_at'], 
                     hw.get('teacher_id'), hw.get('teacher_name'))
                )
    
    # 导入提交数据
    if os.path.exists(SUBMISSION_FILE):
        with open(SUBMISSION_FILE, 'r', encoding='utf-8') as f:
            submissions = json.load(f)
        for sub in submissions:
            c.execute("SELECT COUNT(*) FROM submissions WHERE id = ?", (sub['id'],))
            if c.fetchone()[0] == 0:
                c.execute(
                    "INSERT INTO submissions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (sub['id'], sub['homework_id'], sub['homework_title'], 
                     sub['student_name'], sub['student_answer'], sub['grading_result'], 
                     1 if sub.get('is_late') else 0, sub['submitted_at'])
                )
    
    conn.commit()
    conn.close()

# 加载作业数据
def load_homework():
    """加载作业数据"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM homework ORDER BY created_at DESC")
    homework_list = []
    for row in c.fetchall():
        homework = dict(row)
        # 处理列表类型的字段
        try:
            homework['images'] = eval(homework['images']) if homework['images'] else []
        except:
            homework['images'] = []
        try:
            homework['files'] = eval(homework['files']) if homework['files'] else []
        except:
            homework['files'] = []
        homework_list.append(homework)
    conn.close()
    return homework_list

# 保存作业数据
def save_homework(homework_list):
    """保存作业数据"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # 清空表并重新插入（简单实现，实际应用中应该使用更高效的方法）
    c.execute("DELETE FROM homework")
    for hw in homework_list:
        c.execute(
            "INSERT INTO homework VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (hw['id'], hw['title'], hw['content'], hw.get('deadline'), 
             hw.get('standard_answer'), str(hw.get('images', [])), 
             str(hw.get('files', [])), hw['created_at'], 
             hw.get('teacher_id'), hw.get('teacher_name'))
        )
    conn.commit()
    conn.close()

# 加载提交数据
def load_submissions():
    """加载提交数据"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY submitted_at DESC")
    submission_list = []
    for row in c.fetchall():
        submission = dict(row)
        submission['is_late'] = bool(submission['is_late'])
        submission_list.append(submission)
    conn.close()
    return submission_list

# 保存提交数据
def save_submissions(submission_list):
    """保存提交数据"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # 清空表并重新插入
    c.execute("DELETE FROM submissions")
    for sub in submission_list:
        c.execute(
            "INSERT INTO submissions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (sub['id'], sub['homework_id'], sub['homework_title'], 
             sub['student_name'], sub['student_answer'], sub['grading_result'], 
             1 if sub.get('is_late') else 0, sub['submitted_at'])
        )
    conn.commit()
    conn.close()

# 加载账户数据
def load_accounts():
    """加载账户数据"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM accounts")
    accounts_list = []
    for row in c.fetchall():
        account = dict(row)
        accounts_list.append(account)
    conn.close()
    return accounts_list

# 保存账户数据
def save_accounts(accounts_list):
    """保存账户数据"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # 清空表并重新插入（保留管理员账户）
    c.execute("DELETE FROM accounts WHERE role != '管理员'")
    for account in accounts_list:
        if account['role'] != '管理员':
            c.execute(
                "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)",
                (account['id'], account['username'], account['password'], account['role'], 
                 account.get('identifier'), account['created_at'])
            )
    conn.commit()
    conn.close()

# 验证登录
def verify_login(username, password, role):
    """验证登录"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE username = ? AND password = ? AND role = ?", (username, password, role))
    account = c.fetchone()
    conn.close()
    if account:
        return True, dict(account)
    return False, None

# 注册账户
def register_account(username, password, role, identifier):
    """注册账户"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # 检查用户名是否已存在
    c.execute("SELECT COUNT(*) FROM accounts WHERE username = ? AND role = ?", (username, role))
    if c.fetchone()[0] > 0:
        conn.close()
        return False, "用户名已存在"
    # 创建新账户
    new_account = (
        str(int(time.time())), username, password, role, identifier, time.strftime("%Y-%m-%d %H:%M:%S")
    )
    c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)", new_account)
    conn.commit()
    conn.close()
    return True, "注册成功"

# 搜索用户
def search_users(keyword):
    """搜索用户"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE username LIKE ? AND role != '管理员'", ('%' + keyword + '%',))
    users = []
    for row in c.fetchall():
        user = dict(row)
        users.append(user)
    conn.close()
    return users

# 发送好友请求
def send_friend_request(sender_id, receiver_id):
    """发送好友请求"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # 检查是否已经是好友
    c.execute("SELECT COUNT(*) FROM friend_relationships WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)", (sender_id, receiver_id, receiver_id, sender_id))
    if c.fetchone()[0] > 0:
        conn.close()
        return False, "已经发送过好友请求或已经是好友"
    # 发送好友请求
    request_id = str(int(time.time()))
    c.execute("INSERT INTO friend_relationships VALUES (?, ?, ?, ?, ?)", (request_id, sender_id, receiver_id, "pending", time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return True, "好友请求已发送"

# 处理好友请求
def handle_friend_request(request_id, accept):
    """处理好友请求"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    if accept:
        c.execute("UPDATE friend_relationships SET status = 'accepted' WHERE id = ?", (request_id,))
        conn.commit()
        conn.close()
        return True, "好友请求已接受"
    else:
        c.execute("DELETE FROM friend_relationships WHERE id = ?", (request_id,))
        conn.commit()
        conn.close()
        return True, "好友请求已拒绝"

# 获取好友列表
def get_friends(user_id):
    """获取好友列表"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # 查询已接受的好友关系
    c.execute('''
        SELECT a.* FROM accounts a
        JOIN friend_relationships fr ON (a.id = fr.sender_id OR a.id = fr.receiver_id)
        WHERE (fr.sender_id = ? OR fr.receiver_id = ?) AND fr.status = 'accepted' AND a.id != ?
    ''', (user_id, user_id, user_id))
    friends = []
    for row in c.fetchall():
        friend = dict(row)
        friends.append(friend)
    conn.close()
    return friends

# 获取好友请求
def get_friend_requests(user_id):
    """获取好友请求"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # 查询发送给用户的待处理好友请求
    c.execute('''
        SELECT fr.*, a.username, a.role FROM friend_relationships fr
        JOIN accounts a ON fr.sender_id = a.id
        WHERE fr.receiver_id = ? AND fr.status = 'pending'
    ''', (user_id,))
    requests = []
    for row in c.fetchall():
        request = dict(row)
        requests.append(request)
    conn.close()
    return requests

# 发送消息
def send_message(sender_id, receiver_id, content):
    """发送消息"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # 检查是否是好友
    c.execute('''
        SELECT COUNT(*) FROM friend_relationships
        WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)) AND status = 'accepted'
    ''', (sender_id, receiver_id, receiver_id, sender_id))
    if c.fetchone()[0] == 0:
        conn.close()
        return False, "只有好友才能发送消息"
    # 发送消息
    message_id = str(int(time.time()))
    c.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)", (message_id, sender_id, receiver_id, content, "unread", time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return True, "消息已发送"

# 获取消息
def get_messages(user_id, friend_id):
    """获取与好友的消息记录"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # 查询两人之间的消息
    c.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY created_at ASC
    ''', (user_id, friend_id, friend_id, user_id))
    messages = []
    for row in c.fetchall():
        message = dict(row)
        messages.append(message)
    # 将消息标记为已读
    c.execute("UPDATE messages SET status = 'read' WHERE receiver_id = ? AND sender_id = ?", (user_id, friend_id))
    conn.commit()
    conn.close()
    return messages

# 获取未读消息数量
def get_unread_message_count(user_id):
    """获取未读消息数量"""
    import sqlite3
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND status = 'unread'", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

# AI批改函数
def grade_homework(homework_title, student_answer, standard_answer=None):
    """使用AI批改作业"""
    # 检查API密钥
    if API_KEY == "your_deepseek_api_key_here":
        return "批改失败：请配置有效的DeepSeek API密钥"
    
    try:
        # 构建提示词
        prompt = f"""你是一位严厉但公正的老师，负责批改学生作业。

请根据以下信息对学生的作业进行批改：

作业题目：{homework_title}
{"标准答案：" + standard_answer if standard_answer else ""}
学生答案：{student_answer}

请按照以下格式输出批改结果：
1. 分数：0-100之间的整数
2. 评语：详细的批改意见，包括正确的部分和需要改进的地方
3. 建议：针对学生的不足之处给出具体的改进建议

请注意：
- 评分要严格公正，根据答案的准确性、完整性和逻辑性进行评估
- 评语要具体，指出学生的优点和缺点
- 建议要实用，帮助学生提高
"""
        
        # DeepSeek API 调用
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一位专业的教师，擅长批改作业并给出详细的反馈。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析响应
        result = response.json()['choices'][0]['message']['content']
        return result
    except Exception as e:
        return f"批改失败：{str(e)}"

# 主函数
def main():
    """主函数"""
    # 初始化数据文件
    init_data_files()
    
    # 添加自定义CSS和JavaScript
    st.markdown("""
    <style>
    /* 全局样式 */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    :root {
        --primary-color: #4361ee;
        --secondary-color: #3f37c9;
        --accent-color: #4cc9f0;
        --success-color: #4ade80;
        --warning-color: #fbbf24;
        --error-color: #f87171;
        --info-color: #60a5fa;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --border-radius-sm: 0.375rem;
        --border-radius-md: 0.5rem;
        --border-radius-lg: 0.75rem;
        --border-radius-xl: 1rem;
        --transition: all 0.3s ease;
    }
    
    .main {
        background-color: var(--background-color);
        background-image: radial-gradient(circle at 10% 20%, rgba(67, 97, 238, 0.05) 0%, rgba(76, 201, 240, 0.05) 90%);
        font-family: 'Inter', sans-serif;
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: var(--border-radius-md);
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        border-radius: var(--border-radius-md);
        border: 1px solid var(--border-color);
        padding: 0.5rem;
        transition: var(--transition);
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
    }
    
    /* 右键菜单样式 */
    .context-menu {
        position: fixed;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        display: none;
    }
    
    .context-menu-item {
        padding: 8px 16px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .context-menu-item:hover {
        background-color: #f1f5f9;
    }
    
    .context-menu-item.delete {
        color: #f87171;
    }
    
    /* 消息框样式 */
    .success-box {
        background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(74, 222, 128, 0.05));
        border-left: 4px solid var(--success-color);
        padding: 1rem;
        border-radius: var(--border-radius-md);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(248, 113, 113, 0.1), rgba(248, 113, 113, 0.05));
        border-left: 4px solid var(--error-color);
        padding: 1rem;
        border-radius: var(--border-radius-md);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(96, 165, 250, 0.05));
        border-left: 4px solid var(--info-color);
        padding: 1rem;
        border-radius: var(--border-radius-md);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: var(--card-background) !important;
        border-right: 1px solid var(--border-color);
    }
    
    /* 分隔线样式 */
    .css-1wrcr25 {
        background-color: var(--border-color) !important;
    }
    
    /* 加载动画 */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .pulse {
        animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .card {
            padding: 1rem;
        }
        
        h1 {
            font-size: 1.75rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
    }
    </style>
    
    <script>
    // 右键菜单功能
    document.addEventListener('DOMContentLoaded', function() {
        // 创建右键菜单
        const contextMenu = document.createElement('div');
        contextMenu.className = 'context-menu';
        contextMenu.id = 'contextMenu';
        
        const deleteItem = document.createElement('div');
        deleteItem.className = 'context-menu-item delete';
        deleteItem.textContent = '删除记录';
        contextMenu.appendChild(deleteItem);
        
        document.body.appendChild(contextMenu);
        
        // 存储当前点击的元素信息
        let currentSubmissionId = null;
        
        // 为提交记录卡片添加右键事件
        document.addEventListener('contextmenu', function(e) {
            // 检查是否点击在提交记录卡片上
            const submissionCard = e.target.closest('.submission-card');
            if (submissionCard) {
                e.preventDefault();
                
                // 获取提交ID
                const idElement = submissionCard.querySelector('[data-submission-id]');
                if (idElement) {
                    currentSubmissionId = idElement.getAttribute('data-submission-id');
                }
                
                // 显示右键菜单
                contextMenu.style.left = e.pageX + 'px';
                contextMenu.style.top = e.pageY + 'px';
                contextMenu.style.display = 'block';
            }
        });
        
        // 点击其他地方关闭菜单
        document.addEventListener('click', function(e) {
            if (!contextMenu.contains(e.target)) {
                contextMenu.style.display = 'none';
                currentSubmissionId = null;
            }
        });
        
        // 点击删除选项
        deleteItem.addEventListener('click', function() {
            if (currentSubmissionId) {
                // 创建一个隐藏的表单来处理删除
                const form = document.createElement('form');
                form.method = 'post';
                form.action = '';
                form.style.display = 'none';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'delete_submission';
                input.value = currentSubmissionId;
                form.appendChild(input);
                
                document.body.appendChild(form);
                form.submit();
            }
            contextMenu.style.display = 'none';
        });
    });
    </script>
    """, unsafe_allow_html=True)
    
    # 初始化会话状态
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'role' not in st.session_state:
        st.session_state.role = "教师"
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'selected_homework' not in st.session_state:
        st.session_state.selected_homework = ""
    
    # 登录页面
    if not st.session_state.logged_in:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #4361ee, #4cc9f0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                📝 AI 自动作业批改系统
            </h1>
            <p style="font-size: 1.2rem; color: var(--text-secondary); font-weight: 400;">
                智能批改，高效教学
            </p>
            <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #4361ee, #4cc9f0); border-radius: 2px; margin: 1rem auto;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 选择角色
        st.subheader("请选择角色")
        role = st.selectbox("角色", ["教师", "学生", "管理员"])
        
        # 登录/注册选项卡
        tab1, tab2 = st.tabs(["登录", "注册"])
        
        with tab1:
            st.markdown("**登录账户**")
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            
            if st.button("登录"):
                success, account = verify_login(username, password, role)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.role = role
                    st.session_state.username = username
                    st.session_state.user_id = account['id']  # 设置用户ID
                    st.session_state.student_name = username  # 学生姓名使用用户名
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        
        with tab2:
            st.markdown("**注册新账户**")
            new_username = st.text_input("真实姓名")
            new_password = st.text_input("设置密码", type="password")
            confirm_password = st.text_input("确认密码", type="password")
            
            if role == "学生":
                identifier = st.text_input("学号")
            elif role == "教师":
                identifier = st.text_input("工号")
            else:  # 管理员
                st.warning("管理员账户已预设，无需注册")
                identifier = ""
            
            if st.button("注册"):
                if role == "管理员":
                    st.error("管理员账户已预设，无需注册")
                elif new_password != confirm_password:
                    st.error("两次输入的密码不一致")
                elif not new_username or not new_password or not identifier:
                    st.error("请填写完整信息")
                else:
                    success, message = register_account(new_username, new_password, role, identifier)
                    if success:
                        st.success("注册成功！请登录")
                    else:
                        st.error(message)
        
        return  # 登录页面结束
    
    # 已登录，显示系统标题
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #4361ee, #4cc9f0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            📝 AI 自动作业批改系统
        </h1>
        <p style="font-size: 1.2rem; color: var(--text-secondary); font-weight: 400;">
            智能批改，高效教学
        </p>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #4361ee, #4cc9f0); border-radius: 2px; margin: 1rem auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    # 侧边栏美化
    with st.sidebar:
        st.markdown("<h3 class='header'>系统导航</h3>", unsafe_allow_html=True)
        
        # 显示登录信息
        st.markdown(f"**当前用户：** {st.session_state.username}")
        st.markdown(f"**角色：** {st.session_state.role}")
        
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.role = "教师"
            st.session_state.username = ""
            st.session_state.user_id = ""
            st.session_state.student_name = ""
            st.rerun()
        
        st.divider()
        st.markdown("<small>© 2026 AI 自动作业批改系统</small>", unsafe_allow_html=True)
    
    if st.session_state.role == "教师":
        # 教师端功能
        st.header("👨‍🏫 教师端")
        
        # 创建上传目录
        UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        
        # 标签页布局
        tab1, tab2, tab3 = st.tabs(["发布作业", "提交记录", "消息中心"])
        
        with tab1:
            # 发布作业
            st.subheader("📤 发布作业")
            with st.container():
                homework_title = st.text_input("📌 作业题目", placeholder="请输入作业标题")
                
                # 使用选项卡布局
                tab1_1, tab1_2, tab1_3 = st.tabs(["📝 文字内容", "🖼️ 图片上传", "📎 文件上传"])
                
                with tab1_1:
                    homework_content = st.text_area("作业内容", placeholder="请输入作业详细内容", height=200)
                    standard_answer = st.text_area("📖 标准答案（可选）", placeholder="请输入标准答案（可选）", height=150)
                
                with tab1_2:
                    st.markdown("**上传题目图片（支持 JPG, PNG, GIF）**")
                    uploaded_images = st.file_uploader(
                        "拖拽或点击上传图片",
                        type=['jpg', 'jpeg', 'png', 'gif'],
                        accept_multiple_files=True,
                        help="支持上传多张图片，每张图片大小不超过200MB"
                    )
                    if uploaded_images:
                        st.success(f"已上传 {len(uploaded_images)} 张图片")
                        # 预览上传的图片
                        if len(uploaded_images) <= 3:
                            cols = st.columns(len(uploaded_images))
                            for i, img in enumerate(uploaded_images):
                                with cols[i]:
                                    st.image(img, caption=img.name, width=150)
                        else:
                            cols = st.columns(3)
                            for i, img in enumerate(uploaded_images[:3]):
                                with cols[i]:
                                    st.image(img, caption=img.name, width=150)
                            st.info(f"还有 {len(uploaded_images) - 3} 张图片未预览")
                
                with tab1_3:
                    st.markdown("**上传题目相关文件（支持 PDF, DOCX, TXT 等）**")
                    uploaded_files = st.file_uploader(
                        "拖拽或点击上传文件",
                        type=['pdf', 'docx', 'doc', 'txt', 'xlsx', 'xls', 'pptx', 'ppt'],
                        accept_multiple_files=True,
                        help="支持上传多个文件，每个文件大小不超过200MB"
                    )
                    if uploaded_files:
                        st.success(f"已上传 {len(uploaded_files)} 个文件")
                        for file in uploaded_files:
                            file_size = len(file.getvalue()) / 1024 / 1024  # MB
                            st.write(f"📄 {file.name} ({file_size:.2f} MB)")
                
                # 截止时间设置
                st.markdown("**⏰ 截止时间**")
                deadline = st.datetime_input("设置作业提交的截止时间（可选）", help="超过截止时间提交的作业将被标记为未交")
                
                st.divider()
                
                if st.button("🚀 发布作业", use_container_width=True, type="primary"):
                    if homework_title and homework_content:
                        # 加载现有作业
                        homework_list = load_homework()
                        
                        # 处理上传的图片
                        image_paths = []
                        if uploaded_images:
                            for img in uploaded_images:
                                img_path = os.path.join(UPLOAD_DIR, f"hw_{int(time.time())}_{img.name}")
                                with open(img_path, "wb") as f:
                                    f.write(img.getvalue())
                                image_paths.append(img_path)
                        
                        # 处理上传的文件
                        file_paths = []
                        if uploaded_files:
                            for file in uploaded_files:
                                file_path = os.path.join(UPLOAD_DIR, f"hw_{int(time.time())}_{file.name}")
                                with open(file_path, "wb") as f:
                                    f.write(file.getvalue())
                                file_paths.append(file_path)
                        
                        # 处理截止时间
                        deadline_str = None
                        if deadline:
                            deadline_str = deadline.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 创建新作业
                        new_homework = {
                            "id": str(int(time.time())),
                            "title": homework_title,
                            "content": homework_content,
                            "deadline": deadline_str,
                            "standard_answer": standard_answer,
                            "images": image_paths,
                            "files": file_paths,
                            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # 添加到作业列表
                        homework_list.append(new_homework)
                        save_homework(homework_list)
                        
                        st.markdown('<div class="success-box">🎉 作业发布成功！</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-box">⚠️ 请填写作业题目和内容</div>', unsafe_allow_html=True)
        
        with tab2:
            # 查看作业提交记录
            st.subheader("📋 作业提交记录")
            submissions = load_submissions()
            
            if submissions:
                # 添加统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总提交数", len(submissions))
                with col2:
                    unique_students = len(set([s['student_name'] for s in submissions]))
                    st.metric("学生人数", unique_students)
                with col3:
                    unique_homeworks = len(set([s['homework_title'] for s in submissions]))
                    st.metric("作业数量", unique_homeworks)
                
                st.divider()
                
                # 使用折叠卡片显示提交记录
                for i, submission in enumerate(submissions):
                    # 创建简洁的卡片标题
                    late_tag = " ⚠️ 逾期" if 'is_late' in submission and submission['is_late'] else ""
                    card_title = f"📄 {submission['homework_title']} | {submission['student_name']} | {submission['submitted_at']}{late_tag}"
                    
                    with st.expander(card_title, expanded=False):
                        st.markdown(f"<div data-submission-id='{submission['id']}'></div>", unsafe_allow_html=True)
                        st.markdown("---")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown("**📝 学生答案：**")
                            st.info(submission['student_answer'])
                        with col2:
                            st.markdown("**✅ AI 批改结果：**")
                            st.success(submission['grading_result'])
                        
                        # 添加删除按钮
                        if st.button(f"删除记录 {i+1}", key=f"delete_{submission['id']}"):
                            submissions.pop(i)
                            save_submissions(submissions)
                            st.success("记录已删除")
                            st.rerun()
            else:
                st.markdown("""
                <div class="info-box">
                    <p>暂无提交记录</p>
                    <small>当学生提交作业后，这里将显示批改结果</small>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            # 消息中心
            st.subheader("消息中心")
            
            # 标签页
            tab3_1, tab3_2, tab3_3 = st.tabs(["聊天", "好友请求", "添加好友"])
            
            with tab3_1:
                # 聊天界面
                st.subheader("聊天")
                friends = get_friends(st.session_state.user_id)
                
                if friends:
                    # 选择好友
                    friend_names = [f"{friend['username']} ({friend['role']})" for friend in friends]
                    selected_friend_idx = st.selectbox("选择好友", range(len(friend_names)), format_func=lambda x: friend_names[x])
                    selected_friend = friends[selected_friend_idx]
                    
                    # 显示聊天记录
                    st.subheader(f"与 {selected_friend['username']} 聊天")
                    messages = get_messages(st.session_state.user_id, selected_friend['id'])
                    
                    # 聊天记录容器
                    chat_container = st.container()
                    with chat_container:
                        for msg in messages:
                            if msg['sender_id'] == st.session_state.user_id:
                                st.markdown(f"**我**：{msg['content']}")
                            else:
                                st.markdown(f"**{selected_friend['username']}**：{msg['content']}")
                            st.markdown(f"*发送时间：{msg['created_at']}*")
                            st.markdown("---")
                    
                    # 发送消息
                    message_content = st.text_area("输入消息", placeholder="请输入消息内容")
                    if st.button("发送", use_container_width=True):
                        if message_content:
                            success, msg = send_message(st.session_state.user_id, selected_friend['id'], message_content)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                else:
                    st.info("暂无好友，请先添加好友")
            
            with tab3_2:
                # 好友请求
                st.subheader("好友请求")
                requests = get_friend_requests(st.session_state.user_id)
                
                if requests:
                    for req in requests:
                        with st.expander(f"{req['username']} ({req['role']}) 的好友请求"):
                            st.markdown(f"*发送时间：{req['created_at']}*")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("接受", key=f"accept_{req['id']}"):
                                    success, msg = handle_friend_request(req['id'], True)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                            with col2:
                                if st.button("拒绝", key=f"reject_{req['id']}"):
                                    success, msg = handle_friend_request(req['id'], False)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                else:
                    st.info("暂无好友请求")
            
            with tab3_3:
                # 添加好友
                st.subheader("添加好友")
                search_keyword = st.text_input("搜索用户", placeholder="输入用户名搜索")
                if search_keyword:
                    users = search_users(search_keyword)
                    if users:
                        for user in users:
                            if user['id'] != st.session_state.user_id:
                                with st.expander(f"{user['username']} ({user['role']})"):
                                    st.markdown(f"**角色：** {user['role']}")
                                    if 'identifier' in user and user['identifier']:
                                        st.markdown(f"**{ '学号' if user['role'] == '学生' else '工号' }：** {user['identifier']}")
                                    if st.button(f"发送好友请求", key=f"add_{user['id']}"):
                                        success, msg = send_friend_request(st.session_state.user_id, user['id'])
                                        if success:
                                            st.success(msg)
                                        else:
                                            st.error(msg)
                    else:
                        st.info("未找到匹配的用户")
    
    elif st.session_state.role == "学生":
        # 学生端功能
        st.header("👨‍🎓 学生端")
        
        # 学生信息
        st.subheader("个人信息")
        with st.container():
            student_name = st.text_input("请输入你的姓名", value=st.session_state.student_name, key="student_name", placeholder="请输入你的真实姓名")
        
        # 标签页布局
        tab1, tab2, tab3 = st.tabs(["当前作业", "历史记录", "消息中心"])
        
        with tab1:
            # 查看当前作业
            st.subheader("当前作业")
            homework_list = load_homework()
            
            if homework_list:
                with st.container():
                    # 获取作业标题列表
                    homework_titles = [hw["title"] for hw in homework_list]
                    
                    # 找到上次选择的作业索引
                    if st.session_state.selected_homework in homework_titles:
                        index = homework_titles.index(st.session_state.selected_homework)
                    else:
                        index = 0
                    
                    selected_homework = st.selectbox(
                        "选择要完成的作业",
                        homework_titles,
                        index=index,
                        key="selected_homework",
                        help="选择你要完成的作业"
                    )
                    
                    # 显示作业详情
                    for hw in homework_list:
                        if hw["title"] == selected_homework:
                            selected_homework_id = hw["id"]
                            selected_homework_title = hw["title"]
                            selected_standard_answer = hw["standard_answer"]
                            
                            # 使用选项卡显示不同内容
                            tab1_1, tab1_2, tab1_3 = st.tabs(["📝 作业内容", "🖼️ 图片资料", "📎 相关文件"])
                            
                            with tab1_1:
                                st.markdown("**作业内容：**")
                                st.info(hw['content'])
                                # 显示截止时间
                                if 'deadline' in hw and hw['deadline']:
                                    st.markdown(f"**⏰ 截止时间：** {hw['deadline']}")
                                    # 检查是否已超过截止时间
                                    import datetime
                                    deadline_time = datetime.datetime.strptime(hw['deadline'], "%Y-%m-%d %H:%M:%S")
                                    current_time = datetime.datetime.now()
                                    if current_time > deadline_time:
                                        st.error("⚠️ 此作业已超过截止时间！")
                            
                            with tab1_2:
                                if 'images' in hw and hw['images'] and len(hw['images']) > 0:
                                    st.markdown(f"**共 {len(hw['images'])} 张图片：**")
                                    cols = st.columns(2)
                                    for i, img_path in enumerate(hw['images']):
                                        with cols[i % 2]:
                                            try:
                                                st.image(img_path, caption=f"图片 {i+1}", use_container_width=True)
                                            except Exception as e:
                                                st.error(f"无法加载文件 {i+1}")
                                else:
                                    st.info("暂无图片资料")
                            
                            with tab1_3:
                                if 'files' in hw and hw['files'] and len(hw['files']) > 0:
                                    st.markdown(f"**共 {len(hw['files'])} 个文件：**")
                                    for i, file_path in enumerate(hw['files']):
                                        try:
                                            file_name = os.path.basename(file_path)
                                            with open(file_path, "rb") as f:
                                                st.download_button(
                                                    label=f"📥 下载 {file_name}",
                                                    data=f,
                                                    file_name=file_name,
                                                    key=f"file_{i}"
                                                )
                                        except Exception as e:
                                            st.error(f"无法加载文件 {i+1}")
                                else:
                                    st.info("暂无相关文件")
                            break
                    
                    # 提交作业
                    st.write("\n**提交作业：**")
                    student_answer = st.text_area("请输入你的答案", placeholder="请在此输入你的答案", height=200)
                    
                    if st.button("提交作业", use_container_width=True):
                        if student_name and student_answer:
                            # 检查是否超过截止时间
                            is_late = False
                            if 'deadline' in hw and hw['deadline']:
                                import datetime
                                deadline_time = datetime.datetime.strptime(hw['deadline'], "%Y-%m-%d %H:%M:%S")
                                current_time = datetime.datetime.now()
                                if current_time > deadline_time:
                                    is_late = True
                                    st.warning("⚠️ 你已超过截止时间提交作业，将被标记为未交")
                            
                            # 批改作业
                            with st.spinner("正在批改作业，请稍候..."):
                                grading_result = grade_homework(
                                    selected_homework_title,
                                    student_answer,
                                    selected_standard_answer
                                )
                            
                            # 保存提交记录
                            submissions = load_submissions()
                            new_submission = {
                                "id": str(int(time.time())),
                                "homework_id": selected_homework_id,
                                "homework_title": selected_homework_title,
                                "student_name": student_name,
                                "student_answer": student_answer,
                                "grading_result": grading_result,
                                "is_late": is_late,
                                "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            submissions.append(new_submission)
                            save_submissions(submissions)
                            
                            st.markdown('<div class="success-box">作业提交成功！</div>', unsafe_allow_html=True)
                            st.write("**批改结果：**")
                            st.success(grading_result)
                        else:
                            st.markdown('<div class="error-box">请输入姓名和答案</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">当前暂无作业</div>', unsafe_allow_html=True)
        
        with tab2:
            # 查看历史提交记录
            st.subheader("📚 历史提交记录")
            submissions = load_submissions()
            
            # 只有输入了姓名才显示历史记录
            if student_name and student_name.strip():
                if submissions:
                    student_submissions = [s for s in submissions if s['student_name'] == student_name]
                    if student_submissions:
                        # 添加统计信息
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("我的提交数", len(student_submissions))
                        with col2:
                            st.metric("我的作业数", len(set([s['homework_title'] for s in student_submissions])))
                        
                        st.divider()
                        
                        # 使用折叠卡片显示提交记录
                        for i, submission in enumerate(student_submissions):
                            # 创建简洁的卡片标题
                            card_title = f"📄 {submission['homework_title']} | {submission['submitted_at']}"
                            
                            with st.expander(card_title, expanded=False):
                                st.markdown("---")
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.markdown("**📝 我的答案：**")
                                    st.info(submission['student_answer'])
                                with col2:
                                    st.markdown("**✅ AI 批改结果：**")
                                    st.success(submission['grading_result'])
                                
                                # 添加删除按钮
                                if st.button(f"删除记录 {i+1}", key=f"delete_student_{submission['id']}"):
                                    submissions = load_submissions()
                                    # 找到要删除的记录索引
                                    for j, sub in enumerate(submissions):
                                        if sub['id'] == submission['id']:
                                            submissions.pop(j)
                                            save_submissions(submissions)
                                            st.success("记录已删除")
                                            st.rerun()
                                            break
                    else:
                        st.markdown("""
                        <div class="info-box">
                            <p>暂无提交记录</p>
                            <small>你还没有提交过任何作业</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="info-box">
                        <p>暂无提交记录</p>
                        <small>当有学生提交作业后，这里将显示提交记录</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    <p>请先输入你的姓名</p>
                    <small>输入姓名后即可查看历史提交记录</small>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            # 消息中心
            st.subheader("消息中心")
            
            # 标签页
            tab3_1, tab3_2, tab3_3 = st.tabs(["聊天", "好友请求", "添加好友"])
            
            with tab3_1:
                # 聊天界面
                st.subheader("聊天")
                friends = get_friends(st.session_state.user_id)
                
                if friends:
                    # 选择好友
                    friend_names = [f"{friend['username']} ({friend['role']})" for friend in friends]
                    selected_friend_idx = st.selectbox("选择好友", range(len(friend_names)), format_func=lambda x: friend_names[x])
                    selected_friend = friends[selected_friend_idx]
                    
                    # 显示聊天记录
                    st.subheader(f"与 {selected_friend['username']} 聊天")
                    messages = get_messages(st.session_state.user_id, selected_friend['id'])
                    
                    # 聊天记录容器
                    chat_container = st.container()
                    with chat_container:
                        for msg in messages:
                            if msg['sender_id'] == st.session_state.user_id:
                                st.markdown(f"**我**：{msg['content']}")
                            else:
                                st.markdown(f"**{selected_friend['username']}**：{msg['content']}")
                            st.markdown(f"*发送时间：{msg['created_at']}*")
                            st.markdown("---")
                    
                    # 发送消息
                    message_content = st.text_area("输入消息", placeholder="请输入消息内容")
                    if st.button("发送", use_container_width=True):
                        if message_content:
                            success, msg = send_message(st.session_state.user_id, selected_friend['id'], message_content)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                else:
                    st.info("暂无好友，请先添加好友")
            
            with tab3_2:
                # 好友请求
                st.subheader("好友请求")
                requests = get_friend_requests(st.session_state.user_id)
                
                if requests:
                    for req in requests:
                        with st.expander(f"{req['username']} ({req['role']}) 的好友请求"):
                            st.markdown(f"*发送时间：{req['created_at']}*")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("接受", key=f"accept_{req['id']}"):
                                    success, msg = handle_friend_request(req['id'], True)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                            with col2:
                                if st.button("拒绝", key=f"reject_{req['id']}"):
                                    success, msg = handle_friend_request(req['id'], False)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                else:
                    st.info("暂无好友请求")
            
            with tab3_3:
                # 添加好友
                st.subheader("添加好友")
                search_keyword = st.text_input("搜索用户", placeholder="输入用户名搜索")
                if search_keyword:
                    users = search_users(search_keyword)
                    if users:
                        for user in users:
                            if user['id'] != st.session_state.user_id:
                                with st.expander(f"{user['username']} ({user['role']})"):
                                    st.markdown(f"**角色：** {user['role']}")
                                    if 'identifier' in user and user['identifier']:
                                        st.markdown(f"**{ '学号' if user['role'] == '学生' else '工号' }：** {user['identifier']}")
                                    if st.button(f"发送好友请求", key=f"add_{user['id']}"):
                                        success, msg = send_friend_request(st.session_state.user_id, user['id'])
                                        if success:
                                            st.success(msg)
                                        else:
                                            st.error(msg)
                    else:
                        st.info("未找到匹配的用户")
    elif st.session_state.role == "管理员":
        # 管理员端功能
        st.header("👑 管理员端")
        
        # 标签页布局
        tab1, tab2, tab3 = st.tabs(["账户管理", "作业提交记录", "系统统计"])
        
        with tab1:
            # 查看所有账户
            st.subheader("账户管理")
            accounts = load_accounts()
            
            if accounts:
                st.markdown(f"**总账户数：** {len(accounts)}")
                
                # 按角色分组显示
                roles = {"管理员": [], "教师": [], "学生": []}
                for account in accounts:
                    if account['role'] in roles:
                        roles[account['role']].append(account)
                
                # 显示不同角色的账户
                for role, role_accounts in roles.items():
                    if role_accounts:
                        st.markdown(f"### {role}账户")
                        for account in role_accounts:
                            with st.expander(f"{account['username']} ({account.get('identifier', '无')})"):
                                st.markdown(f"**ID：** {account['id']}")
                                st.markdown(f"**用户名：** {account['username']}")
                                if 'identifier' in account:
                                    st.markdown(f"**{ '学号' if role == '学生' else '工号' }：** {account['identifier']}")
                                st.markdown(f"**创建时间：** {account['created_at']}")
                                # 添加删除按钮（除了管理员账户）
                                if role != "管理员":
                                    if st.button(f"删除{role}账户", key=f"delete_account_{account['id']}"):
                                        account_id = account['id']
                                        accounts = [acc for acc in accounts if acc['id'] != account_id]
                                        save_accounts(accounts)
                                        st.success(f"{role}账户已删除")
                                        st.rerun()
            else:
                st.info("暂无账户")
        
        with tab2:
            # 查看所有作业提交记录
            st.subheader("作业提交记录")
            submissions = load_submissions()
            homework_list = load_homework()
            
            if submissions:
                st.markdown(f"**总提交数：** {len(submissions)}")
                
                # 按作业分组显示
                homework_submissions = {}
                for submission in submissions:
                    hw_title = submission['homework_title']
                    if hw_title not in homework_submissions:
                        homework_submissions[hw_title] = []
                    homework_submissions[hw_title].append(submission)
                
                # 显示每个作业的提交记录
                for hw_title, hw_submissions in homework_submissions.items():
                    st.markdown(f"### {hw_title}")
                    for submission in hw_submissions:
                        late_tag = " ⚠️ 逾期" if 'is_late' in submission and submission['is_late'] else ""
                        with st.expander(f"{submission['student_name']} | {submission['submitted_at']}{late_tag}"):
                            st.markdown(f"<div data-submission-id='{submission['id']}'></div>", unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown(f"**提交ID：** {submission['id']}")
                            st.markdown(f"**学生姓名：** {submission['student_name']}")
                            st.markdown(f"**提交时间：** {submission['submitted_at']}")
                            st.markdown("**学生答案：**")
                            st.info(submission['student_answer'])
                            st.markdown("**AI 批改结果：**")
                            st.success(submission['grading_result'])
                            # 添加删除按钮
                            if st.button(f"删除记录", key=f"admin_delete_{submission['id']}"):
                                submission_id = submission['id']
                                submissions = [sub for sub in submissions if sub['id'] != submission_id]
                                save_submissions(submissions)
                                st.success("记录已删除")
                                st.rerun()
            else:
                st.info("暂无提交记录")
        
        with tab3:
            # 查看系统统计
            st.subheader("系统统计")
            homework_list = load_homework()
            submissions = load_submissions()
            accounts = load_accounts()
            
            # 按角色统计账户数量
            role_counts = {"管理员": 0, "教师": 0, "学生": 0}
            for account in accounts:
                if account['role'] in role_counts:
                    role_counts[account['role']] += 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("作业数量", len(homework_list))
            with col2:
                st.metric("提交记录", len(submissions))
            with col3:
                st.metric("账户数量", len(accounts))
            
            # 显示角色分布
            st.markdown("### 账户角色分布")
            for role, count in role_counts.items():
                st.write(f"{role}：{count} 个")

if __name__ == "__main__":
    main()
