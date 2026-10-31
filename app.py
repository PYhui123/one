import streamlit as st
from dashscope import Generation
import os
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


    def get_ai_response(messages):
        """
        调用通义千问大模型并返回生成器（用于流式输出）
        """
        try:
            response = Generation.call(
                model="qwen-plus",
                messages=messages,
                result_format='message',
                stream=True,  # 开启流式输出
                api_key=os.environ.get("DASHSCOPE_API_KEY")
            )
            return response
        except Exception as e:
            st.error(f"AI 调用失败: {str(e)}")
            return None


    # # 2. 调用你的 AI 逻辑
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 获取当前的完整对话历史（包含刚才 append 的用户消息）
        current_messages = st.session_state.messages

        # 调用真实 AI 接口
        ai_stream = get_ai_response(current_messages)

        if ai_stream:
            # 处理流式返回的数据
            for chunk in ai_stream:
                if chunk.status_code == 200:
                    # 提取当前片段的文本内容
                    content = chunk.output.choices[0].message.content
                    full_response += content

                    # 实时更新界面，模拟打字机效果
                    message_placeholder.markdown(full_response + "▌")
                else:
                    st.error(f"请求出错: {chunk.message}")
                    break

        # 显示最终结果（去掉光标）
        message_placeholder.markdown(full_response)

    # # 3. 保存助手回复到历史记录
    st.session_state.messages.append({"role": "assistant", "content": full_response})