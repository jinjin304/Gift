import streamlit as st
import os
import json
import time

# --- 1. 页面配置 ---
st.set_page_config(page_title="What To Gift", page_icon="🎁", layout="centered")

# --- 2. 导入 Gemini 客户端（需要确保安装了 google-genai 库） ---
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


# --- 3. 核心 AI 推荐函数 ---
def get_ai_recommendations(relation, occasion, budget, hobbies):
    if not AI_READY:
        # 返回模拟数据
        st.info("正在返回模拟结果...")
        time.sleep(1)
        return [{"item": "AI 正在思考中...", "reason": "请检查 Streamlit Secrets 中是否正确配置了 GEMINI_API_KEY。", "price": "无", "link": "#"}]
    
    # 构建详细的 AI 提示词（Prompt）
    prompt = f"""
    你是一个专业且富有创意的送礼参谋。你的任务是根据用户的详细要求，推荐3个独一无二、贴心且具体的礼物方案。
    请注意：所有推荐必须是真实存在且可购买的商品。

    以下是用户输入：
    - 关系：{relation}
    - 场景：{occasion}
    - 预算：{budget}
    - 爱好/特点：{hobbies}

    请严格以 JSON 格式返回你的结果。JSON 结构必须是一个名为 'recommendations' 的列表（List），列表中每个元素都必须包含以下四个键：
    1. 'item' (礼物名称，简洁具体)
    2. 'reason' (推荐理由，详细说明为什么这个礼物适合该场景和人物特点，字数控制在100字以内)
    3. 'price' (预估价格范围，使用中文如 '约 ¥500 - ¥800')
    4. 'link' (一个真实的电商搜索链接，例如淘宝或京东的搜索结果链接，以https://开头)
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
    
    with st.spinner('🤖 Gemini AI 正在为您分析需求，生成个性化方案中...'):
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

st.title("What To Gift")
st.caption("送礼不用猜，AI 帮你选")

st.markdown("---")

# 用户输入区
col1, col2 = st.columns(2)

with col1:
    relation = st.selectbox("对方是你的？", ["女朋友/老婆", "男朋友/老公", "父母/长辈", "好朋友", "领导/客户"])
    budget = st.selectbox("预算范围", ["¥200以内 (小心意)", "¥200 - ¥1000 (体面)", "¥1000 - ¥5000 (贵重)", "不差钱"])

with col2:
    occasion = st.text_input("送礼场景？", value="生日")
    hobbies = st.text_input("对方有什么爱好/特点？", value="喜欢喝茶，对健康比较关注")

# 生成按钮
if st.button("✨ 生成送礼方案", use_container_width=True):
    if not hobbies:
        st.warning("请输入对方的爱好，让 AI 判断得更准！")
    else:
        results = get_ai_recommendations(relation, occasion, budget, hobbies)
        
        if results:
            st.success("🎉 AI 已为您生成 3 个绝佳方案！")
            
            # 结果展示区
            for i, res in enumerate(results):
                with st.expander(f"🎁 方案 {i+1}: {res.get('item', '未知礼物')} ({res.get('price', '未知价格')})", expanded=True):
                    st.write(f"**💡 推荐理由：** {res.get('reason', 'N/A')}")
                    # 使用 markdown 确保链接可以点击
                    st.markdown(f"[🛒 立即搜索购买]({res.get('link', '#')})")
        else:
            st.error("未能成功获取 AI 推荐，请检查 API Key 和网络连接。")

st.markdown("---")
if AI_READY:
    st.markdown("当前版本由 Gemini AI 驱动，提供实时个性化推荐。")
else:
    st.markdown("请配置您的 Gemini API Key 以解锁 AI 推荐功能。")




