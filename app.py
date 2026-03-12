import streamlit as st
import google.generativeai as genai
import json
import re

# 1. 페이지 설정 (화면 너비 최대 활용)
st.set_page_config(page_title="수학 문제 생성기", layout="wide")

# 2. AI 모델 설정 및 문제 생성 로직
def generate_math_problems(grade, unit, diff, q_type, count):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        
        # 가용 모델 자동 탐색
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        model = genai.GenerativeModel(target_model)
        
        prompt = f"""
        수학교사로서 {grade} {unit} 단원의 문제를 {diff} 수준으로 {q_type} {count}개를 출제해.
        모든 수식은 반드시 LaTeX($)로 감싸고 역슬래시는 반드시 두 번(\\\\) 써서 출력해.
        반드시 아래 JSON 리스트 형식으로만 답변해. 다른 설명은 하지마.
        [
            {{
                "type": ["{q_type}"],
                "q": "문제 내용 (라텍스 포함)",
                "choices": ["보기1", "보기2", "보기3", "보기4", "보기5"],
                "correct_idx": 0,
                "answer": "정답(라텍스)",
                "short_answer": "채점용텍스트",
                "solution": "상세 풀이 과정",
                "hints": ["힌트1", "힌트2", "힌트3"],
                "terms": "핵심용어",
                "standard": "성취기준"
            }}
        ]
        """
        response = model.generate_content(prompt)
        # JSON 블록만 추출
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception as e:
        st.error(f"AI 생성 실패: {e}")
        return None

# 3. 사이드바 UI (2022 개정 교육과정 기준)
with st.sidebar:
    st.markdown("### ⚙️ 문제 설정")
    grade = st.selectbox("학년", ["중학교 1학년", "중학교 2학년", "중학교 3학년", "고등학교 1학년", "고등학교 2/3학년"])
    unit = st.text_input("단원명", "다항식의 연산")
    diff = st.select_slider("난이도", options=["7~9등급", "4~6등급", "2~3등급", "1등급"])
    q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    count = st.number_input("문항 수", 1, 5, 3)
    
    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        with st.spinner('AI가 문제를 출제하고 디자인을 입히는 중...'):
            problems = generate_math_problems(grade, unit, diff, q_type, count)
            if problems:
                st.session_state.current_bank = problems

# 4. 메인 화면 구성 (질문자님 HTML 디자인 주입)
if 'current_bank' in st.session_state:
    # 파이썬 데이터를 자바스크립트 변수로 변환 (한글 깨짐 방지)
    json_bank_data = json.dumps(st.session_state.current_bank, ensure_ascii=False)
    
    # 중괄호 문법 오류를 막기 위해 f-string을 쓰지 않고 문자열 치환(.replace) 사용
    html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"/>
<title>수학 문제 생성기</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;800&family=Noto+Serif+KR:wght@400;600&family=Caveat:wght@700&display=swap" rel="stylesheet"/>
<style>
/* CSS 스타일 완벽 이식 */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root { --bg: #f5f6fa; --sidebar-bg: #ffffff; --card-bg: #ffffff; --border: #e5e7eb; --text: #111827; --accent: #4f46e5; --green: #16a34a; --red: #dc2626; }
body { background: var(--bg); font-family: 'Noto Sans KR', sans-serif; color: var(--text); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
.workspace { flex: 1; display: flex; overflow: hidden; }
.center-panel { flex: 1; overflow-y: auto; padding: 20px 16px; display: flex; flex-direction: column; gap: 14px; }
.right-panel { width: 370px; background: var(--sidebar-bg); border-left: 1px solid var(--border); overflow-y: auto; padding: 20px 18px; display: flex; flex-direction: column; gap: 14px; }
.prob-card { background: var(--card-bg); border: 1.5px solid var(--border); border-radius: 14px; padding: 22px; cursor: pointer; position: relative; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: border-color .15s; }
.prob-card.selected { border-color: var(--accent); }
.ox-stamp { position: absolute; top: 12px; left: 14px; font-family: 'Caveat', cursive; font-size: 50px; font-weight: 700; opacity: 0; pointer-events: none; }
.ox-stamp.show-o { color: #e11d48; opacity: 1; }
.ox-stamp.show-x { color: #e11d48; opacity: 1; }
.card-q { font-family: 'Noto Serif KR', serif; font-size: 16px; line-height: 2.1; }
.choice-opt { padding: 10px 14px; border-radius: 9px; cursor: pointer; border: 1.5px solid #f0f1f5; background: var(--bg); margin-top: 7px; transition: all .13s; }
.choice-opt.picked { border-color: var(--accent); background: #ede9fe; }
.choice-opt.revealed-correct { border-color: var(--green) !important; background: #f0fdf4 !important; color: var(--green); }
.choice-opt.revealed-wrong { border-color: var(--red) !important; background: #fef2f2 !important; color: var(--red); }
.hint-body, .ans-box, .sol-box { display: none; padding: 12px; border-radius: 8px; margin-top: 8px; font-size: 13.5px; }
.hint-body.open, .ans-box.open, .sol-box.open { display: block; }
.ans-box { background: #f0fdf4; border: 1px solid var(--green); color: var(--green); }
.sol-box { background: #fffbeb; border: 1px solid #fcd34d; color: #78350f; white-space: pre-wrap; line-height: 1.8; }
.keypad { margin-top: 20px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; border-top: 2px solid var(--accent); padding-top: 15px; }
.k-btn { padding: 8px; font-size: 11px; background: #fff; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; }
</style>
</head>
<body>
<header style="flex-shrink:0; background:#fff; border-bottom:1px solid var(--border); padding:0 24px; height:52px; display:flex; align-items:center; justify-content:space-between;">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:32px; height:32px; background:var(--accent); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:900;">∑</div>
        <div style="font-weight:800; font-size:15px;">수학 문제 생성기</div>
    </div>
    <div style="font-size:11px; color:#6b7280; border:1px solid var(--border); border-radius:6px; padding:3px 10px; background:var(--bg);">수학교육과 캡스톤디자인</div>
</header>
<div class="workspace">
    <div class="center-panel" id="centerPanel"></div>
    <div class="right-panel">
        <div id="rightPanelContents">
            <div style="text-align:center; color:#9ca3af; padding-top:50px;">문제를 클릭하면<br>힌트·정답·풀이가 나옵니다</div>
        </div>
        <div class="keypad">
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\sqrt{}')">√</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\frac{}{}')">분수</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: ^n')">제곱</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\sin')">sin</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\lim')">lim</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\sum')">∑</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\int')">∫</button>
            <button class="k-btn" onclick="alert('입력창에 붙여넣으세요: \\\\theta')">θ</button>
        </div>
    </div>
</div>
<script>
const BANK = __AI_BANK_DATA__;
const states = BANK.map(() => ({ picked: -1, submitted: false }));

function renderProblems() {
    const cp = document.getElementById('centerPanel');
    cp.innerHTML = BANK.map((p, i) => `
        <div class="prob-card" id="card-${i}" onclick="selectCard(${i})">
            <div class="ox-stamp" id="stamp-${i}"></div>
            <div style="font-size:10px; color:var(--accent); font-weight:700; margin-bottom:10px;">QUESTION ${i+1}</div>
            <div class="card-q">${p.q}</div>
            ${p.choices.length > 0 ? 
                `<div style="margin-top:12px;">${p.choices.map((c, ci) => `
                    <div class="choice-opt" id="opt-${i}-${ci}" onclick="pick(${i}, ${ci})">
                        <span style="font-weight:700; margin-right:8px;">${ci+1}</span> ${c}
                    </div>`).join('')}</div>` :
                `<input type="text" id="input-${i}" style="width:100%; padding:12px; margin-top:15px; border:1px solid #ddd; border-radius:10px;" placeholder="정답을 입력하세요">`
            }
            <button onclick="submit(${i})" style="margin-top:20px; width:100%; padding:12px; background:var(--accent); color:white; border:none; border-radius:10px; cursor:pointer; font-weight:700;">채점하기</button>
        </div>
    `).join('');
    renderMathInElement(cp, { delimiters: [{left: "$", right: "$", display: false}] });
}

window.selectCard = function(idx) {
    document.querySelectorAll('.prob-card').forEach((c, i) => c.classList.toggle('selected', i === idx));
    const p = BANK[idx];
    document.getElementById('rightPanelContents').innerHTML = `
        <div style="font-size:10px; color:var(--accent); font-weight:700; letter-spacing:1px;">💡 SOLUTION GUIDE</div>
        <div style="margin-top:20px;">
            <div style="font-size:12px; color:#666; font-weight:700;">HINT</div>
            <div class="hint-body open">${p.hints[0]}</div>
        </div>
        <div style="margin-top:15px;">
            <button onclick="this.nextElementSibling.classList.toggle('open')" style="width:100%; padding:10px; background:#f0fdf4; border:1px solid var(--green); color:var(--green); border-radius:8px; cursor:pointer; font-weight:700;">정답 확인</button>
            <div class="ans-box">정답: ${p.answer}</div>
        </div>
        <div style="margin-top:10px;">
            <button onclick="this.nextElementSibling.classList.toggle('open')" style="width:100%; padding:10px; background:#fffbeb; border:1px solid #fcd34d; color:#d97706; border-radius:8px; cursor:pointer; font-weight:700;">풀이 과정 보기</button>
            <div class="sol-box">${p.solution}</div>
        </div>
        <div style="margin-top:15px; font-size:11px; color:#999; border-top:1px solid #eee; padding-top:10px;">
            핵심 용어: ${p.terms}<br>성취기준: ${p.standard}
        </div>
    `;
    renderMathInElement(document.getElementById('rightPanelContents'), { delimiters: [{left: "$", right: "$", display: false}] });
}

window.pick = function(pi, ci) {
    if (states[pi].submitted) return;
    states[pi].picked = ci;
    document.querySelectorAll('#card-'+pi+' .choice-opt').forEach((o, i) => o.classList.toggle('picked', i === ci));
}

window.submit = function(idx) {
    const p = BANK[idx];
    const stamp = document.getElementById('stamp-'+idx);
    let correct = false;
    if (p.choices.length > 0) {
        correct = (states[idx].picked === p.correct_idx);
        document.querySelectorAll('#card-'+idx+' .choice-opt').forEach((o, i) => {
            if (i === p.correct_idx) o.classList.add('revealed-correct');
            else if (i === states[idx].picked) o.classList.add('revealed-wrong');
        });
    } else {
        const val = document.getElementById('input-'+idx).value.replace(/\s/g,'').toLowerCase();
        correct = (val === p.short_answer.replace(/\s/g,'').toLowerCase());
    }
    stamp.textContent = correct ? '○' : '✕';
    stamp.className = 'ox-stamp ' + (correct ? 'show-o' : 'show-x');
    states[idx].submitted = true;
}

renderProblems();
</script>
</body>
</html>
    """.replace("__AI_BANK_DATA__", json_bank_data) # f-string 대신 .replace()를 사용해 오류 원천 차단
    
    st.components.v1.html(html_code, height=900, scrolling=True)

else:
    # 초기 안내 화면
    st.markdown("""
        <div style="text-align:center; padding-top:150px; color:#9ca3af; font-family:'Noto Sans KR';">
            <h1 style="font-size:50px;">∑</h1>
            <p style="font-size:15px;">왼쪽 사이드바에서 조건을 설정한 뒤<br><b>[문제 생성하기]</b> 버튼을 누르면 실시간 AI 출제가 시작됩니다.</p>
        </div>
    """, unsafe_allow_html=True)
