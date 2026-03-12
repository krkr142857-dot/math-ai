import streamlit as st
import google.generativeai as genai
import json
import re

# 1. 페이지 설정
st.set_page_config(page_title="수학 문제 생성기", layout="wide")

# 2. AI 모델 설정 및 문제 생성 함수
def generate_math_problems(grade, unit, diff, q_type, count):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        model = genai.GenerativeModel(target_model)
        
        prompt = f"""
        수학교사로서 {grade} {unit} 단원의 문제를 {diff} 수준으로 {q_type} {count}개를 출제해.
        모든 수식은 반드시 LaTeX($)로 감싸고 역슬래시는 반드시 두 번(\\\\) 써서 출력해.
        반드시 아래 JSON 구조로만 응답해:
        [
            {{
                "type": ["{q_type}"],
                "q": "문제 내용 (라텍스 포함)",
                "choices": ["보기1", "보기2", "보기3", "보기4", "보기5"],
                "correct_idx": 0,
                "answer": "정답(라텍스)",
                "short_answer": "채점용텍스트",
                "solution": "풀이과정",
                "hints": ["힌트1", "힌트2", "힌트3"],
                "terms": "핵심용어",
                "standard": "성취기준"
            }}
        ]
        """
        response = model.generate_content(prompt)
        # JSON 데이터만 추출
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        return json.loads(match.group())
    except Exception as e:
        st.error(f"AI 생성 오류: {e}")
        return None

# 3. 사이드바 UI (학년/단원/난이도/유형 설정)
with st.sidebar:
    st.markdown("### ⚙️ 문제 설정")
    grade = st.selectbox("학년", ["중학교 1학년", "중학교 2학년", "중학교 3학년", "고등학교 1학년", "고등학교 2/3학년"])
    unit = st.text_input("단원명", "다항식의 연산")
    diff_labels = ["기초(7-9등급)", "기본(4-6등급)", "표준(3등급)", "심화(2등급)", "최고(1등급)"]
    diff = st.select_slider("난이도", options=diff_labels)
    q_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    count = st.number_input("문항 수", 1, 5, 3)
    
    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        problems = generate_math_problems(grade, unit, diff, q_type, count)
        if problems:
            st.session_state.current_bank = problems

# 4. 메인 화면: 질문자님이 주신 HTML 디자인에 데이터 주입
if 'current_bank' in st.session_state:
    # 파이썬 리스트를 자바스크립트용 JSON 문자열로 변환
    json_data = json.dumps(st.session_state.current_bank, ensure_ascii=False)
    
    # [중요] f-string의 중괄호 오류를 피하기 위해 .replace() 방식을 사용합니다.
    html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>수학 문제 생성기</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=Noto+Serif+KR:wght@400;600&family=Caveat:wght@700&display=swap" rel="stylesheet"/>
<style>
/* 질문자님이 제공한 CSS 코드 그대로 유지 */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root { --bg: #f5f6fa; --sidebar-bg: #ffffff; --card-bg: #ffffff; --border: #e5e7eb; --text: #111827; --accent: #4f46e5; --green: #16a34a; --red: #dc2626; }
body { background: var(--bg); font-family: 'Noto Sans KR', sans-serif; color: var(--text); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
.workspace { flex: 1; display: flex; overflow: hidden; }
.center-panel { flex: 1; overflow-y: auto; padding: 20px 16px; display: flex; flex-direction: column; gap: 14px; }
.right-panel { width: 370px; background: var(--sidebar-bg); border-left: 1px solid var(--border); overflow-y: auto; padding: 20px 18px; }
.prob-card { background: var(--card-bg); border: 1.5px solid var(--border); border-radius: 14px; padding: 22px; cursor: pointer; position: relative; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.prob-card.selected { border-color: var(--accent); }
.ox-stamp { position: absolute; top: 12px; left: 14px; font-family: 'Caveat', cursive; font-size: 36px; font-weight: 700; opacity: 0; pointer-events: none; }
.ox-stamp.show-o { color: #e11d48; opacity: 1; }
.ox-stamp.show-x { color: #e11d48; opacity: 1; }
.card-q { font-family: 'Noto Serif KR', serif; font-size: 16px; line-height: 2.1; }
.choice-opt { padding: 10px 14px; border-radius: 9px; cursor: pointer; border: 1.5px solid #f0f1f5; background: var(--bg); margin-top: 7px; transition: all .13s; }
.choice-opt.picked { border-color: var(--accent); background: #ede9fe; }
.choice-opt.revealed-correct { border-color: var(--green) !important; background: #f0fdf4 !important; }
.choice-opt.revealed-wrong { border-color: var(--red) !important; background: #fef2f2 !important; }
.hint-body, .ans-box, .sol-box { display: none; padding: 10px; border-radius: 7px; margin-top: 5px; font-size: 13px; }
.hint-body.open, .ans-box.open, .sol-box.open { display: block; }
.ans-box { background: #f0fdf4; color: var(--green); }
.sol-box { background: #fffbeb; color: #78350f; white-space: pre-wrap; line-height: 1.8; }
.math-keypad { margin-top: 20px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; border-top: 2px solid var(--accent); padding-top: 10px; }
.key-btn { padding: 8px; font-size: 11px; background: white; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; }
</style>
</head>
<body>
<header style="flex-shrink:0; background:#fff; border-bottom:1px solid var(--border); padding:0 24px; height:52px; display:flex; align-items:center; justify-content:space-between;">
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="width:32px; height:32px; background:var(--accent); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:900;">∑</div>
        <div style="font-weight:800; font-size:15px;">수학 문제 생성기</div>
    </div>
    <div style="font-size:11px; color:var(--text-sub); border:1px solid var(--border); border-radius:6px; padding:3px 10px;">수학교육과 캡스톤디자인</div>
</header>
<div class="workspace">
    <div class="center-panel" id="centerPanel"></div>
    <div class="right-panel">
        <div id="rightPanelContents">
            <div style="text-align:center; color:#9ca3af; padding-top:50px;">문제를 클릭하면<br>해설이 나옵니다</div>
        </div>
        <div class="math-keypad">
            <button class="key-btn" onclick="alert('복사됨: \\\\sqrt{}')">√</button>
            <button class="key-btn" onclick="alert('복사됨: \\\\frac{}{}')">분수</button>
            <button class="key-btn" onclick="alert('복사됨: ^n')">제곱</button>
            <button class="key-btn" onclick="alert('복사됨: \\\\pi')">π</button>
            <button class="key-btn" onclick="alert('복사됨: \\\\sin')">sin</button>
            <button class="key-btn" onclick="alert('복사됨: \\\\lim')">lim</button>
            <button class="key-btn" onclick="alert('복사됨: \\\\sum')">∑</button>
            <button class="key-btn" onclick="alert('복사됨: \\\\int')">∫</button>
        </div>
    </div>
</div>
<script>
const BANK = AI_DATA_HOLDER;
let selectedIdx = -1;
const states = BANK.map(() => ({ picked: -1, submitted: false }));

function renderProblems() {
    const cp = document.getElementById('centerPanel');
    cp.innerHTML = BANK.map((p, i) => `
        <div class="prob-card" id="card-${i}" onclick="selectCard(${i})">
            <div class="ox-stamp" id="stamp-${i}"></div>
            <div style="font-size:10px; color:var(--accent); font-weight:700; margin-bottom:8px;">문항 ${i+1}</div>
            <div class="card-q">${p.q}</div>
            ${p.choices.length > 0 ? 
                `<div style="margin-top:10px;">${p.choices.map((c, ci) => `<div class="choice-opt" id="opt-${i}-${ci}" onclick="pick(${i}, ${ci})">${ci+1}. ${c}</div>`).join('')}</div>` :
                `<input type="text" id="input-${i}" style="width:100%; padding:10px; margin-top:10px; border:1px solid #ddd; border-radius:8px;" placeholder="답안 입력">`
            }
            <button onclick="submit(${i})" style="margin-top:15px; width:100%; padding:10px; background:var(--accent); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:700;">채점하기</button>
        </div>
    `).join('');
    renderMathInElement(cp, { delimiters: [{left: "$", right: "$", display: false}] });
}

window.selectCard = function(idx) {
    selectedIdx = idx;
    document.querySelectorAll('.prob-card').forEach((c, i) => c.classList.toggle('selected', i === idx));
    const p = BANK[idx];
    document.getElementById('rightPanelContents').innerHTML = `
        <div style="font-size:10px; color:var(--accent); font-weight:700;">💡 해설 가이드</div>
        <div style="margin-top:15px;">
            <div style="font-size:12px; color:#666;">힌트</div>
            <div class="hint-body open">${p.hints[0]}</div>
        </div>
        <div style="margin-top:15px;">
            <button onclick="this.nextElementSibling.classList.toggle('open')" style="width:100%; padding:8px; background:#f0fdf4; border:1px solid #86efac; color:#16a34a; border-radius:8px; cursor:pointer;">정답 확인</button>
            <div class="ans-box">정답: ${p.answer}</div>
        </div>
        <div style="margin-top:10px;">
            <button onclick="this.nextElementSibling.classList.toggle('open')" style="width:100%; padding:8px; background:#fffbeb; border:1px solid #fcd34d; color:#d97706; border-radius:8px; cursor:pointer;">풀이 보기</button>
            <div class="sol-box">${p.solution}</div>
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
    } else {
        const val = document.getElementById('input-'+idx).value.replace(/\s/g,'');
        correct = (val === p.short_answer.replace(/\s/g,''));
    }
    stamp.textContent = correct ? '○' : '✕';
    stamp.className = 'ox-stamp ' + (correct ? 'show-o' : 'show-x');
    states[idx].submitted = true;
}

renderProblems();
</script>
</body>
</html>
    """.replace("AI_DATA_HOLDER", json_data) # f-string 대신 .replace()를 써서 { } 충돌 방지
    
    st.components.v1.html(html_template, height=900, scrolling=True)

else:
    st.markdown("""
        <div style="text-align:center; padding-top:150px; color:#9ca3af; font-family:'Noto Sans KR';">
            <h1 style="font-size:50px;">∑</h1>
            <p>왼쪽 사이드바에서 조건을 설정하고<br><b>[문제 생성하기]</b>를 누르면 AI가 문제를 출제합니다.</p>
        </div>
    """, unsafe_allow_html=True)
