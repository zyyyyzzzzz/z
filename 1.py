import streamlit as st
import requests

# 设置页面标题
st.set_page_config(page_title="小红书文案AI写作助手", layout="wide")

# 侧边栏：输入API密钥
with st.sidebar:
    st.title("API配置")
    api_key = st.text_input("请输入API密钥", type="password")  # 隐藏输入

# 主页面：输入小红书主题 + 生成按钮
st.title("小红书文案AI写作助手~")
topic = st.text_input("请输入小红书主题：")

if st.button("开始写作"):
    # 校验输入
    if not api_key:
        st.error("请先在侧边栏输入API密钥！")
    elif not topic:
        st.error("请输入小红书主题！")
    else:
        # 调用Kimi API（需替换为Kimi实际接口）
        try:
            # Kimi API的请求参数（参考官方文档，此处为示例格式）
            url = "https://api.moonshot.cn/v1/chat/completions"  # Kimi接口地址（以官方为准）
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"  # 鉴权方式（以官方为准）
            }
            data = {
                "model": "moonshot-v1-8k",  # Kimi模型名（以官方为准）
                "messages": [
                    {"role": "system", "content": "你是小红书文案助手，需要写出活泼、有网感、带emoji的小红书文案，结构包含标题、正文、标签。"},
                    {"role": "user", "content": f"帮我写一篇关于「{topic}」的小红书文案"}
                ]
            }

            # 发送请求
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功
            result = response.json()
            content = result["choices"][0]["message"]["content"]  # 提取文案

            # 展示结果
            st.success("文案生成完成！")
            st.markdown(content)

        except requests.exceptions.RequestException as e:
            st.error(f"API调用失败：{str(e)}")