import streamlit as st
import google.generativeai as genai
import time
import json

# 1. 페이지 설정 및 시각적 이펙트(CSS)
st.set_page_config(page_title="AI 수학 인터랙티브 플랫폼", layout="wide")

st.markdown("""
    <style>
    /* 채점 이펙트 */
    .correct-circle { color: #2ecc71; font-size: 100px; position: absolute; top: -20px; left: 50%; transform: translateX(-50%); opacity: 0.8; font-weight: bold; }
    .wrong-slash { color: #e74c3c; font-size: 120px; position: absolute; top: -30px; left: 50%; transform: translateX(-50%); opacity: 0.8; font-weight: bold; }
    
    /* 레이아웃 및 버튼 */
    .stButton>button { width: 100%; border-radius: 8px; }
    .math-keypad button { background-color: #f8f9fa !important; border: 1px solid #dee2e6 !important; font-family: 'serif'; }
    .hint-area { background-color: #f1f3f5; padding: 15px; border-radius: 10px; border-left: 5px solid #4dabf7; }
    .concept-area { background-color: #fff9db; padding: 15px; border-radius: 10px; border-left: 5px solid #fab005; }
    </style>
    """, unsafe_allow_html=True)

# 2. API 보안 연결
try:
    api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ API 키 설정 오류")
    st.stop()

# 3. 세션 상태 관리 (새로고침 시 데이터 유지)
if 'problem_data' not in st.session_state: st.session_state.problem_data = None
if 'user_answer' not in st.session_state: st.session_state.user_answer = ""
if 'grade_status' not in st.session_state: st.session_state.grade_status = None # 'correct', 'wrong', None
if 'ai_feedback' not in st.session_state: st.session_state.ai_feedback = ""

# 4. 학년 및 단원 데이터 (2022 개정)
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년": ["대수", "미적분I", "확률과 통계", "기하"]
}

# --- [1분할: 사이드바 설정] ---
with st.sidebar:
    st.title("🎓 설정 및 출제")
    # 커서 지워짐 방지를 위해 st.form 사용 고려 가능하나, selectbox는 기본 기능이므로 유지
    sel_grade = st.selectbox("학년 선택", list(curriculum.keys()))
    sel_unit = st.selectbox("단원 선택", curriculum[sel_grade])
    
    # 내신/수능 등급 기반 난이도
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(심화)", "1등급(고난도)"]
    sel_diff = st.select_slider("목표 등급 선택", options=diff_labels)
    
    sel_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    
    if st.button("✨ 새 문제 생성", type="primary"):
        with st.spinner('AI가 단원 성취기준에 맞춰 출제 중...'):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                수학교사로서 2022 개정 교육과정 {sel_grade} {sel_unit} 단원의 문제를 {sel_diff} 수준에 맞춰 {sel_type}으로 출제해.
                수식은 반드시 LaTeX($)를 사용하고 역슬래시는 두 번(\\\\) 써서 JSON 오류를 방지해.
                형식:
                {{
                    "problem": "문제 내용",
                    "options": ["객관식일 때만 5개 항목, 아니면 빈 리스트"],
                    "hint1": "1단계 힌트(살짝)", "hint2": "2단계 힌트(중간)", "hint3": "3단계 힌트(결정적)",
                    "concepts": "관련 공식 및 핵심 개념",
                    "solution": "전체 풀이", "answer": "최종 정답"
                }}
                """
                response = model.generate_content(prompt)
                raw_json = response.text.replace('```json', '').replace('```', '').strip()
                st.session_state.problem_data = json.loads(raw_json)
                # 상태 초기화
                st.session_state.user_answer = ""
                st.session_state.grade_status = None
                st.session_state.ai_feedback = ""
            except:
                st.error("출제 중 오류가 발생했습니다. 다시 시도해주세요.")

# 메인 화면 (2분할 & 3분할)
if st.session_state.problem_data:
    p = st.session_state.problem_data
    col2, col3 = st.columns([1.5, 1])

    # --- [2분할: 문제 및 입력 영역] ---
    with col2:
        st.subheader("📝 Question")
        
        # 채점 이펙트 표시
        if st.session_state.grade_status == "correct":
            st.markdown('<div class="correct-circle">○</div>', unsafe_allow_html=True)
        elif st.session_state.grade_status == "wrong":
            st.markdown('<div class="wrong-slash">／</div>', unsafe_allow_html=True)

        st.write(p['problem'])
        st.write("---")

        # 입력 영역
        if sel_type == "객관식":
            st.session_state.user_answer = st.radio("정답 선택", p['options'], index=None if st.session_state.user_answer == "" else p['options'].index(st.session_state.user_answer))
        else:
            # 공학용 수식 입력기 (버튼들)
            st.write("🎹 수학 기호 입력기")
            btn_cols = st.columns(6)
            # LaTeX 기호들
            math_symbols = {"√": "\\sqrt{ }", "x²": "^2", "÷": "/", "π": "\\pi", "sin": "\\sin", "cos": "\\cos"}
            for i, (lab, sym) in enumerate(math_symbols.items()):
                if btn_cols[i].button(lab, key=f"sym_{i}"):
                    st.session_state.user_answer += sym
            
            # 텍스트 입력창 (단답/서술형)
            st.session_state.user_answer = st.text_area("답변을 입력하세요 (수식은 ^, / 등을 사용 가능)", value=st.session_state.user_answer)

        # 채점 및 다시풀기 버튼
        btn_col_a, btn_col_b = st.columns(2)
        if btn_col_a.button("✅ 제출 및 채점"):
            if sel_type == "객관식":
                if st.session_state.user_answer == p['answer'] or st.session_state.user_answer in p['answer']:
                    st.session_state.grade_status = "correct"
                else: st.session_state.grade_status = "wrong"
            else:
                # [서술형 AI 채점 엔진]
                with st.spinner('AI가 풀이 과정을 분석 중...'):
                    judge_model = genai.GenerativeModel('gemini-1.5-flash')
                    judge_prompt = f"문제: {p['problem']}\n정답: {p['answer']}\n학생답안: {st.session_state.user_answer}\n위 답안이 수학적으로 맞는지 '정답' 혹은 '오답'으로 첫 단어에 대답하고 이유를 설명해."
                    res = judge_model.generate_content(judge_prompt).text
                    if "정답" in res[:10]: st.session_state.grade_status = "correct"
                    else: st.session_state.grade_status = "wrong"
                    st.session_state.ai_feedback = res

        if btn_col_b.button("🔄 다시 풀기"):
            st.session_state.user_answer = ""
            st.session_state.grade_status = None
            st.session_state.ai_feedback = ""
            st.rerun()

        if st.session_state.ai_feedback:
            st.info(f"💡 AI 채점평: {st.session_state.ai_feedback}")

    # --- [3분할: 힌트 및 해설 영역] ---
    with col3:
        st.subheader("💡 Study Guide")
        h1 = st.expander("1단계 힌트 (기초)")
        h1.write(p['hint1'])
        h2 = st.expander("2단계 힌트 (심화)")
        h2.write(p['hint2'])
        h3 = st.expander("3단계 힌트 (결정적)")
        h3.write(p['hint3'])

        st.write("---")
        st.markdown("### 📚 관련 개념 및 공식")
        st.markdown(f'<div class="concept-area">{p["concepts"]}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🔓 정답 및 풀이 확인"):
            st.write(f"**정답:** {p['answer']}")
            st.write(f"**풀이:** {p['solution']}")

else:
    st.info("👈 왼쪽 사이드바에서 학년과 난이도를 선택한 후 [새 문제 생성]을 눌러주세요.")
