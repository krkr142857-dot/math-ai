import streamlit as st
import google.generativeai as genai
import time

# 1. 페이지 설정 및 디자인 (3분할 레이아웃 최적화)
st.set_page_config(page_title="AI 수학 인터랙티브 학습관", layout="wide")

# CSS: 수식 입력기 버튼 및 레이아웃 스타일
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; margin-bottom: 5px; }
    .hint-box { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; margin-bottom: 10px; }
    .concept-box { background-color: #fff9db; padding: 15px; border-radius: 10px; border-left: 5px solid #fcc419; }
    .math-btn { font-size: 18px !important; background-color: #f1f3f5 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. API 키 보안 연결
try:
    api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ API 키 설정 오류")
    st.stop()

# 3. 데이터 및 상태 초기화
if 'problem_data' not in st.session_state:
    st.session_state.problem_data = None
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = ""

curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통)": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하"]
}

# --- [1분할: 사이드바] 설정 영역 ---
with st.sidebar:
    st.title("⚙️ 문제 설정")
    grade = st.selectbox("학년", list(curriculum.keys()))
    unit = st.selectbox("단원", curriculum[grade])
    diff = st.select_slider("난이도", options=["하", "중", "상"])
    q_type = st.radio("유형", ["객관식", "단답형", "서술형"])
    
    if st.button("✨ 새 문제 출제", type="primary"):
        with st.spinner('AI 교사가 문제를 설계 중...'):
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_model = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])
                model = genai.GenerativeModel(target_model)
                
                # 라텍스 깨짐 방지를 위해 명확한 가이드라인 제시
                prompt = f"""
                대한민국 수학교사로서 2022 개정 교육과정 {grade} {unit} 단원의 문제를 {diff} 난이도로 {q_type} 형태로 출제해줘.
                형식은 반드시 아래와 같은 JSON 구조로 답변해줘:
                {{
                    "problem": "문제 내용 (수식은 반드시 $ 기호로 감싸줘)",
                    "options": ["객관식일 경우만 5개 항목, 아니면 빈 리스트"],
                    "hint1": "살짝 던져주는 힌트",
                    "hint2": "조금 더 구체적인 힌트",
                    "hint3": "결정적인 힌트(거의 정답 수준)",
                    "concepts": "관련 공식 및 핵심 개념 설명",
                    "solution": "상세 풀이 과정",
                    "answer": "최종 정답"
                }}
                라텍스 기호 사용 시 역슬래시를 두 번 써서 깨짐을 방지해줘.
                """
                response = model.generate_content(prompt)
                # 텍스트에서 JSON 부분만 추출 (가장 안정적인 방식)
                import json
                raw_text = response.text.replace('```json', '').replace('```', '').strip()
                st.session_state.problem_data = json.loads(raw_text)
                st.session_state.user_answer = "" # 답변 초기화
            except Exception as e:
                st.error(f"출제 실패: {e}")

# 메인 화면 레이아웃 (2분할과 3분할)
if st.session_state.problem_data:
    col2, col3 = st.columns([1.5, 1])

    # --- [2분할: 센터] 문제 및 입력 영역 ---
    with col2:
        st.subheader("📝 오늘의 문제")
        p = st.session_state.problem_data
        st.markdown(f"#### {p['problem']}")
        
        st.write("---")
        
        # 답변 입력 영역
        if q_type == "객관식":
            st.session_state.user_answer = st.radio("정답 선택", p['options'])
        else:
            # 수식 입력 도구 (가상 키보드)
            st.write("🎹 수학 기호 도우미 (클릭 시 입력창에 삽입)")
            m_cols = st.columns(6)
            symbols = {"x²": "^2", "√": "sqrt()", "π": "pi", "÷": "/", "×": "*", "分数": "(/)"}
            
            def add_symbol(s):
                st.session_state.user_answer += s

            for i, (label, sym) in enumerate(symbols.items()):
                if m_cols[i % 6].button(label, key=f"btn_{i}"):
                    st.session_state.user_answer += sym
            
            st.session_state.user_answer = st.text_area("답변을 입력하세요", value=st.session_state.user_answer, height=150)
        
        if st.button("✅ 채점하기"):
            if st.session_state.user_answer.strip() == str(p['answer']).strip():
                st.balloons()
                st.success("정답입니다! 완벽해요!")
            else:
                st.error("다시 한번 생각해볼까요? 오른쪽 힌트를 참고해보세요.")

    # --- [3분할: 우측] 힌트 및 해설 영역 ---
    with col3:
        with st.expander("💡 1단계 힌트 (살짝)", expanded=False):
            st.info(p['hint1'])
        with st.expander("🔍 2단계 힌트 (자세히)", expanded=False):
            st.info(p['hint2'])
        with st.expander("📢 3단계 힌트 (결정적)", expanded=False):
            st.warning(p['hint3'])
        
        st.write("---")
        with st.expander("📚 관련 공식 및 개념", expanded=True):
            st.markdown(f"<div class='concept-box'>{p['concepts']}</div>", unsafe_allow_html=True)
            
        st.write("---")
        if st.checkbox("📖 정답 및 전체 풀이 보기"):
            st.write(f"**정답: {p['answer']}**")
            st.write(p['solution'])

else:
    st.write("👈 왼쪽 사이드바에서 설정을 마친 후 [새 문제 출제] 버튼을 눌러주세요!")
