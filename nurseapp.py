import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드 (UTF-8 인코딩 명시)
try:
    load_dotenv(encoding='utf-8')
except Exception as e:
    # .env 파일이 없거나 읽을 수 없는 경우 무시 (환경변수 사용)
    pass

# 페이지 설정
st.set_page_config(
    page_title="간호사 AI 상담사",
    page_icon="🏥",
    layout="wide"
)

# Colab 환경 확인 및 API 키 가져오기
def get_api_key():
    # 1. .env 파일에서 로드된 환경변수 확인 (로컬 환경)
    api_key = os.getenv('OPENAI_API_KEY')
    
    # 2. Colab 환경인 경우 userdata에서 가져오기
    if not api_key:
        try:
            from google.colab import userdata
            api_key = userdata.get('OPENAI_API_KEY')
        except ImportError:
            # Colab이 아닌 경우
            pass
    
    return api_key

# OpenAI 클라이언트 초기화
@st.cache_resource
def init_client():
    api_key = get_api_key()
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다.")
        st.info("""
        **로컬 환경:**
        - 프로젝트 루트에 `.env` 파일을 생성하고 다음을 추가하세요:
        ```
        OPENAI_API_KEY=your-api-key-here
        ```
        - 또는 `.env.example` 파일을 참고하세요.
        
        **Colab 환경:**
        - userdata에 API 키를 저장하세요.
        """)
        st.stop()
    return OpenAI(api_key=api_key)

client = init_client()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """# Role
당신은 병원에서 근무하는 전문 간호사로서, 환자와 보호자가 이해하기 쉽도록 의사의 진료 내용을 친절하고 명확하게 설명하는 역할을 맡고 있습니다. 보호자는 의학 지식이 전혀 없다는 전제를 항상 기억하세요.

# Context
- 의료 설명을 할 때 절대 전문 용어나 어려운 단어를 사용하지 마세요. 반드시 쉬운 일상 언어로 풀어 설명해야 합니다.
- 전달받은 진단, 검사 결과, 처방, 주의사항 등 이미 제공된 의사의 설명만을 다룹니다. 본인이 직접 진단하거나 추가적인 치료를 지시하지 않습니다.
- 설명이 부족하거나 불확실한 정보가 있다면, 내용을 추측하거나 임의로 보충하지 말고 "궁금하신 점은 병원에 다시 문의해 주세요"와 같이 안내합니다.
- 설명 내용은 5~10문장 내외의 자연스러운 한국어 대화체로 작성합니다.
- 항상 차분하고 공감하는 태도와 어조를 유지하세요.

# 출력 형식
- [이해를 돕는 쉬운 설명] (5~10문장, 자연스럽고 공손한 대화체)
- [불확실하거나 추가 확인 필요시 안내 문구] (필요할 경우에만)

**중요:**
- 반드시 전문 용어를 풀어서 설명하세요.
- 절대 추가 진단이나 치료 제안, 임의의 해석을 하지 마세요.
- 필요한 경우 병원 문의를 안내하세요.

(중요 목표: 보호자가 걱정 없이 진료 내용을 쉽게 이해할 수 있도록 돕는 것입니다.)"""
        },
        {
            "role": "assistant",
            "content": "안녕하세요! 👋 저는 여러분의 건강을 도와드리는 간호사입니다. 어떤 병이나 증상에 대해 알고 싶으신가요? 진료 내용이나 검사 결과에 대해 궁금한 점이 있으시면 언제든 물어보세요. 쉽고 친절하게 설명해드리겠습니다."
        }
    ]

# 말풍선 스타일 CSS
st.markdown("""
<style>
    .speech-bubble {
        position: relative;
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        min-width: 200px;
        max-width: 600px;
        width: fit-content;
        margin-left: 20px;
        font-size: 16px;
        line-height: 1.6;
        color: black;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .speech-bubble:before {
        content: "";
        position: absolute;
        left: -20px;
        top: 30px;
        width: 0;
        height: 0;
        border-top: 15px solid transparent;
        border-bottom: 15px solid transparent;
        border-right: 20px solid white;
    }
    .nurse-container {
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding: 20px;
        min-height: 400px;
    }
    .nurse-image {
        flex-shrink: 0;
    }
    .chat-area {
        flex: 1;
        max-width: 800px;
    }
    .user-question {
        background: #e3f2fd;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        text-align: right;
        font-size: 15px;
        color: black;
        min-width: 200px;
        max-width: 600px;
        width: fit-content;
        margin-left: auto;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 (최소화)
with st.sidebar:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": """# Role
당신은 병원에서 근무하는 전문 간호사로서, 환자와 보호자가 이해하기 쉽도록 의사의 진료 내용을 친절하고 명확하게 설명하는 역할을 맡고 있습니다. 보호자는 의학 지식이 전혀 없다는 전제를 항상 기억하세요.

# Context
- 의료 설명을 할 때 절대 전문 용어나 어려운 단어를 사용하지 마세요. 반드시 쉬운 일상 언어로 풀어 설명해야 합니다.
- 전달받은 진단, 검사 결과, 처방, 주의사항 등 이미 제공된 의사의 설명만을 다룹니다. 본인이 직접 진단하거나 추가적인 치료를 지시하지 않습니다.
- 설명이 부족하거나 불확실한 정보가 있다면, 내용을 추측하거나 임의로 보충하지 말고 "궁금하신 점은 병원에 다시 문의해 주세요"와 같이 안내합니다.
- 설명 내용은 5~10문장 내외의 자연스러운 한국어 대화체로 작성합니다.
- 항상 차분하고 공감하는 태도와 어조를 유지하세요.

# 출력 형식
- [이해를 돕는 쉬운 설명] (5~10문장, 자연스럽고 공손한 대화체)
- [불확실하거나 추가 확인 필요시 안내 문구] (필요할 경우에만)

**중요:**
- 반드시 전문 용어를 풀어서 설명하세요.
- 절대 추가 진단이나 치료 제안, 임의의 해석을 하지 마세요.
- 필요한 경우 병원 문의를 안내하세요.

(중요 목표: 보호자가 걱정 없이 진료 내용을 쉽게 이해할 수 있도록 돕는 것입니다.)"""
            },
            {
                "role": "assistant",
                "content": "안녕하세요! 👋 저는 여러분의 건강을 도와드리는 간호사입니다. 어떤 병이나 증상에 대해 알고 싶으신가요? 진료 내용이나 검사 결과에 대해 궁금한 점이 있으시면 언제든 물어보세요. 쉽고 친절하게 설명해드리겠습니다."
            }
        ]
        st.rerun()

# 메인 레이아웃 - 간호사 캐릭터와 말풍선
col1, col2 = st.columns([1, 2])

with col1:
    # 간호사 이미지 (왼쪽)
    st.image("nurse.png", width=300)

with col2:
    # 말풍선 영역 (오른쪽)
    # 사용자 질문과 간호사 답변 표시
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        
        if message["role"] == "user":
            st.markdown(f'<div class="user-question">💬 {message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f'<div class="speech-bubble">{message["content"]}</div>', unsafe_allow_html=True)

# 사용자 입력
if prompt := st.chat_input("진료 내용에 대해 궁금한 점을 입력해주세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 어시스턴트 응답 생성
    with st.spinner("답변을 생성하고 있습니다..."):
        try:
            # OpenAI API 호출
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.5,
                max_tokens=2048
            )
            
            assistant_response = response.choices[0].message.content
            
            # 어시스턴트 메시지 추가
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # 페이지 새로고침하여 말풍선 표시
            st.rerun()
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

