import streamlit as st

# 假设你的核心逻辑在 ASK.py 里，或者你可以直接把函数复制过来
# from ASK import get_answer

# --- 页面配置 ---
st.set_page_config(page_title="设备维修助手", page_icon="🛠️")
st.title("🛠️ 工业设备维修助手")
st.caption("基于 RAG 技术的智能问答系统")

# --- 初始化会话状态 (用来保存聊天记录) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 显示历史聊天记录 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 处理用户输入 ---
if prompt := st.chat_input("请输入您的维修问题..."):
    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用你的 AI 逻辑 (这里需要替换成你真实的函数调用)
    # 假设你有一个函数叫 get_ai_response(question)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()  # 创建一个占位符

        # 模拟思考过程 (或者在这里调用你的 search + llm 代码)
        # full_response = get_ai_response(prompt)
        full_response = "正在检索知识库并生成回答..."  # 占位符

        # 如果你想做成打字机效果，可以用这个循环：
        message_placeholder.markdown(full_response)

        # 3. 保存助手回复到历史记录
    st.session_state.messages.append({"role": "assistant", "content": full_response})