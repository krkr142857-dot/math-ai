import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 디자인 설정 (보내주신 HTML/CSS 테마 완벽 반영)
st.set_page_config(page_title="AI 수학 인터랙티브 플랫폼", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Noto+Serif+KR&display=swap');
    
    :root { --accent: #4f46e5; --bg: #f5f6fa; }
    .stApp { background-color: var(--bg); }
    
    /* 빨간펜 X자 이펙트 */
    .stamp-o { color: #e11d48; font-size: 150px; position: absolute; top: 20%; left: 50%; transform: translate(-50%, -50%); opacity: 0.6; font-weight: bold; z-index: 99; pointer-events: none; }
    .stamp-x { color: #e11d48; font-size: 150px; position: absolute; top: 20%; left: 50%; transform: translate(-50%, -50%); opacity: 0.6; font-weight: bold; z-index: 99; pointer-events: none; }

    /* 문제 카드 (Center Panel 스타일) */
    .prob-card { 
        background: white; border: 1.5px solid #e5e7eb; border-radius: 14px; 
        padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; 
        position: relative; line-height: 2.1; font-family: 'Noto Serif KR', serif;
    }
    
    /* 수식 키패드 (한글 프로그램 스타일) */
    .keypad-box { 
        background: #ffffff; border: 1.5px solid #4f46e5; border-radius: 12px; 
        padding: 15px; margin-top: 10px; box-shadow: 0 -4px 10px rgba(79,70,229,0.1);
    }
    .math-btn-row { display: flex; gap: 5px; margin-bottom: 5px; justify-content: center; }
    
    /* 사이드바 */
    [data-testid="stSidebar"] { background-color: white; border-right: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

# 2. AI 모델 연결 (자동 이름 찾기 포함)
def get_ai_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        return genai.GenerativeModel(name)
    except: return None

# 3. 데이터 및 상태 관리
if 'problem_data' not in st.session_state: st.session_state.problem_data = None
if 'user_answer' not in st.session_state: st.session_state.user_answer = ""
if 'grade_status' not in st.session_state: st.session_state.grade_status = None
if 'ai_feedback' not in st.session_state: st.session_state.ai_feedback = ""

curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통수학1,2)": ["다항식", "방정식과 부등식", "경우의 수", "행렬", "집합과 명제", "함수와 그래프"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하", "미적분II"]
}

# --- [1분할: 사이드바 설정] ---
with st.sidebar:
    st.header("⚙ 문제 설정")
    sel_grade = st.selectbox("학년", list(curriculum.keys()))
    sel_unit = st.selectbox("단원", curriculum[sel_grade])
    diff = st.select_slider("목표 등급", options=["7~9등급", "4~6등급", "2~3등급", "1등급"])
    sel_type = st.radio("유형", ["객관식", "단답형", "서술형"])
    
    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        model = get_ai_model()
        if model:
            with st.spinner('문제를 생성 중...'):
                prompt = f"""
                수학교사로서 {sel_grade} {sel_unit} 단원 문제를 {diff} 수준으로 {sel_type}으로 1개 출제해.
                모든 수식은 반드시 LaTeX($)로 감싸고 역슬래시는 두 번(\\\\) 써서 JSON 오류를 막아.
                {{
                    "problem": "문제 내용",
                    "options": ["객관식 5개, 아니면 빈 리스트"],
                    "hint1": "살짝 힌트", "hint2": "중간 힌트", "hint3": "결정적 힌트",
                    "concepts": "공식 및 개념", "solution": "상세 풀이", "answer": "정답"
                }}
                답변은 JSON만 출력해.
                """
                try:
                    res = model.generate_content(prompt).text
                    match = re.search(r'\{.*\}', res, re.DOTALL)
                    st.session_state.problem_data = json.loads(match.group())
                    st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""
                except: st.error("출제 실패. 다시 시도해 주세요.")

# --- 메인 워크스페이스 ---
if st.session_state.problem_data:
    p = st.session_state.problem_data
    col_center, col_right = st.columns([1.6, 1])

    # --- [2분할: 센터 패널] ---
    with col_center:
        st.markdown('<div class="prob-card">', unsafe_allow_html=True)
        if st.session_state.grade_status == "correct": st.markdown('<div class="stamp-o">○</div>', unsafe_allow_html=True)
        elif st.session_state.grade_status == "wrong": st.markdown('<div class="stamp-x">✕</div>', unsafe_allow_html=True)
        
        st.subheader("📝 Question")
        st.write(p.get('problem', ''))
        
        # 문제 하단에 힌트 및 개념 배치
        with st.expander("💡 단계별 힌트 및 핵심 개념"):
            st.info(f"1단계: {p.get('hint1')}")
            st.info(f"2단계: {p.get('hint2')}")
            st.warning(f"3단계: {p.get('hint3')}")
            st.success(f"개념정리: {p.get('concepts')}")
        st.markdown('</div>', unsafe_allow_html=True)

        # 답변 입력 영역
        if sel_type == "객관식":
            st.session_state.user_answer = st.radio("정답 선택", p.get('options', []), index=None if st.session_state.user_answer == "" else p.get('options').index(st.session_state.user_answer))
        else:
            st.session_state.user_answer = st.text_area("답안 입력란", value=st.session_state.user_answer, height=150, help="아래 키패드를 이용해 수식을 입력하세요.")
            # [한글 수식 편집기용 실시간 미리보기]
            if st.session_state.user_answer:
                st.write("🔍 **수식 미리보기 (입력한 내용이 수식으로 보입니다)**")
                st.latex(st.session_state.user_answer.replace('\\\\', '\\'))

        # 채점 버튼
        c1, c2 = st.columns(2)
        if c1.button("✅ 제출 및 채점", type="primary"):
            if sel_type == "객관식":
                st.session_state.grade_status = "correct" if st.session_state.user_answer == p.get('answer') else "wrong"
            else:
                model = get_ai_model()
                res = model.generate_content(f"문제: {p.get('problem')}\n정답: {p.get('answer')}\n학생답: {st.session_state.user_answer}\n채점해줘. '정답' 혹은 '오답'으로 시작.").text
                st.session_state.grade_status = "correct" if "정답" in res[:10] else "wrong"
                st.session_state.ai_feedback = res
        if c2.button("🔄 다시 풀기"):
            st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""; st.rerun()

    # --- [3분할: 우측 패널] ---
    with col_right:
        st.subheader("💡 Study Guide")
        # 정답 및 풀이 (스크롤 가능 영역)
        with st.container():
            if st.button("🔓 정답 및 상세 풀이 공개"):
                st.success(f"**정답:** {p.get('answer')}")
                st.write(p.get('solution'))
                if st.session_state.ai_feedback: st.info(st.session_state.ai_feedback)
        
        st.write("---")
        
        # [고정형 수식 키패드 - 한글 프로그램 스타일]
        st.markdown('<div class="keypad-box">', unsafe_allow_html=True)
        st.write("🎹 **수식 편집 도구**")
        
        # 버튼들을 카테고리별로 배치
        def add_sym(s): st.session_state.user_answer += s

        r1 = st.columns(4)
        if r1[0].button("$\sqrt{\square}$"): st.session_state.user_answer += "\\sqrt{ }"; st.rerun()
        if r1[1].button("$\frac{\square}{\square}$"): st.session_state.user_answer += "\\frac{ }{ }"; st.rerun()
        if r1[2].button("$x^n$"): st.session_state.user_answer += "^n"; st.rerun()
        if r1[3].button("$\pi$"): st.session_state.user_answer += "\\pi"; st.rerun()
        
        r2 = st.columns(4)
        if r2[0].button("$\sin$"): st.session_state.user_answer += "\\sin "; st.rerun()
        if r2[1].button("$\cos$"): st.session_state.user_answer += "\\cos "; st.rerun()
        if r2[2].button("$\tan$"): st.session_state.user_answer += "\\tan "; st.rerun()
        if r2[3].button("$\theta$"): st.session_state.user_answer += "\\theta"; st.rerun()
        
        r3 = st.columns(4)
        if r3[0].button("$\lim$"): st.session_state.user_answer += "\\lim_{x \\to \\infty}"; st.rerun()
        if r3[1].button("$\sum$"): st.session_state.user_answer += "\\sum_{k=1}^{n}"; st.rerun()
        if r3[2].button("$\int$"): st.session_state.user_answer += "\\int "; st.rerun()
        if r3[3].button("$log$"): st.session_state.user_answer += "\\log "; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("기호를 클릭하면 입력창에 추가됩니다. 괄호 { } 사이에 숫자를 넣으세요.")

else:
    st.info("👈 왼쪽 설정에서 [문제 생성하기]를 누르면 학습이 시작됩니다.")
