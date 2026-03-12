import streamlit as st
import google.generativeai as genai
import json
import re

# 1. 페이지 설정 및 사용자 제공 CSS 테마 완벽 이식
st.set_page_config(page_title="수학 문제 생성기", layout="wide")

# CSS: 제공하신 HTML의 모든 스타일(색상, 폰트, 레이아웃)을 1:1로 매칭
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&family=Noto+Serif+KR:wght@400;600&family=Caveat:wght@700&display=swap');
    
    :root {
      --bg: #f5f6fa; --sidebar-bg: #ffffff; --card-bg: #ffffff; --border: #e5e7eb;
      --text: #111827; --accent: #4f46e5; --red: #dc2626; --green: #16a34a;
    }
    
    .stApp { background: var(--bg); font-family: 'Noto Sans KR', sans-serif; }
    
    /* 헤더 스타일 */
    .custom-header {
        background: #fff; border-bottom: 1px solid var(--border);
        padding: 10px 24px; display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 10px;
    }

    /* 빨간펜 O/X 스탬프 (제공하신 디자인 반영) */
    .ox-stamp {
        position: absolute; top: 10px; left: 15px;
        font-family: 'Caveat', cursive; font-size: 80px; font-weight: 700;
        line-height: 1; pointer-events: none; z-index: 99; color: #e11d48; opacity: 0.7;
    }

    /* 문제 카드 (Center Panel) */
    .prob-card {
        background: var(--card-bg); border: 1.5px solid var(--border);
        border-radius: 14px; padding: 25px; position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px;
        font-family: 'Noto Serif KR', serif; line-height: 2.1; color: var(--text);
    }
    
    /* 우측 패널 하단 고정 키패드 */
    .fixed-keypad {
        background: #ffffff; border: 2px solid var(--accent);
        padding: 15px; border-radius: 12px;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.05); margin-top: 10px;
    }
    
    /* LaTeX 깨짐 방지 스타일 */
    .katex { font-size: 1.1em !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. AI 모델 설정
def load_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        return genai.GenerativeModel(target)
    except: return None

# 3. 세션 상태 관리 (데이터 유지)
if 'problems' not in st.session_state: st.session_state.problems = []
if 'user_ans' not in st.session_state: st.session_state.user_ans = {}
if 'results' not in st.session_state: st.session_state.results = {}
if 'input_text' not in st.session_state: st.session_state.input_text = ""

# 교육과정 데이터
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통수학)": ["다항식", "방정식과 부등식", "경우의 수", "행렬", "집합과 명제"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하", "미적분II"]
}

# 4. 상단 헤더 (HTML 구조 이식)
st.markdown("""
    <div class="custom-header">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; background:#4f46e5; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:900;">∑</div>
            <div>
                <div style="font-weight:800; font-size:15px; color:#111827;">수학 문제 생성기</div>
                <div style="font-size:10.5px; color:#9ca3af;">2022 개정 교육과정 · 수학교육과 캡스톤디자인</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. [1분할: 왼쪽 사이드바]
with st.sidebar:
    st.markdown("### ⚙ 문제 설정")
    sel_grade = st.selectbox("학년 선택", list(curriculum.keys()))
    sel_unit = st.selectbox("단원 선택", curriculum[sel_grade])
    
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(표준)", "1등급(심화)"]
    sel_diff = st.select_slider("목표 등급 설정", options=diff_labels)
    
    sel_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    sel_count = st.number_input("문항 수", 1, 5, 3)

    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        model = load_model()
        if model:
            with st.spinner('AI가 문제를 설계 중입니다...'):
                prompt = f"""
                수학교사로서 {sel_grade} {sel_unit} 단원의 문제를 {sel_diff} 수준으로 {sel_type} {sel_count}개를 출제해.
                모든 수식은 반드시 LaTeX($)로 감싸고 역슬래시는 반드시 두 번(\\\\) 써서 출력해.
                JSON 형식: {{ "probs": [ {{ "q": "문제", "choices": ["보기5개"], "hints": ["힌트3개"], "concepts": "개념", "solution": "풀이", "answer": "정답" }} ] }}
                """
                try:
                    res = model.generate_content(prompt).text
                    data = json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())
                    st.session_state.problems = data['probs']
                    st.session_state.results = {}
                    st.session_state.user_ans = {}
                    st.session_state.input_text = ""
                except: st.error("출제 실패. 다시 시도해 주세요.")

# 6. 메인 콘텐츠 (2분할: 센터, 3분할: 우측)
if st.session_state.problems:
    col_center, col_right = st.columns([1.5, 1])

    with col_center:
        for i, prob in enumerate(st.session_state.problems):
            st.markdown('<div class="prob-card">', unsafe_allow_html=True)
            
            # O/X 스탬프
            res_status = st.session_state.results.get(i)
            if res_status == "correct": st.markdown('<div class="ox-stamp">○</div>', unsafe_allow_html=True)
            elif res_status == "wrong": st.markdown('<div class="ox-stamp">✕</div>', unsafe_allow_html=True)
            
            st.markdown(f"<small style='color:#4f46e5; font-weight:700;'>문제 {i+1}</small>", unsafe_allow_html=True)
            st.write(prob['q'])
            
            if sel_type == "객관식":
                st.session_state.user_ans[i] = st.radio(f"보기 ({i+1})", prob['choices'], key=f"r_{i}", index=None)
            else:
                st.session_state.user_ans[i] = st.text_area(f"답안 입력 ({i+1})", key=f"t_{i}", value=st.session_state.input_text if i==0 else "")

            # 버튼 영역
            c1, c2 = st.columns(2)
            if c1.button(f"✅ 채점", key=f"g_{i}"):
                if sel_type == "객관식":
                    st.session_state.results[i] = "correct" if st.session_state.user_ans[i] == prob['answer'] else "wrong"
                else:
                    model = load_model()
                    check = model.generate_content(f"문제:{prob['q']}\n정답:{prob['answer']}\n학생답:{st.session_state.user_ans[i]}\n맞으면 '정답' 아니면 '오답'이라고만 해.").text
                    st.session_state.results[i] = "correct" if "정답" in check else "wrong"
                st.rerun()
            if c2.button(f"↺ 다시", key=f"re_{i}"):
                st.session_state.results[i] = None
                st.rerun()
            
            # 힌트/개념을 2분할(문제 하단)에 배치
            with st.expander("💡 힌트 및 핵심 개념"):
                st.write(f"**힌트:** {prob['hints'][0]}")
                st.info(f"**개념:** {prob['concepts']}")
            
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("### 💡 학습 가이드")
        p = st.session_state.problems[0] # 첫 번째 문제 기준 해설 표시
        
        with st.container():
            st.markdown("##### 🔓 정답 및 상세 해설")
            if st.button("해설 보기"):
                st.success(f"**정답:** {p['answer']}")
                st.write(prob['solution'])
        
        st.write("---")
        # [고정형 수식 키패드]
        st.markdown('<div class="fixed-keypad">', unsafe_allow_html=True)
        st.markdown("<small style='color:#4f46e5; font-weight:700;'>🎹 수식 입력기</small>", unsafe_allow_html=True)
        k_cols = st.columns(4)
        syms = {"√": "\\sqrt{ }", "分": "\\frac{ }{ }", "xⁿ": "^n", "π": "\\pi", "sin": "\\sin", "∑": "\\sum", "lim": "\\lim", "∫": "\\int"}
        for idx, (lab, val) in enumerate(syms.items()):
            if k_cols[idx%4].button(lab, key=f"k_{lab}"):
                st.code(val) # 클릭 시 코드를 보여줌
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align:center; padding-top:100px; color:#9ca3af;"><h1>📝</h1>왼쪽에서 설정을 선택하고<br>문제 생성하기를 누르세요</div>', unsafe_allow_html=True)
