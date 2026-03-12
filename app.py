import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="AI 수학 인터랙티브 플랫폼", layout="wide")

st.markdown("""
    <style>
    .stamp-o { color: #e11d48; font-size: 100px; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); opacity: 0.6; font-weight: bold; z-index: 10; pointer-events: none; }
    .stamp-x { color: #e11d48; font-size: 100px; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); opacity: 0.6; font-weight: bold; z-index: 10; pointer-events: none; }
    .prob-card { background: white; border: 1.5px solid #e5e7eb; border-radius: 14px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; position: relative; min-height: 200px; }
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e5e7eb; }
    .keypad-container { background: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; padding: 10px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. API 보안 연결
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        return genai.GenerativeModel(name)
    except:
        return None

# 3. 세션 상태 관리
if 'problem_data' not in st.session_state: st.session_state.problem_data = None
if 'user_answer' not in st.session_state: st.session_state.user_answer = ""
if 'grade_status' not in st.session_state: st.session_state.grade_status = None
if 'ai_feedback' not in st.session_state: st.session_state.ai_feedback = ""

curriculum_data = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통수학1,2)": ["다항식", "방정식과 부등식", "경우의 수", "행렬", "집합과 명제", "함수와 그래프"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하", "미적분II"]
}

# --- [1분할: 사이드바] ---
with st.sidebar:
    st.title("∑ 수학 문제 생성기")
    grade = st.selectbox("학년 선택", list(curriculum_data.keys()))
    unit = st.selectbox("단원 선택", curriculum_data[grade])
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(심화)", "1등급(고난도)"]
    difficulty = st.select_slider("난이도 설정", options=diff_labels)
    q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])

    if st.button("✦ 문제 생성하기", type="primary"):
        model = get_model()
        if model:
            with st.spinner('문제를 설계 중입니다...'):
                prompt = f"""
                수학교사로서 {grade} {unit} 단원의 문제를 {difficulty} 수준으로 {q_type} 형태로 1개 출제해.
                모든 수식은 LaTeX($)로 감싸고, JSON 내부에서 역슬래시가 깨지지 않게 두 번(\\\\) 써.
                반드시 아래 JSON 형식으로만 응답해:
                {{
                    "problem": "문제 내용",
                    "options": ["객관식일 때만 5개, 아니면 빈 리스트"],
                    "hint1": "힌트1", "hint2": "힌트2", "hint3": "힌트3",
                    "concepts": "핵심 개념", "solution": "풀이", "answer": "정답"
                }}
                """
                try:
                    res = model.generate_content(prompt).text
                    json_str = re.search(r'\{.*\}', res, re.DOTALL).group()
                    st.session_state.problem_data = json.loads(json_str)
                    st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""
                except:
                    st.error("AI가 형식을 지키지 못했습니다. 다시 시도해 주세요.")

# --- 메인 화면 ---
if st.session_state.problem_data:
    p = st.session_state.problem_data
    col_center, col_right = st.columns([1.5, 1])

    with col_center:
        st.markdown('<div class="prob-card">', unsafe_allow_html=True)
        if st.session_state.grade_status == "correct": st.markdown('<div class="stamp-o">○</div>', unsafe_allow_html=True)
        elif st.session_state.grade_status == "wrong": st.markdown('<div class="stamp-x">✕</div>', unsafe_allow_html=True)

        st.subheader("📝 문제")
        # [.get() 방식을 사용하여 KeyError 방지]
        st.write(p.get('problem', '문제를 불러오는 데 실패했습니다.'))
        
        with st.expander("💡 힌트 및 개념"):
            st.info(f"1단계: {p.get('hint1', '힌트 없음')}")
            st.info(f"2단계: {p.get('hint2', '힌트 없음')}")
            st.warning(f"3단계: {p.get('hint3', '힌트 없음')}")
            st.success(f"핵심 개념: {p.get('concepts', '내용 없음')}")
        st.markdown('</div>', unsafe_allow_html=True)

        if q_type == "객관식":
            opts = p.get('options', [])
            st.session_state.user_answer = st.radio("정답 선택", opts, index=None if st.session_state.user_answer not in opts else opts.index(st.session_state.user_answer))
        else:
            st.session_state.user_answer = st.text_area("답변 입력", value=st.session_state.user_answer)

        b1, b2 = st.columns(2)
        if b1.button("✅ 제출 및 채점"):
            if q_type == "객관식":
                st.session_state.grade_status = "correct" if st.session_state.user_answer == p.get('answer') else "wrong"
            else:
                model = get_model()
                res = model.generate_content(f"문제: {p.get('problem')}\n정답: {p.get('answer')}\n학생답: {st.session_state.user_answer}\n채점해줘. '정답' 혹은 '오답'으로 시작.").text
                st.session_state.grade_status = "correct" if "정답" in res[:10] else "wrong"
                st.session_state.ai_feedback = res
        
        if b2.button("🔄 다시 풀기"):
            st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""; st.rerun()

    with col_right:
        st.subheader("📋 해설지")
        if st.button("🔓 정답 및 풀이 공개"):
            st.success(f"**정답:** {p.get('answer')}")
            st.write(p.get('solution', '풀이가 없습니다.'))
        
        st.write("---")
        st.markdown('<div class="keypad-container">', unsafe_allow_html=True)
        st.write("🎹 수학 기호 입력기")
        k_cols = st.columns(4)
        syms = {"√": "\\sqrt{ }", "sin": "\\sin ", "cos": "\\cos ", "tan": "\\tan ", "分": "\\frac{ }{ }", "lim": "\\lim_{x \\to \\infty}", "∑": "\\sum", "θ": "\\theta", "xⁿ": "^n", "π": "\\pi ", "∫": "\\int ", "°": "^{\\circ}"}
        for i, (lab, val) in enumerate(syms.items()):
            if k_cols[i%4].button(lab): st.session_state.user_answer += val
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("👈 왼쪽에서 설정을 완료하고 [문제 생성하기]를 눌러주세요.")
