import streamlit as st
import google.generativeai as genai

# 디자인 설정
st.set_page_config(page_title="AI 수학 문제 생성기", layout="centered")

# API 키 연결 확인
try:
    # Secrets에서 키를 가져올 때 앞뒤 공백을 제거(.strip())해서 혹시 모를 실수를 방지합니다.
    raw_key = st.secrets["GOOGLE_API_KEY"]
    api_key = raw_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ API 키를 설정하는 중 오류가 발생했습니다: {e}")
    st.stop()

# 2022 개정 교육과정 데이터
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통)": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하"]
}

st.title("🧮 AI 수학 문제 생성기")
st.caption("2022 개정 교육과정 완벽 반영")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("학년 선택", list(curriculum.keys()))
with col2:
    unit = st.selectbox("단원 선택", curriculum[grade])

diff = st.select_slider("난이도", options=["하", "중", "상"])
q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"], horizontal=True)

if st.button("✨ 문제 생성하기", use_container_width=True):
    with st.spinner('AI가 문제를 출제 중입니다...'):
        try:
            # [수정 포인트] 가장 안정적인 모델 이름을 직접 명시
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"대한민국 수학교사로서 2022 개정 교육과정 {grade} {unit} 단원의 문제를 {diff} 난이도로 {q_type} 형태로 출제해줘. 풀이와 정답도 포함해."
            
            response = model.generate_content(prompt)
            st.success("문제 생성 완료!")
            st.markdown("---")
            st.markdown(response.text)
            
        except Exception as e:
            # 에러가 나면 어떤 모델을 쓸 수 있는지 리스트를 보여줍니다 (진단용)
            st.error(f"❌ 에러 발생: {e}")
            st.info("사용 가능한 모델 리스트를 확인해 보세요:")
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.write(models)
