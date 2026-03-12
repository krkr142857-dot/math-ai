import streamlit as st
import google.generativeai as genai
import time

# 1. 페이지 설정 및 디자인 개선 (CSS 적용)
st.set_page_config(page_title="AI 수학 문제 생성기", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .problem-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. API 키 보안 연결
try:
    raw_key = st.secrets["GOOGLE_API_KEY"]
    api_key = raw_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ API 키 설정 오류가 발생했습니다. 관리자 설정을 확인하세요.")
    st.stop()

# 3. 2022 개정 교육과정 데이터
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통)": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하"]
}

# 4. 상단 헤더
st.title("🎓 AI 수학 문제 스마트 생성기")
st.info("2022 개정 교육과정을 기반으로 맞춤형 문항을 설계합니다.")

# 5. 입력 인터페이스 레이아웃
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("학년", list(curriculum.keys()))
    with col2:
        unit = st.selectbox("단원", curriculum[grade])

    diff = st.select_slider("문항 난이도", options=["하", "중", "상"])
    q_type = st.radio("문항 유형", ["객관식", "단답형", "서술형"], horizontal=True)

st.markdown("---")

# 6. 문제 생성 및 자동 재시도 로직
if st.button("🚀 문항 생성 시작"):
    placeholder = st.empty() # 카운트다운 등을 표시할 공간
    
    # 가용 모델 자동 탐색
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0] if available_models else "")

    if not target_model:
        st.error("사용 가능한 AI 모델을 찾을 수 없습니다.")
    else:
        max_retries = 3
        success = False
        
        for i in range(max_retries):
            try:
                with st.spinner(f'문항을 생성 중입니다... (시도 {i+1}/{max_retries})'):
                    model = genai.GenerativeModel(target_model)
                    prompt = f"""
                    대한민국 수학교사로서 2022 개정 교육과정 {grade} {unit} 단원의 문제를 {diff} 난이도로 {q_type} 형태로 출제해줘.
                    - 수학 기호와 수식은 반드시 LaTeX 형식을 사용해줘.
                    - 문제, 풀이, 정답을 명확히 구분해서 작성해줘.
                    """
                    response = model.generate_content(prompt)
                    
                    # 성공 시 결과 출력
                    st.success("✅ 문항 생성이 완료되었습니다.")
                    st.markdown(f'<div class="problem-box">{response.text}</div>', unsafe_allow_html=True)
                    success = True
                    break
            
            except Exception as e:
                if "429" in str(e): # 사용량 제한 에러인 경우
                    if i < max_retries - 1:
                        for seconds in range(5, 0, -1):
                            placeholder.warning(f"⚠️ 접속자가 많아 {seconds}초 후 자동으로 다시 시도합니다...")
                            time.sleep(1)
                        placeholder.empty()
                    else:
                        st.error("❌ 현재 접속자가 너무 많아 요청을 처리할 수 없습니다. 잠시 후 다시 시도해 주세요.")
                else:
                    st.error(f"❌ 오류 발생: {e}")
                    break
