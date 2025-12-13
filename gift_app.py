import streamlit as st
import time
import random

# --- 页面配置 ---
st.set_page_config(page_title="心意管家 AI", page_icon="🎁", layout="centered")

# --- 模拟 AI 推荐算法 (在实际产品中，这里会连接 GPT/Gemini API) ---
def get_ai_recommendations(relation, occasion, budget, hobbies):
    # 模拟 AI 思考过程
    with st.spinner(f'AI 正在分析 {relation} 的性格与 {occasion} 的场景...'):
        time.sleep(1.5) # 假装在思考
    
    # 这里是模拟的数据库，实际会由 AI 实时生成
    recommendations = [
        {
            "item": "定制黑胶唱片机",
            "reason": f"既然对方喜欢{hobbies}，复古的黑胶唱片机不仅能听音乐，更是一种生活态度的展示。非常适合{occasion}。",
            "price": "约 ¥800 - ¥1200",
            "link": "https://www.taobao.com/search?q=黑胶唱片机"
        },
        {
            "item": "全自动胶囊咖啡机",
            "reason": f"考虑到{budget}的预算，送一台高颜值的咖啡机非常体面。每天早上一杯咖啡，对方都会想起你。",
            "price": "约 ¥600 - ¥900",
            "link": "https://www.jd.com/search?keyword=胶囊咖啡机"
        },
        {
            "item": "深度睡眠香薰礼盒",
            "reason": "现代人压力大，送一份高质量的睡眠体验绝对不会出错。包装精美，仪式感满满。",
            "price": "约 ¥300 - ¥500",
            "link": "https://www.taobao.com/search?q=助眠香薰"
        }
    ]
    return recommendations

# --- 软件界面 (UI) ---

st.title("🎁 心意管家 (Gift Guru)")
st.caption("你的一人公司 AI 送礼顾问")

st.markdown("---")

# 1. 用户输入区
col1, col2 = st.columns(2)

with col1:
    relation = st.selectbox("对方是你的？", ["女朋友/老婆", "男朋友/老公", "父母/长辈", "好朋友", "领导/客户"])
    budget = st.selectbox("预算范围", ["¥200以内 (小心意)", "¥200 - ¥1000 (体面)", "¥1000 - ¥5000 (贵重)", "不差钱"])

with col2:
    occasion = st.text_input("送礼场景？", value="生日")
    hobbies = st.text_input("对方有什么爱好/特点？", value="喜欢听歌，偶尔喝咖啡")

# 2. 生成按钮
if st.button("✨ 生成送礼方案", use_container_width=True):
    if not hobbies:
        st.warning("请输入对方的爱好，让 AI 判断得更准！")
    else:
        # 调用上面的模拟函数
        results = get_ai_recommendations(relation, occasion, budget, hobbies)
        
        st.success("AI 已为您生成 3 个绝佳方案！")
        
        # 3. 结果展示区
        for res in results:
            with st.expander(f"🎁 推荐：{res['item']} ({res['price']})", expanded=True):
                st.write(f"**💡 推荐理由：** {res['reason']}")
                st.markdown(f"[🛒 点击购买链接]({res['link']})")

st.markdown("---")
st.markdown("*注：这是一个 MVP 原型。实际接入 AI API 后，推荐内容将完全根据您的输入实时生成。*")