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
API_KEY = "sk-799a856d82094530a874c97496c79506"

# 获取脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储文件（使用绝对路径）
HOMEWORK_FILE = os.path.join(BASE_DIR, "homework_data.json")
SUBMISSION_FILE = os.path.join(BASE_DIR, "submission_data.json")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts_data.json")

# 初始化数据文件
def init_data_files():
    """初始化数据文件"""
    if not os.path.exists(HOMEWORK_FILE):
        with open(HOMEWORK_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(SUBMISSION_FILE):
        with open(SUBMISSION_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(ACCOUNTS_FILE):
        # 初始化管理员账户
        admin_account = {
            "id": "admin",
            "username": "管理员",
            "password": "123456",
            "role": "管理员",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([admin_account], f, ensure_ascii=False, indent=2)

# 加载作业数据
def load_homework():
    """加载作业数据"""
    with open(HOMEWORK_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存作业数据
def save_homework(homework_list):
    """保存作业数据"""
    with open(HOMEWORK_FILE, 'w', encoding='utf-8') as f:
        json.dump(homework_list, f, ensure_ascii=False, indent=2)

# 加载提交数据
def load_submissions():
    """加载提交数据"""
    with open(SUBMISSION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存提交数据
def save_submissions(submission_list):
    """保存提交数据"""
    with open(SUBMISSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(submission_list, f, ensure_ascii=False, indent=2)

# 加载账户数据
def load_accounts():
    """加载账户数据"""
    with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存账户数据
def save_accounts(accounts_list):
    """保存账户数据"""
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts_list, f, ensure_ascii=False, indent=2)

# 验证登录
def verify_login(username, password, role):
    """验证登录"""
    accounts = load_accounts()
    for account in accounts:
        if account['username'] == username and account['password'] == password and account['role'] == role:
            return True, account
    return False, None

# 注册账户
def register_account(username, password, role, identifier):
    """注册账户"""
    accounts = load_accounts()
    # 检查用户名是否已存在
    for account in accounts:
        if account['username'] == username and account['role'] == role:
            return False, "用户名已存在"
    # 创建新账户
    new_account = {
        "id": str(int(time.time())),
        "username": username,
        "password": password,
        "role": role,
        "identifier": identifier,  # 学号或工号
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    accounts.append(new_account)
    save_accounts(accounts)
    return True, "注册成功"

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
        
        # 发布作业
        st.subheader("📤 发布作业")
        with st.container():
            homework_title = st.text_input("📌 作业题目", placeholder="请输入作业标题")
            
            # 使用选项卡布局
            tab1, tab2, tab3 = st.tabs(["📝 文字内容", "🖼️ 图片上传", "📎 文件上传"])
            
            with tab1:
                homework_content = st.text_area("作业内容", placeholder="请输入作业详细内容", height=200)
                standard_answer = st.text_area("📖 标准答案（可选）", placeholder="请输入标准答案（可选）", height=150)
            
            with tab2:
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
            
            with tab3:
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
    
    elif st.session_state.role == "学生":
        # 学生端功能
        st.header("👨‍🎓 学生端")
        
        # 学生信息
        st.subheader("个人信息")
        with st.container():
            student_name = st.text_input("请输入你的姓名", value=st.session_state.student_name, key="student_name", placeholder="请输入你的真实姓名")
        
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
                        tab1, tab2, tab3 = st.tabs(["📝 作业内容", "🖼️ 图片资料", "📎 相关文件"])
                        
                        with tab1:
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
                        
                        with tab2:
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
                        
                        with tab3:
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
                <p>请先输入姓名</p>
                <small>在页面顶部输入你的姓名后，即可查看历史提交记录</small>
            </div>
            """, unsafe_allow_html=True)
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
                                        accounts = [acc for acc in accounts if acc['id'] != account['id']]
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
                                submissions = [sub for sub in submissions if sub['id'] != submission['id']]
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
