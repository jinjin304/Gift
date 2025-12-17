import streamlit as st
import os
import json
import time

# --- 语言字典 ---
MESSAGES = {
    "zh": {
        "title": "What To Gift",
        "caption": "送礼不用猜，AI 帮你选",
        "language_select": "Language / 语言",
        "currency_select": "选择货币 (Currency)",
        "select_relation": "对方是你的？",
        "select_budget": "预算范围",
        "input_occasion": "送礼场景？",
        "input_hobbies": "对方有什么爱好/特点？",
        "button_generate": "✨ 生成送礼方案",
        "placeholder_occasion": "生日",
        "placeholder_hobbies": "喜欢喝茶，对健康比较关注",
        "warning_hobbies": "请输入对方的爱好，让 AI 判断得更准！",
        "success_ai": "🎉 AI 已为您生成 3 个绝佳方案！",
        "reason": "💡 推荐理由：",
        "search_link": "🛒 立即搜索购买",
        "budget_options": ["较小金额", "中等金额", "高昂金额", "不设限制"],
        "relation_options": [
            "女朋友", "老婆", "男朋友", "老公", "父亲", "母亲", 
            "爷爷", "奶奶", "好朋友 (男)", "好朋友 (女)", "领导", "客户"
        ],
        "footer_ai": "由 AI 提供实时个性化推荐。",
        "footer_no_ai": "请配置您的 Gemini API Key 以解锁 AI 推荐功能。",
    },
    "en": {
        "title": "What To Gift",
        "caption": "No Idea? AI will pick one for you",
        "language_select": "Language / 语言",
        "currency_select": "Select Currency",
        "select_relation": "Who is the recipient?",
        "select_budget": "Budget Range",
        "input_occasion": "Occasion?",
        "input_hobbies": "Recipient's hobbies/characteristics?",
        "button_generate": "✨ Generate Gift Ideas",
        "placeholder_occasion": "Birthday",
        "placeholder_hobbies": "Loves tea, interested in health and wellness",
        "warning_hobbies": "Please enter the recipient's hobbies for better AI suggestions!",
        "success_ai": "🎉 AI has generated 3 excellent ideas!",
        "reason": "💡 Recommendation Reason:",
        "search_link": "🛒 Search and Buy Now",
        "budget_options": ["Small Budget", "Medium Budget", "High Budget", "No limit"],
        "relation_options": [
            "Girlfriend", "Wife", "Boyfriend", "Husband", "Father", "Mother", 
            "Grandfather", "Grandmother", "Close Friend (Male)", "Close Friend (Female)", 
            "Boss/Supervisor", "Client"
        ],
        "footer_ai": "Powered by AI, providing real-time personalized recommendations.",
        "footer_no_ai": "Please configure your Gemini API Key to unlock AI features.",
    }
}

# --- 1. 页面配置 ---
st.set_page_config(page_title="What To Gift", page_icon="🎁", layout="centered")

# --- 2. 导入 Gemini 客户端 ---
try:
    from google import genai
    from google.genai import types
    
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        MODEL_NAME = "gemini-2.5-flash"
        AI_READY = True
    else:
        st.warning("⚠️ Gemini API Key 未找到。软件将运行在模拟模式。")
        AI_READY = False
except Exception as e:
    st.error(f"❌ 初始化失败: {e}")
    AI_READY = False

# --- UI 初始化（侧边栏配置） ---
# 语言选择
st.session_state['lang'] = st.session_state.get('lang', 'zh')
lang_key = st.sidebar.selectbox(MESSAGES["zh"]["language_select"], ["中文 (zh)", "English (en)"])
st.session_state['lang'] = 'zh' if '中文' in lang_key else 'en'
TEXT = MESSAGES[st.session_state['lang']]

# 货币选择 (新增功能)
currency = st.sidebar.selectbox(TEXT["currency_select"], ["CNY (¥)", "USD ($)", "MYR (RM)", "SGD ($)", "EUR (€)", "GBP (£)"])

# --- 3. 核心 AI 推荐函数 ---
def get_ai_recommendations(relation, occasion, budget, hobbies, selected_currency):
    if not AI_READY:
        st.info("正在返回模拟结果...")
        time.sleep(1)
        return [{"item": "AI 正在思考中...", "reason": "请检查 API Key 配置。", "price": "无", "link": "#"}]
    
    current_lang = st.session_state['lang']
    
    # 提示词中加入了货币要求
    prompt = f"""
    You are a professional gift consultant. Recommend 3 unique gift ideas.
    IMPORTANT: All items must be real and purchasable.

    User Input:
    - Relationship: {relation}
    - Occasion: {occasion}
    - Budget: {budget}
    - Hobbies: {hobbies}
    - **Currency to use for price**: {selected_currency}

    Rules:
    1. Respond strictly in **{current_lang}**.
    2. Provide price estimates in the selected currency: **{selected_currency}**.
    3. Return ONLY a JSON object with a 'recommendations' list containing: 'item', 'reason', 'price', and 'link'.
    """

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item": {"type": "string"},
                            "reason": {"type": "string"},
                            "price": {"type": "string"},
                            "link": {"type": "string"}
                        },
                        "required": ["item", "reason", "price", "link"]
                    }
                }
            }
        },
    )
    
    with st.spinner(f'🤖 AI is generating ideas in {current_lang}...'):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[prompt],
                config=config,
            )
            data = json.loads(response.text)
            return data.get('recommendations', [])
        except Exception as e:
            st.error(f"API Error: {e}")
            return []

# --- 4. 软件界面 (UI) ---
st.title(TEXT["title"])
st.caption(TEXT["caption"])
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    relation = st.selectbox(TEXT["select_relation"], TEXT["relation_options"])
    # 预算选项现在不带具体符号，AI 会根据侧边栏选中的货币来判断金额大小
    budget = st.selectbox(TEXT["select_budget"], TEXT["budget_options"])

with col2:
    occasion = st.text_input(TEXT["input_occasion"], value=TEXT["placeholder_occasion"])
    hobbies = st.text_input(TEXT["input_hobbies"], value=TEXT["placeholder_hobbies"])

if st.button(TEXT["button_generate"], use_container_width=True):
    if not hobbies:
        st.warning(TEXT["warning_hobbies"])
    else:
        # 将选中的 currency 传给函数
        results = get_ai_recommendations(relation, occasion, budget, hobbies, currency)
        
        if results:
            st.success(TEXT["success_ai"])
            for i, res in enumerate(results):
                with st.expander(f"🎁 {i+1}: {res.get('item', 'N/A')} ({res.get('price', 'N/A')})", expanded=True):
                    st.write(f"**{TEXT['reason']}** {res.get('reason', 'N/A')}")
                    st.markdown(f"[{TEXT['search_link']}]({res.get('link', '#')})")
        else:
            st.error("AI 推荐获取失败。")

st.markdown("---")
st.markdown(TEXT["footer_ai"] if AI_READY else TEXT["footer_no_ai"])
