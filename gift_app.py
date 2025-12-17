import streamlit as st
import os
import json
import time

# --- 1. 语言字典：预算以美元为显示基础 ---
MESSAGES = {
    "zh": {
        "title": "What To Gift",
        "caption": "送礼不用猜，AI 帮你选",
        "language_select": "Language / 语言",
        "currency_select": "目标显示货币 (Currency)",
        "select_relation": "对方是你的？",
        "select_budget": "预算范围 (以 USD 为基准)",
        "input_occasion": "送礼场景？",
        "input_hobbies": "对方有什么爱好/特点？",
        "button_generate": "✨ 生成送礼方案",
        "placeholder_occasion": "生日",
        "placeholder_hobbies": "喜欢喝茶，对健康比较关注",
        "warning_hobbies": "请输入对方的爱好，让 AI 判断得更准！",
        "success_ai": "🎉 AI 已为您生成 3 个绝佳方案！",
        "reason": "💡 推荐理由：",
        "search_link": "🛒 立即搜索购买",
        # 预算选项固定显示美金数值
        "budget_options": ["$50 以内", "$50 - $200", "$200 - $500", "$500 - $1000", "$1000 以上"],
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
        "currency_select": "Display Currency",
        "select_relation": "Who is the recipient?",
        "select_budget": "Budget Range (Based on USD)",
        "input_occasion": "Occasion?",
        "input_hobbies": "Recipient's hobbies/characteristics?",
        "button_generate": "✨ Generate Gift Ideas",
        "placeholder_occasion": "Birthday",
        "placeholder_hobbies": "Loves tea, interested in health and wellness",
        "warning_hobbies": "Please enter the recipient's hobbies for better AI suggestions!",
        "success_ai": "🎉 AI has generated 3 excellent ideas!",
        "reason": "💡 Recommendation Reason:",
        "search_link": "🛒 Search and Buy Now",
        "budget_options": ["Under $50", "$50 - $200", "$200 - $500", "$500 - $1000", "Above $1000"],
        "relation_options": [
            "Girlfriend", "Wife", "Boyfriend", "Husband", "Father", "Mother", 
            "Grandfather", "Grandmother", "Close Friend (Male)", "Close Friend (Female)", 
            "Boss/Supervisor", "Client"
        ],
        "footer_ai": "Powered by AI, providing real-time personalized recommendations.",
        "footer_no_ai": "Please configure your Gemini API Key to unlock AI features.",
    }
}

# --- 2. 页面配置与侧边栏 ---
st.set_page_config(page_title="What To Gift", page_icon="🎁", layout="centered")

# 语言与货币选择
st.session_state['lang'] = st.session_state.get('lang', 'zh')
lang_key = st.sidebar.selectbox(MESSAGES["zh"]["language_select"], ["中文 (zh)", "English (en)"])
st.session_state['lang'] = 'zh' if '中文' in lang_key else 'en'
TEXT = MESSAGES[st.session_state['lang']]

currency_choice = st.sidebar.selectbox(TEXT["currency_select"], ["USD ($)", "CNY (¥)", "MYR (RM)", "SGD ($)", "EUR (€)", "GBP (£)"])

# --- 3. 初始化 Gemini 客户端 ---
try:
    from google import genai
    from google.genai import types
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        MODEL_NAME = "gemini-2.5-flash"
        AI_READY = True
    else:
        st.warning("⚠️ API Key 未找到。")
        AI_READY = False
except Exception as e:
    st.error(f"❌ 初始化失败: {e}")
    AI_READY = False

# --- 4. 核心 AI 推荐函数 ---
def get_ai_recommendations(relation, occasion, budget_usd, hobbies, target_currency):
    if not AI_READY:
        return []
    
    current_lang = st.session_state['lang']
    
    # 核心 Prompt 修改：要求 AI 换算
    prompt = f"""
    You are a professional gift consultant. Recommend 3 gift ideas.
    
    User Requirements:
    - Recipient: {relation}
    - Occasion: {occasion}
    - **Budget Base**: {budget_usd} (This value is in USD)
    - Hobbies: {hobbies}
    
    **CRITICAL INSTRUCTIONS**:
    1. Respond entirely in **{current_lang}**.
    2. The user wants the prices displayed in **{target_currency}**. 
    3. You MUST convert the USD budget range into the equivalent value in **{target_currency}** based on current approximate exchange rates.
    4. Ensure the recommended items are realistic within that converted budget in the local market.
    5. Return JSON only.
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
    
    with st.spinner(f'🤖 AI is calculating and thinking...'):
        try:
            # 增加重试逻辑以应对 503 错误
            for i in range(3): 
                try:
                    response = client.models.generate_content(model=MODEL_NAME, contents=[prompt], config=config)
                    return json.loads(response.text).get('recommendations', [])
                except Exception as e:
                    if "503" in str(e) and i < 2:
                        time.sleep(2) # 等待 2 秒重试
                        continue
                    raise e
        except Exception as e:
            st.error(f"Gemini API 报错: {e}")
            return []

# --- 5. 软件界面 (UI) ---
st.title(TEXT["title"])
st.caption(TEXT["caption"])
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    relation = st.selectbox(TEXT["select_relation"], TEXT["relation_options"])
    budget = st.selectbox(TEXT["select_budget"], TEXT["budget_options"])
with col2:
    occasion = st.text_input(TEXT["input_occasion"], value=TEXT["placeholder_occasion"])
    hobbies = st.text_input(TEXT["input_hobbies"], value=TEXT["placeholder_hobbies"])

if st.button(TEXT["button_generate"], use_container_width=True):
    if not hobbies:
        st.warning(TEXT["warning_hobbies"])
    else:
        results = get_ai_recommendations(relation, occasion, budget, hobbies, currency_choice)
        if results:
            st.success(TEXT["success_ai"])
            for i, res in enumerate(results):
                with st.expander(f"🎁 {i+1}: {res.get('item')} ({res.get('price')})", expanded=True):
                    st.write(f"**{TEXT['reason']}** {res.get('reason')}")
                    st.markdown(f"[{TEXT['search_link']}]({res.get('link')})")

st.markdown("---")
st.markdown(TEXT["footer_ai"] if AI_READY else TEXT["footer_no_ai"])
