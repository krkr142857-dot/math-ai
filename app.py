import streamlit as st
import google.generativeai as genai

# 1. 배경 설정 (깔끔한 디자인)
st.set_page_config(page_title="AI 수학 문제 생성기", layout="centered")

# 2. 보안 설정: API 키를 안전하게 가져오기 (나중에 설정창에 입력할 값)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.warning("⚠️ API 키가 설정되지 않았습니다. 관리자 페이지에서 설정해주세요.")
    st.stop()

# 3. 데이터 설정 (2022 개정 교육과정)
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통)": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하"]
}

# 4. 화면 구성 (심플하게)
st.title("🧮 AI 수학 문제 생성기")
st.caption("2022 개정 교육과정을 준수합니다.")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("학년 선택", list(curriculum.keys()))
with col2:
    unit = st.selectbox("단원 선택", curriculum[grade])

diff = st.select_slider("난이도", options=["하", "중", "상"])
q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"], horizontal=True)

# 5. 문제 생성 버튼 로직
if st.button("✨ 문제 생성하기", use_container_width=True):
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # AI에게 보낼 정교한 지시문(프롬프트)
    prompt = f"""
    너는 대한민국 수학교사야. 2022 개정 교육과정의 {grade} {unit} 단원에서 문제를 출제해줘.
    - 난이도: {diff}
    - 유형: {q_type}
    - 조건: 문제와 함께 상세한 풀이 과정, 정답을 포함해줘. 수학 기호는 LaTeX 형식을 사용해줘.
    """
    
    with st.spinner('AI가 문제를 출제 중입니다...'):
        response = model.generate_content(prompt)
        st.success("문제 생성 완료!")
        st.markdown("---")
        st.markdown(response.text)


