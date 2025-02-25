import warnings
warnings.filterwarnings("ignore", category=Warning)

import streamlit as st
import st_pages 

# Set page config
st.set_page_config(page_title="Chatbaby - Ollama Interface", layout="wide", page_icon="🤖")

# Load custom CSS from file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles.css')

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "AI Conversation"  # 设置默认页面

# Header（保持不变）
st.markdown(f"""
<div class="header">
    <div class="animated-bg"></div>
    <div class="header-content">
        <h1 class="header-title">Chatbaby</h1> 
        <p class="header-subtitle">后台推理资源由四川大学伍元凯团队提供。</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 更新后的页面定义
PAGES = {
    "AI Conversation": {
        "icon": "chat-dots",
        "func": st_pages.ai_chatbot,
        "description": "Interactive AI Chat",
        "badge": "Application",
        "color": "var(--highlight-color)"
    },
    "RAG Conversation": {
        "icon": "chat-dots",
        "func": st_pages.rag_chat,
        "description": "PDF AI Chat Assistant",
        "badge": "Application",
        "color": "var(--highlight-color)"
    }
}

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
""", unsafe_allow_html=True)

# 必须保留的导航函数定义
def navigate():  # 这个函数定义之前被意外删除了
    with st.sidebar:
        st.markdown('''
        <a href="https://cs.scu.edu.cn/info/1279/17062.htm" target="_blank" style="text-decoration: none; color: inherit; display: block;">
            <div class="header-container" style="cursor: pointer;">
                <div class="profile-section">
                    <div class="profile-info">
                        <h1 style="font-size: 38px;">Wykteam</h1>
                        <span class="active-badge" style="font-size: 20px;">伍元凯教授火热招生中，点击直达</span>
                    </div>
                </div>
            </div>
        </a>
        ''', unsafe_allow_html=True)

        st.markdown('---')

        # 创建导航菜单项
        for page, info in PAGES.items():
            selected = st.session_state.current_page == page
            
            if st.button(
                f"{page}",
                key=f"nav_{page}",
                use_container_width=True,
                type="secondary" if selected else "primary"
            ):
                st.session_state.current_page = page
                st.rerun()

            st.markdown(f"""
                <div class="menu-item {'selected' if selected else ''}">
                    <div class="menu-icon">
                        <i class="bi bi-{info['icon']}"></i>
                    </div>
                    <div class="menu-content">
                        <div class="menu-title">{page}</div>
                        <div class="menu-description">{info['description']}</div>
                    </div>
                    <div class="menu-badge">{info['badge']}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        
        return st.session_state.current_page

# 执行页面逻辑
try:
    selected_page = navigate()  # 现在可以正确调用函数
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    page_function = PAGES[selected_page]["func"]
    page_function()
except Exception as e:
    st.error(f"Error loading page: {str(e)}")
    st.session_state.current_page = "AI Conversation"
    st.rerun()


