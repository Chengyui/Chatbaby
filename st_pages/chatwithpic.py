import streamlit as st
import base64
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from schema.streamhandler import StreamHandler
from schema.ollama_models_db import get_ollama_models
from typing import Any, List, Optional
import requests
import json
from langchain_core.outputs import Generation, LLMResult
from langchain.callbacks.manager import CallbackManagerForLLMRun

def query_ollama(image_base64, prompt="请直接返回图中文字信息，若没有文字信息则详细描述图中物体"):
    url = "http://localhost:11434/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "minicpm-v:latest",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{image_base64}"
                    }
                ]
            }
        ],
        "stream": False,
        "keep_alive":100
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()


        content = response.content

        encodings = ['utf-8', 'ascii', 'latin1']
        for encoding in encodings:
            try:
                decoded_content = content.decode(encoding)
                print(json.loads(decoded_content)["choices"][0]["message"]["content"])
                return json.loads(decoded_content)
            except UnicodeDecodeError:
                continue
            except json.JSONDecodeError:
                continue


        st.error("Failed to decode response. Raw response:")
        st.text(content)
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with Ollama: {e}")
        return None


def get_conversation_chain(model_name: str) -> ConversationChain:
    """初始化支持图片的对话链"""
    llm = Ollama(
        model=model_name,
        temperature=0.2,
        base_url="http://localhost:11434",
        keep_alive=3600,
    )

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template="""Current conversation:
                    {history}
                    Human: {input}
                    Assistant:""")

    memory = ConversationBufferMemory(return_messages=True)
    return ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=True)


# def on_model_change():
#     """模型切换回调函数"""
#     st.session_state.messages = []
#     st.session_state.conversation = None
#     st.session_state.uploaded_image = None

# 修改模型切换回调（保留图片上下文）
def on_model_change():
    # st.session_state.messages = []
    # st.session_state.conversation = None
    # st.session_state.uploaded_image = None
    # 注意：不再清除 uploaded_image 和 image_description
    # st.session_state.messages = []
    # st.session_state.conversation = None
    # st.session_state.uploaded_image = None
    # st.session_state.image_description = None
    st.session_state.image_prompt_added = False
    pass
def run():
    """主运行函数"""
    st.markdown('''
    <style>
        .uploaded-image {max-width: 300px; margin-top: 10px;}
    </style>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="header-container">
        <p class="header-subtitle">🤖 支持多模态的智能聊天助手</p>
    </div>
    </div>
    ''', unsafe_allow_html=True)

    # 初始化会话状态
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None

    # 获取可用模型
    models = get_ollama_models()
    if not models:
        st.warning("请先启动Ollama服务")
        return

    # 模型选择
    st.subheader("选择语言模型:")
    col1, _ = st.columns([2, 6])
    with col1:
        model_name = st.selectbox(
            "模型",
            models,
            format_func=lambda x: f'🔮 {x}',
            key="model_select",
            on_change=on_model_change,
            label_visibility="collapsed"
        )

    # Initialize conversation if needed
    if st.session_state.conversation is None:
        st.session_state.conversation = get_conversation_chain(model_name)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            try:
                img = message["image"]
                st.image(f"data:image/png;base64,{img}",
                         use_column_width=True,
                         caption="用户上传图片")
                st.markdown(message["content"])
            except:
                st.markdown(message["content"])


    # 图片上传组件
    # if "image_description" not in st.session_state:
    uploaded_file = st.file_uploader(
        "上传图片（支持PNG/JPG）",
        type=["png", "jpg", "jpeg"],
        key="image_uploader",
        label_visibility="collapsed"
    )

    # 处理上传的图片（修改这部分）
    if uploaded_file is not None and "image_description" not in st.session_state:
        bytes_data = uploaded_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        st.session_state.uploaded_image = base64_image

        # 实时显示预览
        st.session_state.messages.append({
            "role": "user",
            "image": base64_image,
            "content":""
        })
        # st.image(bytes_data, caption="已上传图片")

        # 自动触发图片分析（新增部分）
        # if "minicpm" in model_name.lower():
        with st.spinner('正在分析图片...'):
            analysis_result = query_ollama(base64_image)
            if analysis_result:
                st.session_state.image_description= analysis_result["choices"][0]["message"]["content"]
                # 显示并保存结果
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    try:
                        st.image(f"data:image/png;base64,{base64_image}",
                                 use_column_width=True,
                                )
                        # 显示并保存结果
                        response_placeholder.markdown("视觉分析结果："+st.session_state.image_description)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "image": base64_image,
                            "content": f"图片分析完成：{st.session_state.image_description}",
                        })
                    except Exception as e:
                        error_msg = f"生成回复时出错: {str(e)}"
                        response_placeholder.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # 处理用户输入（修改输入处理逻辑）
    if prompt := st.chat_input(f"与{model_name}对话..."):
        full_prompt = prompt

        # 如果有图片描述则自动附加到输入（新增上下文拼接）
        if 'image_description' in st.session_state and st.session_state.image_prompt_added is False:
            full_prompt = f"[图片内容：{st.session_state.image_description}] {prompt}"
            st.session_state.image_prompt_added = True

        # 添加用户消息到历史（保持原逻辑）
        user_message = {"role": "user", "content": full_prompt}
        # if st.session_state.get('uploaded_image'):
        #     user_message["image"] = st.session_state.uploaded_image
        st.session_state.messages.append(user_message)

        # 显示用户消息（增加描述显示）
        with st.chat_message("user"):
            st.markdown(prompt)  # 仅显示原始输入
            # if st.session_state.get('uploaded_image'):
            #     st.image(f"data:image/png;base64,{st.session_state.uploaded_image}",
            #              use_column_width=True,
            #              caption="")
            #     # 显示分析结果提示（新增）
            #     if 'image_description' in st.session_state:
            #         st.caption(f"当前对话包含图片上下文：{st.session_state.image_description}")

        # 生成回复（优化模型切换支持）
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                # # 视觉模型特殊处理（新增判断逻辑）
                # if "minicpm" in model_name.lower():
                #     # 直接使用图片分析结果
                #     response = st.session_state.image_description
                # else:
                # 普通对话流程（修改为使用full_prompt）
                stream_handler = StreamHandler(response_placeholder)
                st.session_state.conversation.llm.callbacks = [stream_handler]

                response = st.session_state.conversation.run(
                    input=full_prompt  # 使用包含上下文的完整prompt
                )

                # 显示并保存结果
                response_placeholder.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                error_msg = f"生成回复时出错: {str(e)}"
                response_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
