import streamlit as st
import os
import json
import time

# --- 1. 语言字典 ---
MESSAGES = {
    "zh": {
        "title": "What To Gift",
        "caption": "送礼不用猜，AI 帮你选",
        "language_select": "Language / 语言",
        "currency_select": "目标显示货币 (Currency)",
        "select_relation": "对方是你的？",
        "select_budget": "预算金额",
        "input_occasion": "送礼场景？",
        "input_hobbies": "对方有什么爱好/特点？",
        "button_generate": "✨ 生成送礼方案",
        "placeholder_occasion": "例如：生日、周年纪念、乔迁",
        "placeholder_hobbies": "例如：喜欢喝茶，对健康比较关注，极简主义者",
        "warning_hobbies": "请输入完整的场景和爱好，让 AI 判断得更准！",
        "success_ai": "🎉 AI 已为您生成 3 个绝佳方案！",
        "reason": "💡 推荐理由：",
        "search_link": "🛒 立即搜索购买",
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
        "select_budget": "Budget Amount",
        "input_occasion": "Occasion?",
        "input_hobbies": "Recipient's hobbies/characteristics?",
        "button_generate": "✨ Generate Gift Ideas",
        "placeholder_occasion": "e.g. Birthday, Anniversary",
        "placeholder_hobbies": "e.g. Loves tea, health-conscious, minimalist",
        "warning_hobbies": "Please enter both occasion and hobbies for better AI suggestions!",
        "success_ai": "🎉 AI has generated 3 excellent ideas!",
        "reason": "💡 Recommendation Reason:",
        "search_link": "🛒 Search and Buy Now",
        "relation_options": [
            "Girlfriend", "Wife", "Boyfriend", "Husband", "Father", "Mother", 
            "Grandfather", "Grandmother", "Close Friend (Male)", "Close Friend (Female)", 
            "Boss/Supervisor", "Client"
        ],
        "footer_ai": "Powered by AI, providing real-time personalized recommendations.",
        "footer_no_ai": "Please configure your Gemini API Key to unlock AI features.",
    }
}

# --- 2. 页面配置 ---
st.set_page_config(page_title="What To Gift", page_icon="🎁", layout="centered")

# 侧边栏设置
st.session_state['lang'] = st.session_state.get('lang', 'zh')
lang_key = st.sidebar.selectbox(MESSAGES["zh"]["language_select"], ["中文 (zh)", "English (en)"])
st.session_state['lang'] = 'zh' if '中文' in lang_key else 'en'
TEXT = MESSAGES[st.session_state['lang']]

# 货币选择
currency_choice = st.sidebar.selectbox(TEXT["currency_select"], ["USD ($)", "CNY (¥)", "MYR (RM)", "SGD ($)", "EUR (€)", "GBP (£)"])

# --- 3. 初始化 Gemini 客户端 ---
try:
    from google import genai
    from google.genai import types
    if "GEMINI_API_KEY" in st.secrets:
        # 这里建议直接使用变量读取，不要把明文 Key 留在代码里
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        MODEL_NAME = "gemini-2.0-flash" 
        AI_READY = True
    else:
        st.warning("⚠️ API Key 未找到。")
        AI_READY = False
except Exception as e:
    st.error(f"❌ 初始化失败: {e}")
    AI_READY = False

# --- 4. 核心 AI 推荐函数 ---
def get_ai_recommendations(relation, occasion, budget_val, hobbies, target_currency):
    if not AI_READY: return []
    current_lang = st.session_state['lang']
    
    # 核心 Prompt：告诉 AI 用户输入的金额和货币单位
    prompt = f"""
    You are a professional gift consultant. Recommend 3 gift ideas.
    
    User Requirements:
    - Recipient: {relation}
    - Occasion: {occasion}
    - **Budget**: {budget_val} {target_currency} 
    - Hobbies: {hobbies}
    
    Instructions:
    1. Respond entirely in **{current_lang}**.
    2. Suggest gifts that strictly fit the budget of **{budget_val} {target_currency}**.
    3. The 'price' field in your response must be in **{target_currency}**.
    4. Return JSON only with 'item', 'reason', 'price', and 'link'.
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
                            "item": {"type":
