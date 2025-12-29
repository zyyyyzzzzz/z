import streamlit as st
import requests
import os

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


# 核心API调用函数（纯原生实现，避开LangChain版本兼容问题）
def call_kimi_api(prompt, style, api_key):
    """直接调用Kimi API生成B站风格内容（稳定版）"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # B站风格提示词（优化版）
    system_prompt = f"""
    你是B站资深UP主，擅长生成符合B站用户喜好的内容：
    1. 标题要吸睛，带B站热门梗/数字/反问，比如“千万别再踩坑了！”“3分钟搞定！”
    2. 文案口语化，像和观众聊天，多用“宝子们”“家人们”“敲黑板”等B站常用语
    3. 结构清晰：开头钩子+核心内容+结尾互动（求三连/评论）
    4. 附带5个以上B站热门标签（带#），符合主题
    5. 整体风格：{style}，语言活泼有网感，避免太官方
    """

    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": f"帮我生成一篇B站视频的标题+文案，主题是：{prompt}"}
        ],
        "temperature": 0.9,
        "max_tokens": 1000
    }

    try:
        # 超时设置，避免卡住
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json() if e.response.headers.get(
            'Content-Type') == 'application/json' else e.response.text
        return f"❌ API调用失败（HTTP {e.response.status_code}）：{error_detail}"
    except requests.exceptions.Timeout:
        return "❌ 请求超时，请检查网络或稍后重试"
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

        # 优化版复制按钮（稳定复制到剪贴板）
        if st.button("📋 复制全部内容"):
            # 安全转义所有特殊字符
            escaped_result = (
                result.replace("\\", "\\\\")
                .replace("`", "\\`")
                .replace("\n", "\\n")
                .replace('"', '\\"')
                .replace("'", "\\'")
                .replace("$", "\\$")
            )
            # 嵌入JS实现剪贴板复制
            st.components.v1.html(f"""
                <script>
                    (async function() {{
                        try {{
                            await navigator.clipboard.writeText(`{escaped_result}`);
                            alert('✅ 内容已成功复制到剪贴板！');
                        }} catch (err) {{
                            // 降级方案：创建临时文本框复制
                            const textarea = document.createElement('textarea');
                            textarea.value = `{escaped_result}`;
                            document.body.appendChild(textarea);
                            textarea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textarea);
                            alert('✅ 已通过兼容模式复制到剪贴板！');
                        }}
                    }})();
                </script>
            """, height=0, width=0)

# 底部提示
st.info("💡 提示：API密钥需从Moonshot（Kimi）官网申请，生成的内容可根据需求自行修改")

# 可选：添加调试信息（如需排查问题可取消注释）
# st.sidebar.markdown("### 🛠️ 调试信息")
# st.sidebar.write(f"Python版本: {os.sys.version}")
# st.sidebar.write(f"Requests版本: {requests.__version__}")
# st.sidebar.write(f"Streamlit版本: {st.__version__}")