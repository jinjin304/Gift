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
        "budget_options": ["200以内 ", "200 - 1000 ", "1000 - 5000 ", "5000以上"],
        # ** FIX: 关系选项再次细化 **
        "relation_options": [
            "女朋友", 
            "老婆", 
            "男朋友", 
            "老公", 
            "父亲", 
            "母亲", 
            "爷爷", 
            "奶奶", 
            "好朋友 (男)", 
            "好朋友 (女)",
            "领导",
            "客户"
        ],
        "footer_ai": "由AI提供实时个性化推荐。",
        "footer_no_ai": "请配置您的 Gemini API Key 以解锁 AI 推荐功能。",
    },
    "en": {
        "title": "What To Gift",
        "caption": "No Idea? AI will pick one for you",
        "language_select": "Language / 语言",
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
        "budget_options": ["Under 200 ", "200 - 1000 ", "1000 - 5000 ", "5000 above"],
        # ** FIX: 关系选项再次细化 **
        "relation_options": [
            "Girlfriend", 
            "Wife", 
            "Boyfriend", 
            "Husband", 
            "Father", 
            "Mother", 
            "Grandfather", 
            "Grandmother", 
            "Close Friend (Male)", 
            "Close Friend (Female)",
            "Boss/Supervisor",
            "Client"
        ],
        "footer_ai": "Powered by AI, providing real time personalized recommendations.",
        "footer_no_ai": "Please configure your Gemini API Key to unlock AI features.",
    }
}



# --- 1. 页面配置 ---

st.set_page_config(page_title="What To Gift", page_icon="🎁", layout="centered")



# --- 2. 导入 Gemini 客户端 ---

try:

    from google import genai

    from google.genai import types

    

    # 尝试从 Streamlit secrets 读取 API Key

    if "GEMINI_API_KEY" in st.secrets:

        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        MODEL_NAME = "gemini-2.5-flash" # 适合快速响应的模型

        AI_READY = True

    else:

        st.warning("⚠️ Gemini API Key 未找到。软件将运行在模拟模式。")

        AI_READY = False



except ImportError:

    st.error("❌ 缺少 google-genai 库。请确保在 requirements.txt 中添加了 'google-genai'。")

    AI_READY = False

except Exception as e:

    st.error(f"❌ 初始化 Gemini 客户端失败: {e}")

    AI_READY = False



# --- UI 初始化（必须放在函数调用前） ---

# 语言选择器和全局文本加载

st.session_state['lang'] = st.session_state.get('lang', 'zh')

lang_key = st.sidebar.selectbox(MESSAGES["zh"]["language_select"], ["中文 (zh)", "English (en)"])

st.session_state['lang'] = 'zh' if '中文' in lang_key else 'en'

TEXT = MESSAGES[st.session_state['lang']] # 核心变量，所有 UI 文本都从这里取



# --- 3. 核心 AI 推荐函数 ---

def get_ai_recommendations(relation, occasion, budget, hobbies):

    if not AI_READY:

        # 返回模拟数据

        st.info("正在返回模拟结果...")

        time.sleep(1)

        return [{"item": "AI 正在思考中...", "reason": "请检查 Streamlit Secrets 中是否正确配置了 GEMINI_API_KEY。", "price": "无", "link": "#"}]

    

    current_lang = st.session_state['lang'] # 获取当前语言 ('zh' 或 'en')

    

    # 构建详细的 AI 提示词（Prompt）

    prompt = f"""

    You are a professional and creative gift consultant. Your task is to recommend 3 unique, thoughtful, and specific gift ideas based on the user's detailed requirements.

    IMPORTANT: All recommendations must be real, purchasable products.



    User Input Details:

    - Relationship: {relation}

    - Occasion: {occasion}

    - Budget: {budget}

    - Hobbies/Traits: {hobbies}



    You MUST strictly respond in the **{current_lang}** language for ALL text fields.

    

    Please strictly return the result in JSON format. The JSON structure MUST be a list named 'recommendations'. Each item in the list MUST contain the following four keys:

    1. 'item' (Gift name, concise and specific)

    2. 'reason' (Recommendation reason, explain why the gift suits the occasion and person, max 100 characters in the target language)

    3. 'price' (Estimated price range, e.g., '约 500 - 800' or 'Approx 70 - 120')

    4. 'link' (A REAL e-commerce search link, e.g., Taobao/JD search link, starting with https://)

    """



    # 配置 Gemini API 调用参数

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

    

    with st.spinner(f'🤖 Gemini AI is thinking and generating personalized ideas in {current_lang}...'):

        try:

            response = client.models.generate_content(

                model=MODEL_NAME,

                contents=[prompt],

                config=config,

            )

            

            # 解析 JSON 响应

            data = json.loads(response.text)

            return data.get('recommendations', [])



        except Exception as e:

            st.error(f"Gemini API 调用失败或解析错误: {e}")

            return []





# --- 4. 软件界面 (UI) ---



st.title(TEXT["title"])

st.caption(TEXT["caption"])



st.markdown("---")



# 用户输入区

col1, col2 = st.columns(2)



with col1:

    # ** 修复：使用 TEXT 字典加载标签和选项 **

    relation = st.selectbox(TEXT["select_relation"], TEXT["relation_options"])

    budget = st.selectbox(TEXT["select_budget"], TEXT["budget_options"])



with col2:

    # ** 修复：使用 TEXT 字典加载标签和默认值 **

    occasion = st.text_input(TEXT["input_occasion"], value=TEXT["placeholder_occasion"])

    hobbies = st.text_input(TEXT["input_hobbies"], value=TEXT["placeholder_hobbies"])



# 生成按钮

if st.button(TEXT["button_generate"], use_container_width=True):

    if not hobbies:

        st.warning(TEXT["warning_hobbies"])

    else:

        results = get_ai_recommendations(relation, occasion, budget, hobbies)

        

        if results:

            st.success(TEXT["success_ai"])

            

            # 结果展示区

            for i, res in enumerate(results):

                # ** 修复：使用 TEXT 字典加载标签 **

                with st.expander(f"🎁 {i+1}: {res.get('item', 'N/A')} ({res.get('price', 'N/A')})", expanded=True):

                    st.write(f"**{TEXT['reason']}** {res.get('reason', 'N/A')}")

                    # ** 修复：使用 TEXT 字典加载链接文本 **

                    st.markdown(f"[{TEXT['search_link']}]({res.get('link', '#')})")

        else:

            st.error("未能成功获取 AI 推荐，请检查 API Key 和网络连接。")



st.markdown("---")

if AI_READY:

    st.markdown(TEXT["footer_ai"])

else:

    st.markdown(TEXT["footer_no_ai"])


