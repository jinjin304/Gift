# 文件名: app.py
import streamlit as st
import os
import time
from lang import STRINGS  # <--- 1. 导入刚才写的变量文件

# --- 页面基础设置 ---
st.set_page_config(page_title="What To Gift", page_icon="🎁", layout="centered")

# --- 初始化 Session State (记住用户的语言选择) ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'zh'

# --- 侧边栏配置 ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 语言切换器
    lang_choice = st.selectbox("Language / 语言", ["中文 (zh)", "English (en)"])
    if "English" in lang_choice:
        st.session_state['lang'] = 'en'
    else:
        st.session_state['lang'] = 'zh'
    
    TEXT = STRINGS[st.session_state['lang']]
    
    st.markdown("---")
    
    # --- 修改处：添加了 PHP (₱) ---
    currency = st.selectbox(TEXT["currency_select"], ["USD ($)", "CNY (¥)", "MYR (RM)", "SGD ($)", "EUR (€)", "PHP (₱)"])

# --- 主界面 ---
st.title(TEXT["title"])
st.caption(TEXT["caption"])

# --- 表单区域 ---
# 使用 st.form 可以避免每改一个字页面就刷新一次
with st.form("gift_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        # 使用变量 TEXT["select_relation"]
        relation = st.selectbox(TEXT["select_relation"], TEXT["relation_options"])
    
    with col2:
        budget = st.number_input(TEXT["select_budget"], min_value=0, value=100)

    occasion = st.text_input(TEXT["input_occasion"], placeholder=TEXT["placeholder_occasion"])
    hobbies = st.text_area(TEXT["input_hobbies"], placeholder=TEXT["placeholder_hobbies"])

    submitted = st.form_submit_button(TEXT["button_generate"])

# --- AI 生成逻辑 ---
if submitted:
    if not hobbies or not occasion:
        st.warning(TEXT["warning_hobbies"])
    else:
        # 检查 API Key
        if "GEMINI_API_KEY" not in st.secrets:
            st.error(TEXT["error_api"])
        else:
            try:
                # 只有点击按钮且校验通过后，才引用 AI 库，加快启动速度
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                
                with st.spinner("AI is thinking..."):
                    # 这里的 Prompt 动态插入了用户当前选的语言
                    sys_prompt = f"""
                    You are a gift expert. 
                    User Language: {st.session_state['lang']}
                    Target Currency: {currency}
                    
                    Task: Recommend 3 specific gifts for a {relation} for {occasion}.
                    Hobbies: {hobbies}.
                    Budget: {budget} {currency}.
                    
                    Requirements:
                    1. Output MUST be in JSON format.
                    2. Use the language specified above ({st.session_state['lang']}) for all descriptions.
                    3. JSON keys must be: 'item_name', 'reason', 'estimated_price'.
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=sys_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema={
                                "type": "object",
                                "properties": {
                                    "recommendations": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "item_name": {"type": "string"},
                                                "reason": {"type": "string"},
                                                "estimated_price": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        )
                    )
                    
                    # --- 解析并显示结果 ---
                    import json
                    data = json.loads(response.text)
                    
                    st.success(TEXT["success_ai"])
                    
                    for gift in data["recommendations"]:
                        with st.expander(f"🎁 {gift['item_name']}", expanded=True):
                            st.write(f"**{TEXT['reason']}** {gift['reason']}")
                            st.write(f"**{TEXT['price_label']}** {gift['estimated_price']}")
                            # 生成 Google 搜索链接
                            query = f"{gift['item_name']} buy"
                            st.markdown(f"[{TEXT['search_link']}](https://www.google.com/search?q={query})")

            except Exception as e:
                st.error(f"Error: {e}")

