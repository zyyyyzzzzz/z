import streamlit as st
import os
# ========== 适配LangChain v0.1+ 最新路径 ==========
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# =================================================

# 页面配置 - B站风格
st.set_page_config(page_title="B站热门话题助手", layout="wide", page_icon="📺")

# 左侧栏：API密钥输入
with st.sidebar:
    st.title("📝 API配置")
    api_key = st.text_input("请输入Kimi API密钥", type="password")
    if not api_key:
        st.warning("⚠️ 请先输入API密钥才能使用")

    # 可选：模型选择（LangChain特性）
    model_option = st.selectbox(
        "选择Kimi模型：",
        ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        index=0
    )

# 主页面
st.title("📺 B站热门话题助手")
st.subheader("一键生成B站视频标题+文案+标签（LangChain稳定版）", divider="rainbow")
topic = st.text_input(
    "请输入B站创作主题：",
    placeholder="例如：“2025年度游戏盘点”、“新手学Python避坑指南”、“原神新版本开荒攻略”"
)
style = st.selectbox(
    "选择创作风格：",
    ["轻松搞笑", "干货教学", "情绪共鸣", "吐槽点评", "沉浸式体验"]
)
generate_btn = st.button("🚀 生成内容", disabled=not (api_key and topic))


# LangChain核心函数（适配最新版）
def generate_bilibili_content(topic, style, api_key, model_name):
    """使用LangChain v0.1+ 调用Kimi API生成B站内容"""
    try:
        # 1. 初始化LangChain的OpenAI兼容模型（适配Kimi）
        llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.9,
            max_tokens=1000,
            openai_api_key=api_key,
            openai_api_base="https://api.moonshot.cn/v1",  # Kimi API地址
            request_timeout=30  # 超时设置
        )

        # 2. 构建LangChain提示词模板（核心特性）
        system_template = """
        你是B站资深UP主，擅长生成符合B站用户喜好的内容：
        1. 标题要吸睛，带B站热门梗/数字/反问，比如“千万别再踩坑了！”“3分钟搞定！”
        2. 文案口语化，像和观众聊天，多用“宝子们”“家人们”“敲黑板”等B站常用语
        3. 结构清晰：开头钩子+核心内容+结尾互动（求三连/评论）
        4. 附带5个以上B站热门标签（带#），符合主题
        5. 整体风格：{style}，语言活泼有网感，避免太官方
        """

        human_template = "帮我生成一篇B站视频的标题+文案，主题是：{topic}"

        # 3. 创建提示词模板链（LangChain v0.1+ 标准写法）
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template)
        ])

        # 4. 格式化提示词并调用模型（最新版invoke方法）
        formatted_prompt = prompt.format_messages(style=style, topic=topic)
        response = llm.invoke(formatted_prompt)

        return response.content

    except Exception as e:
        error_msg = f"❌ 生成失败：{str(e)}"
        st.error(error_msg)
        return error_msg


# 生成按钮逻辑
if generate_btn:
    with st.spinner("🎬 LangChain正在调用Kimi API生成内容..."):
        result = generate_bilibili_content(topic, style, api_key, model_option)
        st.subheader("✅ 生成结果（LangChain稳定版）：")
        st.markdown("---")
        st.write(result)
        st.markdown("---")

        # 复制功能（稳定版）
        if st.button("📋 复制全部内容"):
            # 安全转义特殊字符
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
                            // 降级方案：兼容老旧浏览器
                            const textarea = document.createElement('textarea');
                            textarea.value = `{escaped_result}`;
                            document.body.appendChild(textarea);
                            textarea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textarea);
                            alert('✅ 兼容模式：内容已复制到剪贴板！');
                        }}
                    }})();
                </script>
            """, height=0, width=0)

# 底部提示
st.info("💡 提示：API密钥需从Moonshot（Kimi）官网申请，本版本适配LangChain v0.1+ 最新版")

# LangChain版本信息（修复__version__错误）
with st.expander("🔍 版本信息与特性说明"):
    import langchain
    import pkg_resources  # 使用Python标准库获取版本


    # 安全获取版本信息的方法
    def get_package_version(package_name):
        try:
            return pkg_resources.get_distribution(package_name).version
        except:
            return "未知版本"


    langchain_version = get_package_version("langchain")
    langchain_core_version = get_package_version("langchain-core")
    langchain_openai_version = get_package_version("langchain-openai")

    st.markdown(f"""
    - LangChain版本：{langchain_version}
    - LangChain-Core版本：{langchain_core_version}
    - LangChain-OpenAI版本：{langchain_openai_version}
    - 核心特性：
      1. 适配v0.1+新路径：`langchain_core.prompts` 替代旧版 `langchain.prompts`
      2. 使用标准`invoke()`方法调用模型
      3. 统一的提示词模板管理，支持参数化注入
      4. 兼容Kimi API的OpenAI接口规范，稳定调用
    """)