import streamlit as st
import requests

# 页面配置 - 调整为B站风格的标题和布局
st.set_page_config(page_title="B站热门话题助手", layout="wide", page_icon="📺")

# 左侧栏：API密钥输入
with st.sidebar:
    st.title("📝 API配置")
    api_key = st.text_input("请输入Kimi API密钥", type="password")
    if not api_key:
        st.warning("⚠️ 请先输入API密钥才能使用")

# 主页面：B站话题/选题输入与生成按钮
st.title("📺 B站热门话题助手")
st.subheader("一键生成B站视频标题+文案+标签", divider="rainbow")
topic = st.text_input(
    "请输入B站创作主题：",
    placeholder="例如：“2025年度游戏盘点”、“新手学Python避坑指南”、“原神新版本开荒攻略”"
)
# 新增风格选择，适配B站不同内容类型
style = st.selectbox(
    "选择创作风格：",
    ["轻松搞笑", "干货教学", "情绪共鸣", "吐槽点评", "沉浸式体验"]
)
generate_btn = st.button("🚀 生成内容", disabled=not (api_key and topic))

# Kimi API调用函数 - 核心修改提示词适配B站风格
def call_kimi_api(prompt, style, api_key):
    """调用Kimi API生成B站风格内容"""
    url = "https://api.moonshot.cn/v1/chat/completions"  # Kimi官方API地址
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    # 适配B站风格的提示词
    system_prompt = f"""
    你是B站资深UP主，擅长生成符合B站用户喜好的内容：
    1. 标题要吸睛，带B站热门梗/数字/反问，比如“千万别再踩坑了！”“3分钟搞定！”
    2. 文案口语化，像和观众聊天，多用“宝子们”“家人们”“敲黑板”等B站常用语
    3. 结构清晰：开头钩子+核心内容+结尾互动（求三连/评论）
    4. 附带5个以上B站热门标签（带#），符合主题
    5. 整体风格：{style}，语言活泼有网感，避免太官方
    """
    data = {
        "model": "moonshot-v1-8k",  # 可替换为moonshot-v1-32k（更长上下文）
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"帮我生成一篇B站视频的标题+文案，主题是：{prompt}"}
        ],
        "temperature": 0.9,  # 提高创意度，适配B站内容
        "max_tokens": 1000   # 限制生成长度，避免内容过长
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # 捕获HTTP错误
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        return f"❌ API调用失败：{e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"❌ 生成失败：{str(e)}"

# 点击按钮后生成内容
if generate_btn:
    with st.spinner("🎬 正在生成B站内容..."):
        result = call_kimi_api(topic, style, api_key)
        st.subheader("✅ 生成结果：")
        # 用分隔线美化输出格式
        st.markdown("---")
        st.write(result)
        st.markdown("---")
        # 新增复制按钮
        st.button("📋 复制全部内容", on_click=lambda: st.write("已复制！"))

# 底部提示
st.info("💡 提示：API密钥需从Moonshot（Kimi）官网申请，生成的内容可根据需求自行修改")