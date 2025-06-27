from common import get_llm_response
import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile

# 运行：streamlit run ...

def get_answer(question:str)->str:
    try:
        client = OpenAI(api_key=api_key,base_url=base_url)
        system_prompt = (
            "你是一个机车又可爱、带有台妹口音的聊天助手，名叫小七，回答时语气活泼，偶尔撒娇，"
            "喜欢用可爱的表情符号和emoji表情，语言风格亲切又带点俏皮。"
            "非常善解人意，十分会提供情绪价值。"
        )
        stream = get_llm_response(
            client,
            model=model_name,
            system_prompt=system_prompt,
            user_prompt=question,
            stream=True
        )
        for chunk in stream:
            yield chunk.choices[0].delta.content or ''
    except:
        return "抱歉，请检查你的api_key哦。"


with st.sidebar:
    api_vendor = st.radio(label ="请选择API供应商",options =["OpenAI","DeepSeek"])
    if api_vendor == "OpenAI":
        base_url = 'https://twapi.openai-hk.com/v1'
        model_options = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
        ]
    elif api_vendor == "DeepSeek":
        base_url = 'https://api.deepseek.com'
        model_options = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k",
            'deepseek-chat',
            'deepseek-reasoner'
            'deepseek-text-v1',
        ]
    model_name = st.selectbox(label ="请选择模型",options = model_options)
    api_key = st.text_input(label ="请输入API Key",type ="password")

    # 新增上传文本文件功能
    uploaded_file = st.file_uploader("上传文本文件", type=["txt"])
    uploaded_content = ""
    if uploaded_file is not None:
        # 读取上传文件内容
        uploaded_content = uploaded_file.read().decode("utf-8")
        st.markdown("### 上传文件内容预览")
        st.text_area("", uploaded_content, height=200)

    # 新增上传音乐文件功能
    uploaded_music = st.file_uploader("上传音乐文件（mp3/wav等）", type=["mp3","wav","ogg","m4a"])
    if uploaded_music is not None:
        st.audio(uploaded_music, format='audio/mp3')

if 'messages' not in st.session_state:
    st.session_state['messages'] = [('ai','你好，我是你的聊天机器人，有什么事情都可以与我分享哦，我叫小七😀')]

st.write("### 聊天机器人小七")

if not api_key:
    st.error("请输入API Key")
    st.stop()

for role, content in st.session_state['messages']:
    st.chat_message(role).write(content)

user_input = st.chat_input(placeholder ="请输入")
if user_input:
    _, history = st.session_state['messages'][-1]
    st.session_state['messages'].append(('human',user_input))
    st.chat_message("human").write(user_input)
    with st.spinner("小七正在思考中哦~，请耐心等待..."):
        # 如果上传了文件，可以将文件内容附加到问题后面
        prompt = f'{history}, {user_input}'
        if uploaded_content:
            prompt += f"\n\n附加文件内容：\n{uploaded_content}"
        answer = get_answer(prompt)
        result = st.chat_message("ai").write_stream(answer)
        st.session_state['messages'].append(('ai',result))

        # 文本转语音播放按钮
        if result:
            if st.button("🔊 播放AI回复语音"):
                # 使用gTTS生成语音并播放
                tts = gTTS(text=result, lang='zh-cn')
                with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmpfile:
                    tts.save(tmpfile.name)
                    audio_bytes = tmpfile.read()
                    st.audio(audio_bytes, format="audio/mp3")