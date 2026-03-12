import streamlit as st
import google.generativeai as genai

# 1. 디자인 설정
st.set_page_config(page_title="AI 수학 문제 생성기", layout="centered")

# 2. API 키 연결 (공백이나 따옴표 실수 방지 로직 강화)
try:
    raw_key = st.secrets["GOOGLE_API_KEY"]
    api_key = raw_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ API 키 설정 오류: {e}")
    st.stop()

# 3. 데이터 설정
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통)": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하"]
}

st.title("🧮 AI 수학 문제 생성기")
st.caption("2022 개정 교육과정 기반")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("학년 선택", list(curriculum.keys()))
with col2:
    unit = st.selectbox("단원 선택", curriculum[grade])

diff = st.select_slider("난이도", options=["하", "중", "상"])
q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"], horizontal=True)

# 4. 문제 생성 로직
if st.button("✨ 문제 생성하기", use_container_width=True):
    with st.spinner('AI 모델을 확인하고 문제를 생성 중입니다...'):
        try:
            # [핵심] 내 계정에서 사용 가능한 모델 중 'gemini'가 들어간 첫 번째 모델을 자동으로 찾습니다.
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 우선순위: 1.5-flash -> 1.5-pro -> 리스트의 첫 번째 모델
            target_model = ""
            for m_name in available_models:
                if "gemini-1.5-flash" in m_name:
                    target_model = m_name
                    break
            
            if not target_model:
                for m_name in available_models:
                    if "gemini" in m_name:
                        target_model = m_name
                        break
            
            if not target_model:
                st.error("사용 가능한 Gemini 모델을 찾을 수 없습니다.")
            else:
                # 선택된 모델로 문제 생성
                model = genai.GenerativeModel(target_model)
                prompt = f"대한민국 수학교사로서 2022 개정 교육과정 {grade} {unit} 단원의 문제를 {diff} 난이도로 {q_type} 형태로 출제해줘. 풀이와 정답도 포함해."
                
                response = model.generate_content(prompt)
                st.success(f"성공! (사용 모델: {target_model})")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"❌ 최종 에러 발생: {e}")
            st.info("이 메시지가 계속 뜨면 API 키 자체의 문제일 가능성이 높습니다.")
