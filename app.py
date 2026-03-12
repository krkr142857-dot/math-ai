import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 페이지 설정 및 디자인 (클로드 스타일 + 커스텀 CSS)
st.set_page_config(page_title="AI 수학 인터랙티브 플랫폼", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Noto+Serif+KR&display=swap');
    
    .main { background-color: #f5f6fa; }
    
    /* 빨간펜 이펙트 */
    .stamp-o { color: #e11d48; font-size: 100px; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); opacity: 0.6; font-weight: bold; z-index: 10; pointer-events: none; font-family: 'cursive'; }
    .stamp-x { color: #e11d48; font-size: 100px; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); opacity: 0.6; font-weight: bold; z-index: 10; pointer-events: none; font-family: 'serif'; }

    /* 문제 카드 스타일 */
    .prob-card { background: white; border: 1.5px solid #e5e7eb; border-radius: 14px; padding: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; position: relative; }
    
    /* 3분할 레이아웃 조절 */
    .stColumn { overflow: visible !important; }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e5e7eb; padding-top: 20px; }
    
    /* 수식 입력기 하단 고정 느낌 */
    .keypad-container { background: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; padding: 10px; margin-top: 20px; }
    .stButton>button { width: 100%; border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

# 2. API 보안 연결 및 오류 방지
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        return genai.GenerativeModel(name)
    except:
        st.error("⚠️ API 연결에 실패했습니다. 키 설정을 확인하세요.")
        return None

# 3. 데이터 및 세션 상태
if 'problem_data' not in st.session_state: st.session_state.problem_data = None
if 'user_answer' not in st.session_state: st.session_state.user_answer = ""
if 'grade_status' not in st.session_state: st.session_state.grade_status = None
if 'ai_feedback' not in st.session_state: st.session_state.ai_feedback = ""

# 2022 개정 교육과정 기준 학년 및 과목 데이터
curriculum_data = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통수학1,2)": ["다항식", "방정식과 부등식", "경우의 수", "행렬", "집합과 명제", "함수와 그래프"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하", "미적분II"]
}

# 4. [1분할: 사이드바 설정 영역]
with st.sidebar:
    st.title("∑ 수학 문제 생성기")
    st.caption("2022 개정 교육과정 반영")
    
    grade = st.selectbox("학년 선택", list(curriculum_data.keys()))
    unit = st.selectbox("단원 선택", curriculum_data[grade])
    
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(심화)", "1등급(고난도)"]
    difficulty = st.select_slider("난이도 설정", options=diff_labels)
    
    q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    q_count = st.number_input("문항 수", 1, 5, 1)

    if st.button("✦ 문제 생성하기", type="primary"):
        model = get_model()
        if model:
            with st.spinner('문제를 설계 중입니다...'):
                prompt = f"""
                수학교사로서 {grade} {unit} 단원의 문제를 {difficulty} 수준으로 {q_type} {q_count}개를 출제해.
                수식은 반드시 LaTeX($)로 감싸고, JSON 내부에서 역슬래시가 깨지지 않게 두 번(\\\\) 써야 해.
                형식:
                {{
                    "problem": "문제 내용 (라텍스 포함)",
                    "options": ["객관식일 때만 5개, 아니면 빈 리스트"],
                    "hint1": "살짝 힌트", "hint2": "조금 더 힌트", "hint3": "결정적 힌트",
                    "concepts": "핵심 공식 및 개념 정리",
                    "solution": "상세 풀이 과정",
                    "answer": "정답"
                }}
                답변은 반드시 이 JSON 객체 1개만 출력해.
                """
                try:
                    res = model.generate_content(prompt).text
                    clean_json = re.search(r'\{.*\}', res, re.DOTALL).group()
                    st.session_state.problem_data = json.loads(clean_json)
                    st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""
                except:
                    st.error("출제 중 오류가 발생했습니다. 다시 눌러주세요.")

# 메인 레이아웃 (2분할: 센터, 3분할: 우측)
if st.session_state.problem_data:
    col_center, col_right = st.columns([1.5, 1])
    p = st.session_state.problem_data

    # --- [2분할: 센터] 문제 및 힌트/개념 ---
    with col_center:
        st.markdown(f'<div class="prob-card">', unsafe_allow_html=True)
        # O/X 이펙트 (X자로 수정)
        if st.session_state.grade_status == "correct":
            st.markdown('<div class="stamp-o">○</div>', unsafe_allow_html=True)
        elif st.session_state.grade_status == "wrong":
            st.markdown('<div class="stamp-x">✕</div>', unsafe_allow_html=True)

        st.subheader("📝 문제")
        st.write(p['problem'])
        
        # 힌트 및 개념을 문제 하단에 배치
        with st.expander("💡 단계별 힌트 보기"):
            st.info(f"1단계: {p['hint1']}")
            st.info(f"2단계: {p['hint2']}")
            st.warning(f"3단계(결정적): {p['hint3']}")
        
        with st.expander("📚 핵심 공식 및 관련 개념"):
            st.success(p['concepts'])
            
        st.markdown('</div>', unsafe_allow_html=True)

        # 답변 입력창
        if q_type == "객관식":
            st.session_state.user_answer = st.radio("정답을 선택하세요", p['options'], index=None if st.session_state.user_answer == "" else p['options'].index(st.session_state.user_answer))
        else:
            st.session_state.user_answer = st.text_area("답변을 입력하세요", value=st.session_state.user_answer, height=150)

        # 채점/다시풀기 버튼
        b1, b2 = st.columns(2)
        if b1.button("✅ 제출 및 채점"):
            if q_type == "객관식":
                st.session_state.grade_status = "correct" if st.session_state.user_answer == p['answer'] else "wrong"
            else:
                model = get_model()
                res = model.generate_content(f"문제: {p['problem']}\n정답: {p['answer']}\n학생답: {st.session_state.user_answer}\n채점해줘. '정답' 혹은 '오답'으로 시작.").text
                st.session_state.grade_status = "correct" if "정답" in res[:10] else "wrong"
                st.session_state.ai_feedback = res
        
        if b2.button("🔄 다시 풀기"):
            st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""; st.rerun()

    # --- [3분할: 우측] 정답/풀이(스크롤) + 가상 키보드(고정) ---
    with col_right:
        # 상단: 정답 및 풀이 (스크롤 가능하게 expander 활용)
        st.subheader("📋 해설지")
        with st.container():
            if st.button("🔓 정답 및 풀이 공개"):
                st.success(f"**정답:** {p['answer']}")
                st.write(p['solution'])
                if st.session_state.ai_feedback:
                    st.info(f"AI 채점평: {st.session_state.ai_feedback}")
        
        st.write("---")
        
        # 하단: 수학 기호 입력기 (고정된 느낌으로 하단 배치)
        st.markdown('<div class="keypad-container">', unsafe_allow_html=True)
        st.write("🎹 수학 기호 입력기")
        k_col1, k_col2, k_col3, k_col4 = st.columns(4)
        syms = {
            "√": "\\sqrt{ }", "sin": "\\sin ", "cos": "\\cos ", "tan": "\\tan ",
            "分": "\\frac{ }{ }", "lim": "\\lim_{x \\to \\infty}", "∑": "\\sum_{k=1}^{n}", "θ": "\\theta",
            "xⁿ": "^n", "°": "^{\\circ}", "π": "\\pi ", "∫": "\\int "
        }
        for i, (lab, val) in enumerate(syms.items()):
            cols = [k_col1, k_col2, k_col3, k_col4]
            if cols[i%4].button(lab, key=f"key_{lab}"):
                st.session_state.user_answer += val
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 왼쪽 사이드바에서 설정을 완료하고 [문제 생성하기]를 눌러주세요.")
