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
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #f5f6fa;
  --sidebar-bg: #ffffff;
  --card-bg: #ffffff;
  --border: #e5e7eb;
  --border-light: #f0f1f5;
  --text: #111827;
  --text-sub: #6b7280;
  --text-dim: #9ca3af;
  --accent: #4f46e5;
  --accent-light: #ede9fe;
  --accent-mid: #818cf8;
  --green: #16a34a;
  --green-bg: #f0fdf4;
  --green-border: #86efac;
  --red: #dc2626;
  --red-bg: #fef2f2;
  --red-border: #fca5a5;
  --yellow: #d97706;
  --yellow-bg: #fffbeb;
  --yellow-border: #fcd34d;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
}

body {
  background: var(--bg);
  font-family: 'Noto Sans KR', sans-serif;
  color: var(--text);
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ── 헤더 ── */
header {
  flex-shrink: 0;
  background: #fff;
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 50;
}
.logo { display: flex; align-items: center; gap: 10px; }
.logo-icon {
  width: 32px; height: 32px;
  background: var(--accent);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 900; color: #fff;
}
.logo-text { font-weight: 800; font-size: 15px; color: var(--text); }
.logo-sub { font-size: 10.5px; color: var(--text-dim); }
.header-badge {
  font-size: 11px; color: var(--text-sub);
  border: 1px solid var(--border);
  border-radius: 6px; padding: 3px 10px;
  background: var(--bg);
}

/* ── 3-패널 ── */
.workspace { flex: 1; display: flex; overflow: hidden; }

/* ── 왼쪽 사이드바 ── */
aside {
  width: 220px; flex-shrink: 0;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  overflow-y: auto; padding: 20px 16px 24px; gap: 20px;
}
aside::-webkit-scrollbar { width: 3px; }
aside::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.sb-label { font-size: 10px; color: var(--accent); letter-spacing: 2px; font-weight: 700; margin-bottom: 10px; }
.field-label { font-size: 11.5px; color: var(--text-sub); margin-bottom: 7px; font-weight: 500; }

.subunit-list { display: flex; flex-direction: column; gap: 4px; }
.subunit-btn {
  padding: 8px 10px; border-radius: 8px; cursor: pointer;
  border: 1.5px solid var(--border); background: transparent;
  color: var(--text-sub); font-family: inherit; font-size: 12.5px;
  transition: all .15s; text-align: left; line-height: 1.4;
}
.subunit-btn:hover { border-color: var(--accent-mid); color: var(--accent); background: var(--accent-light); }
.subunit-btn.active { border-color: var(--accent); background: var(--accent-light); color: var(--accent); font-weight: 600; }
.subunit-btn .sub-desc { font-size: 10px; color: var(--text-dim); margin-top: 2px; font-weight: 400; }

.level-row { display: flex; gap: 3px; }
.level-btn {
  flex: 1; padding: 7px 3px; border-radius: 6px; cursor: pointer;
  border: 1.5px solid var(--border); background: transparent;
  color: var(--text-dim); font-family: inherit; font-size: 10.5px;
  transition: all .15s; text-align: center;
}
.level-btn:hover { border-color: #aaa; color: var(--text-sub); }
.level-hint-text { font-size: 10px; color: var(--text-dim); margin-top: 6px; line-height: 1.4; }

.type-row { display: flex; gap: 4px; }
.type-btn {
  flex: 1; padding: 8px 4px; border-radius: 7px; cursor: pointer;
  border: 1.5px solid var(--border); background: transparent;
  color: var(--text-sub); font-family: inherit; font-size: 11px;
  transition: all .15s; text-align: center;
}
.type-btn:hover { border-color: var(--accent-mid); color: var(--accent); background: var(--accent-light); }
.type-btn.active { border-color: var(--accent); background: var(--accent-light); color: var(--accent); font-weight: 600; }

.count-ctrl { display: flex; align-items: center; gap: 12px; }
.count-btn {
  width: 28px; height: 28px; border-radius: 6px;
  border: 1.5px solid var(--border); background: var(--bg);
  color: var(--text-sub); font-size: 16px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.count-btn:hover { border-color: var(--accent); color: var(--accent); }
.count-num { font-size: 22px; font-weight: 800; color: var(--text); min-width: 24px; text-align: center; }

#generateBtn {
  width: 100%; padding: 12px; border-radius: 9px; border: none;
  background: var(--accent); color: #fff;
  font-size: 13.5px; font-weight: 700; cursor: pointer; font-family: inherit;
  transition: all .2s; margin-top: auto;
  box-shadow: 0 2px 8px rgba(79,70,229,0.3);
}
#generateBtn:hover { background: #4338ca; box-shadow: 0 4px 12px rgba(79,70,229,0.4); }
#generateBtn:active { transform: scale(.98); }

/* ── 가운데 패널 ── */
.center-panel {
  flex: 1; overflow-y: auto;
  padding: 20px 16px; display: flex; flex-direction: column; gap: 14px; min-width: 0;
}
.center-panel::-webkit-scrollbar { width: 4px; }
.center-panel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.empty-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: var(--text-dim); text-align: center; gap: 10px;
}
.empty-icon { font-size: 40px; }
.empty-text { font-size: 13.5px; line-height: 2; color: var(--text-sub); }

/* ── 문제 카드 ── */
.prob-card {
  background: var(--card-bg);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 22px 22px 18px;
  cursor: pointer;
  transition: border-color .15s, box-shadow .15s;
  position: relative;
  box-shadow: var(--shadow);
}
.prob-card:hover { border-color: var(--accent-mid); box-shadow: var(--shadow-md); }
.prob-card.selected { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(79,70,229,0.08), var(--shadow-md); }
.prob-card.state-correct { border-color: var(--green-border); }
.prob-card.state-wrong   { border-color: var(--red-border); }

/* 빨간펜 O/X */
.ox-stamp {
  position: absolute; top: 12px; left: 14px;
  font-family: 'Caveat', cursive;
  font-size: 36px; font-weight: 700;
  line-height: 1; pointer-events: none;
  opacity: 0; transition: opacity .25s;
}
.ox-stamp.show-o { color: #e11d48; opacity: 1; }
.ox-stamp.show-x { color: #e11d48; opacity: 1; }

.card-num {
  font-size: 10.5px; font-weight: 700; color: var(--accent);
  letter-spacing: 1px; margin-bottom: 10px;
  padding-left: 36px; /* ox stamp 공간 */
  display: flex; align-items: center; justify-content: space-between;
}
.retry-btn {
  font-size: 11px; color: var(--red); font-weight: 600;
  background: var(--red-bg); border: 1px solid var(--red-border);
  border-radius: 5px; padding: 2px 10px; cursor: pointer;
  font-family: inherit; transition: all .15s; display: none;
}
.retry-btn:hover { background: #fee2e2; }
.retry-btn.visible { display: block; }

.card-q {
  font-family: 'Noto Serif KR', serif;
  font-size: 16px; line-height: 2.1; color: var(--text);
}

/* 객관식 선지 */
.choices-list { margin-top: 14px; display: flex; flex-direction: column; gap: 7px; }
.choice-opt {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 9px; cursor: pointer;
  border: 1.5px solid var(--border-light);
  background: var(--bg);
  font-family: 'Noto Serif KR', serif;
  font-size: 14.5px; color: var(--text);
  transition: all .13s; user-select: none;
}
.choice-opt:hover { border-color: var(--accent-mid); background: var(--accent-light); }
.choice-opt.picked { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }
.choice-opt.revealed-correct { border-color: var(--green) !important; background: var(--green-bg) !important; color: var(--green) !important; }
.choice-opt.revealed-wrong   { border-color: var(--red) !important;   background: var(--red-bg) !important;   color: var(--red) !important;   opacity: .7; }
.choice-opt.disabled { pointer-events: none; }
.cn { font-size: 12.5px; font-weight: 700; color: var(--accent-mid); min-width: 16px; }
.choice-opt.revealed-correct .cn { color: var(--green); }
.choice-opt.revealed-wrong   .cn { color: var(--red); }

/* 정답 확인 버튼 (카드 내부) */
.card-check-row { margin-top: 14px; display: flex; align-items: center; gap: 10px; }
.card-confirm-btn {
  padding: 9px 20px; border-radius: 8px; border: 1.5px solid var(--accent);
  background: var(--accent); color: #fff;
  font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit;
  transition: all .15s;
}
.card-confirm-btn:hover { background: #4338ca; }
.card-confirm-btn:disabled { background: var(--border); border-color: var(--border); color: var(--text-dim); cursor: default; }

/* 단답형 */
.short-wrap { margin-top: 14px; display: flex; gap: 8px; }
.short-input {
  flex: 1; background: var(--bg); border: 1.5px solid var(--border);
  border-radius: 8px; padding: 10px 13px; font-size: 15px; color: var(--text);
  font-family: 'Noto Serif KR', serif; outline: none; transition: border .15s;
}
.short-input:focus { border-color: var(--accent); }
.short-input:disabled { opacity: .6; background: var(--border-light); }
.short-confirm-btn {
  padding: 10px 16px; border-radius: 8px; border: 1.5px solid var(--accent);
  background: var(--accent); color: #fff;
  font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit;
  transition: all .15s; white-space: nowrap;
}
.short-confirm-btn:hover { background: #4338ca; }
.short-confirm-btn:disabled { background: var(--border); border-color: var(--border); color: var(--text-dim); cursor: default; }

/* 서술형 */
.essay-wrap { margin-top: 14px; }
.essay-input {
  width: 100%; background: var(--bg); border: 1.5px solid var(--border);
  border-radius: 9px; padding: 12px 14px; font-size: 14.5px; color: var(--text);
  font-family: 'Noto Serif KR', serif; outline: none; resize: vertical;
  min-height: 90px; line-height: 1.9; transition: border .15s;
}
.essay-input:focus { border-color: var(--accent); }
.essay-input:disabled { opacity: .6; background: var(--border-light); }
.essay-confirm-btn {
  margin-top: 8px; padding: 9px 18px; border-radius: 8px;
  border: 1.5px solid var(--accent); background: var(--accent); color: #fff;
  font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; transition: all .15s;
}
.essay-confirm-btn:hover { background: #4338ca; }
.essay-confirm-btn:disabled { background: var(--border); border-color: var(--border); color: var(--text-dim); cursor: default; }

/* 피드백 */
.answer-feedback {
  margin-top: 10px; padding: 10px 14px; border-radius: 8px;
  font-size: 13.5px; font-family: 'Noto Serif KR', serif; line-height: 1.8;
  display: none;
}
.answer-feedback.show { display: block; }
.answer-feedback.fb-correct { background: var(--green-bg); border: 1px solid var(--green-border); color: var(--green); }
.answer-feedback.fb-wrong   { background: var(--red-bg);   border: 1px solid var(--red-border);   color: var(--red); }

/* 선택 닷 */
.sel-dot { position: absolute; top: 14px; right: 14px; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); display: none; }
.prob-card.selected .sel-dot { display: block; }

/* ── 오른쪽 패널 ── */
.right-panel {
  width: 370px; flex-shrink: 0;
  background: var(--sidebar-bg);
  border-left: 1px solid var(--border);
  overflow-y: auto; padding: 20px 18px;
  display: flex; flex-direction: column; gap: 14px;
}
.right-panel::-webkit-scrollbar { width: 4px; }
.right-panel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.right-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: var(--text-dim); text-align: center; gap: 8px;
}
.right-empty-icon { font-size: 30px; }
.right-empty-text { font-size: 12.5px; line-height: 1.9; color: var(--text-sub); }

.rp-label { font-size: 10px; color: var(--accent); letter-spacing: 2px; font-weight: 700; }

.hint-item { margin-bottom: 4px; }
.hint-toggle {
  width: 100%; background: var(--bg); border: 1px solid var(--border);
  border-radius: 7px; padding: 8px 12px; color: var(--text-sub); font-size: 12.5px;
  cursor: pointer; font-family: inherit; transition: all .13s;
  text-align: left; display: flex; justify-content: space-between; align-items: center;
}
.hint-toggle:hover { border-color: var(--accent-mid); color: var(--accent); }
.hint-toggle.open { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }
.hint-body {
  padding: 9px 12px; margin-top: 4px;
  background: var(--accent-light); border: 1px solid rgba(79,70,229,0.15);
  border-radius: 7px; font-size: 13px; color: #3730a3;
  line-height: 1.9; font-family: 'Noto Serif KR', serif; display: none;
}
.hint-body.open { display: block; }

.reveal-btn {
  width: 100%; padding: 9px 14px; border-radius: 8px; cursor: pointer;
  font-size: 13px; font-weight: 600; font-family: inherit; transition: all .15s; text-align: left;
}
.reveal-btn.ans-btn { border: 1.5px solid var(--green-border); background: var(--green-bg); color: var(--green); }
.reveal-btn.ans-btn:hover { background: #dcfce7; }
.reveal-btn.sol-btn { border: 1.5px solid var(--yellow-border); background: var(--yellow-bg); color: var(--yellow); }
.reveal-btn.sol-btn:hover { background: #fef3c7; }

.ans-box {
  padding: 10px 14px; border-radius: 8px; margin-top: 6px;
  background: var(--green-bg); border: 1px solid var(--green-border);
  font-size: 14px; color: var(--green); font-weight: 700; display: none;
  font-family: 'Noto Serif KR', serif;
}
.ans-box.open { display: block; }
.sol-box {
  padding: 12px 14px; border-radius: 8px; margin-top: 6px;
  background: var(--yellow-bg); border: 1px solid var(--yellow-border);
  font-size: 13px; color: #78350f; line-height: 2.1; display: none;
  font-family: 'Noto Serif KR', serif; white-space: pre-wrap;
}
.sol-box.open { display: block; }

details {
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
}
details summary {
  list-style: none; padding: 9px 13px; cursor: pointer;
  font-size: 12.5px; color: var(--text-sub); user-select: none; font-weight: 500;
}
details summary::-webkit-details-marker { display: none; }
.detail-body { padding: 0 13px 10px; font-size: 12.5px; color: var(--text-sub); line-height: 1.9; }

.done-note { text-align: center; font-size: 11.5px; color: var(--text-dim); padding: 2px 0 4px; }
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">∑</div>
    <div>
      <div class="logo-text">수학 문제 생성기</div>
      <div class="logo-sub">공통수학1 · 다항식 · 2022 개정 교육과정</div>
    </div>
  </div>
  <div class="header-badge">수학교육과 캡스톤디자인</div>
</header>

<div class="workspace">
  <aside>
    <div class="sb-label">⚙ 문제 설정</div>
    <div>
      <div class="field-label">소단원</div>
      <div class="subunit-list" id="subunitGroup">
        <button class="subunit-btn active" data-value="연산">다항식의 연산<div class="sub-desc">덧셈·뺄셈·곱셈·나눗셈</div></button>
        <button class="subunit-btn" data-value="나머지">항등식과 나머지 정리<div class="sub-desc">항등식·나머지정리·인수정리</div></button>
        <button class="subunit-btn" data-value="인수분해">인수분해<div class="sub-desc">인수분해 공식과 응용</div></button>
      </div>
    </div>
    <div>
      <div class="field-label">난이도</div>
      <div class="level-row" id="levelGroup">
        <button class="level-btn" data-lv="1" data-color="#16a34a" data-desc="공식 직접 대입 (1~2단계)" data-label="기초">기초</button>
        <button class="level-btn active" data-lv="2" data-color="#2563eb" data-desc="공식 단순 적용 (2~3단계)" data-label="기본">기본</button>
        <button class="level-btn" data-lv="3" data-color="#d97706" data-desc="개념 응용 (3~4단계)" data-label="표준">표준</button>
        <button class="level-btn" data-lv="4" data-color="#ea580c" data-desc="복합 조건 (4~5단계)" data-label="심화">심화</button>
        <button class="level-btn" data-lv="5" data-color="#dc2626" data-desc="역발상·다단계 (5단계↑)" data-label="최고">최고</button>
      </div>
      <div class="level-hint-text" id="levelHint">공식 단순 적용 (2~3단계)</div>
    </div>
    <div>
      <div class="field-label">문제 유형</div>
      <div class="type-row" id="typeGroup">
        <button class="type-btn active" data-value="객관식">객관식</button>
        <button class="type-btn" data-value="단답형">단답형</button>
        <button class="type-btn" data-value="서술형">서술형</button>
      </div>
    </div>
    <div>
      <div class="field-label">문항 수</div>
      <div class="count-ctrl">
        <button class="count-btn" id="countDown">−</button>
        <div class="count-num" id="countDisplay">3</div>
        <button class="count-btn" id="countUp">+</button>
      </div>
    </div>
    <button id="generateBtn">✦ 문제 생성하기</button>
  </aside>

  <div class="center-panel" id="centerPanel">
    <div class="empty-state">
      <div class="empty-icon">📝</div>
      <div class="empty-text">왼쪽에서 설정을 선택하고<br>문제 생성하기를 누르세요</div>
    </div>
  </div>

  <div class="right-panel" id="rightPanel">
    <div class="right-empty">
      <div class="right-empty-icon">👆</div>
      <div class="right-empty-text">문제를 클릭하면<br>힌트·정답·풀이가<br>여기에 나옵니다</div>
    </div>
  </div>
</div>

<script>
// ═══════════════════════════════════════════════════
// 문제 은행
// ═══════════════════════════════════════════════════
const BANK = {
  연산:{
    1:[
      {type:["객관식","단답형","서술형"],q:"$(2x^2 - 3x + 1) + (x^2 + 5x - 2)$를 계산하면?",choices:["$3x^2 + 2x - 1$","$3x^2 - 2x + 1$","$x^2 + 2x - 1$","$3x^2 + 2x + 1$","$3x^2 - 2x - 1$"],correct_idx:0,answer:"$3x^2 + 2x - 1$",short_answer:"3x²+2x-1",solution:"1단계: 동류항끼리 묶기\n$(2x^2+x^2)+(-3x+5x)+(1-2)$\n\n2단계: 계산\n$=3x^2+2x-1$",hints:["동류항(차수가 같은 항)끼리 더한다","$x^2$항, $x$항, 상수항을 각각 모은다","$(2+1)x^2+(-3+5)x+(1-2)$를 계산한다"],terms:"동류항: 문자와 차수가 같은 항",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$(5x - 3) - (2x + 4)$를 계산하면?",choices:["$3x - 7$","$3x + 7$","$7x - 7$","$3x - 1$","$7x + 7$"],correct_idx:0,answer:"$3x - 7$",short_answer:"3x-7",solution:"괄호 앞 빼기 부호 처리\n$5x-3-2x-4$\n동류항 정리: $3x-7$",hints:["뺄셈은 괄호 안 모든 부호를 바꿔 더한다","$5x-2x=3x$","$-3-4=-7$"],terms:"다항식의 뺄셈: 빼는 식의 각 항의 부호를 바꿔서 더한다",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$3x(2x - 4)$를 전개하면?",choices:["$6x^2 - 12x$","$6x^2 + 12x$","$5x^2 - 12x$","$6x^2 - 4x$","$3x^2 - 12x$"],correct_idx:0,answer:"$6x^2 - 12x$",short_answer:"6x²-12x",solution:"분배법칙 적용\n$3x\\times2x - 3x\\times4 = 6x^2-12x$",hints:["단항식×다항식은 분배법칙을 이용한다","$3x\\times2x$와 $3x\\times(-4)$를 각각 계산한다","$x\\times x=x^2$"],terms:"분배법칙: $a(b+c)=ab+ac$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"}
    ],
    2:[
      {type:["객관식","단답형","서술형"],q:"$(x+3)(x-5)$를 전개하면?",choices:["$x^2-2x-15$","$x^2+2x-15$","$x^2-2x+15$","$x^2-8x-15$","$x^2+8x+15$"],correct_idx:0,answer:"$x^2-2x-15$",short_answer:"x²-2x-15",solution:"$(x+a)(x+b)=x^2+(a+b)x+ab$에 $a=3,b=-5$\n$x^2-2x-15$",hints:["$(x+a)(x+b)=x^2+(a+b)x+ab$ 공식 이용","$a=3$, $b=-5$","$(a+b)=-2$, $ab=-15$"],terms:"곱셈공식: $(x+a)(x+b)=x^2+(a+b)x+ab$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$(2x+1)(3x-2)$를 전개하면?",choices:["$6x^2-x-2$","$6x^2+x-2$","$6x^2-x+2$","$5x^2-x-2$","$6x^2+x+2$"],correct_idx:0,answer:"$6x^2-x-2$",short_answer:"6x²-x-2",solution:"FOIL로 전개\n$6x^2-4x+3x-2=6x^2-x-2$",hints:["FOIL: 앞×앞, 앞×뒤, 뒤×앞, 뒤×뒤","$x$항: $-4x+3x=-x$","상수항: $-2$"],terms:"FOIL: 두 이항식의 곱을 순서대로 전개하는 방법",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$(x+2)^2-(x-2)^2$을 간단히 하면?",choices:["$8x$","$4x$","$2x$","$8x^2$","$4$"],correct_idx:0,answer:"$8x$",short_answer:"8x",solution:"$A^2-B^2=(A+B)(A-B)$ 활용\n$[(x+2)+(x-2)]\\cdot[(x+2)-(x-2)]=2x\\cdot4=8x$",hints:["$A^2-B^2=(A+B)(A-B)$ 공식 이용","$(A+B)=2x$","$(A-B)=4$"],terms:"합차공식: $A^2-B^2=(A+B)(A-B)$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"}
    ],
    3:[
      {type:["객관식","단답형","서술형"],q:"$x^2+3x-2$를 $x+1$로 나누었을 때 몫과 나머지는?",choices:["몫 $x+2$, 나머지 $-4$","몫 $x+2$, 나머지 $4$","몫 $x-2$, 나머지 $4$","몫 $x+4$, 나머지 $-2$","몫 $x+2$, 나머지 $0$"],correct_idx:0,answer:"몫 $x+2$, 나머지 $-4$",short_answer:"몫 x+2 나머지 -4",solution:"$x^2\\div x=x$ → 몫의 첫 항 $x$\n$(x+1)\\cdot x=x^2+x$, 빼면 $2x-2$\n$2x\\div x=2$ → 몫에 $+2$\n$(x+1)\\cdot2=2x+2$, 빼면 $-4$",hints:["최고차항부터 차례로 나눈다","$x^2\\div x=x$가 몫의 첫 항이다","나머지의 차수 < 나누는 식의 차수"],terms:"다항식 나눗셈: $f(x)=Q(x)g(x)+R$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$(x+y)^3$을 전개하면?",choices:["$x^3+3x^2y+3xy^2+y^3$","$x^3+y^3$","$x^3-3x^2y+3xy^2-y^3$","$x^3+2x^2y+2xy^2+y^3$","$x^3+3xy+y^3$"],correct_idx:0,answer:"$x^3+3x^2y+3xy^2+y^3$",short_answer:"x³+3x²y+3xy²+y³",solution:"$(a+b)^3=a^3+3a^2b+3ab^2+b^3$에 $a=x,b=y$ 대입",hints:["$(a+b)^3=a^3+3a^2b+3ab^2+b^3$ 공식 이용","이항정리 계수는 $1,3,3,1$","각 항의 차수 합은 항상 3"],terms:"세제곱 전개: $(a+b)^3=a^3+3a^2b+3ab^2+b^3$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"}
    ],
    4:[
      {type:["객관식","단답형","서술형"],q:"$x+\\dfrac{1}{x}=3$일 때, $x^2+\\dfrac{1}{x^2}$의 값은?",choices:["$7$","$9$","$11$","$5$","$6$"],correct_idx:0,answer:"$7$",short_answer:"7",solution:"양변 제곱\n$\\left(x+\\dfrac{1}{x}\\right)^2=9$\n$x^2+2+\\dfrac{1}{x^2}=9$\n$x^2+\\dfrac{1}{x^2}=7$",hints:["주어진 식을 제곱하면 구하는 식이 포함된다","$(a+b)^2=a^2+2ab+b^2$ 이용","$x\\cdot\\dfrac{1}{x}=1$"],terms:"대칭식 활용: 주어진 식을 제곱·세제곱하여 변형",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"},
      {type:["단답형","서술형"],q:"$a+b+c=5$, $ab+bc+ca=3$일 때 $a^2+b^2+c^2$의 값을 구하시오.",choices:[],correct_idx:-1,answer:"$19$",short_answer:"19",solution:"$(a+b+c)^2=a^2+b^2+c^2+2(ab+bc+ca)$\n$25=a^2+b^2+c^2+6$\n$a^2+b^2+c^2=19$",hints:["$(a+b+c)^2=a^2+b^2+c^2+2(ab+bc+ca)$ 이용","$(a+b+c)^2=25$","$a^2+b^2+c^2=25-6$"],terms:"$(a+b+c)^2=a^2+b^2+c^2+2ab+2bc+2ca$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"}
    ],
    5:[
      {type:["단답형","서술형"],q:"$x+y+z=4$, $xy+yz+zx=2$, $xyz=1$일 때 $x^3+y^3+z^3$의 값을 구하시오.",choices:[],correct_idx:-1,answer:"$43$",short_answer:"43",solution:"$(x+y+z)^2=16$, $x^2+y^2+z^2=12$\n$x^2+y^2+z^2-xy-yz-zx=10$\n$x^3+y^3+z^3=3+40=43$",hints:["$(x+y+z)^2$을 전개하여 $x^2+y^2+z^2$를 구한다","$x^2+y^2+z^2-xy-yz-zx=12-2=10$","$x^3+y^3+z^3=3xyz+(x+y+z)\\times10$"],terms:"$x^3+y^3+z^3-3xyz=(x+y+z)(x^2+y^2+z^2-xy-yz-zx)$",standard:"[10공수01-01] 다항식의 사칙연산을 할 수 있다"}
    ]
  },
  나머지:{
    1:[
      {type:["객관식","단답형","서술형"],q:"등식 $2x^2+ax+b=2x^2-3x+5$가 항등식일 때, $a+b$의 값은?",choices:["$2$","$-2$","$8$","$-8$","$3$"],correct_idx:0,answer:"$2$",short_answer:"2",solution:"항등식이므로 동류항의 계수가 같다.\n$a=-3$, $b=5$, $a+b=2$",hints:["항등식은 양변의 같은 차수의 계수가 모두 같다","$x$의 계수: $a=-3$","상수항: $b=5$"],terms:"항등식: 변수 값에 관계없이 항상 성립하는 등식",standard:"[10공수01-02] 항등식의 성질을 이해하고 미정계수를 구할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$f(x)=x^2-3x+2$일 때 $f(2)$의 값은?",choices:["$0$","$1$","$2$","$3$","$4$"],correct_idx:0,answer:"$0$",short_answer:"0",solution:"$f(2)=4-6+2=0$",hints:["$f(2)$는 $f(x)$에 $x=2$를 대입한 값이다","$2^2=4$, $3\\times2=6$","$4-6+2$를 계산한다"],terms:"함수값: $f(a)$는 $f(x)$의 $x$에 $a$를 대입한 값",standard:"[10공수01-03] 나머지 정리를 이해하고 활용할 수 있다"}
    ],
    2:[
      {type:["객관식","단답형","서술형"],q:"$f(x)=x^3-2x^2+3x-1$을 $(x-1)$로 나누었을 때의 나머지는?",choices:["$1$","$-1$","$2$","$0$","$3$"],correct_idx:0,answer:"$1$",short_answer:"1",solution:"나머지 정리: 나머지 $=f(1)$\n$f(1)=1-2+3-1=1$",hints:["나머지 정리: $(x-a)$로 나눈 나머지 $=f(a)$","$(x-1)$로 나누므로 $a=1$","$f(1)=1-2+3-1$을 계산한다"],terms:"나머지 정리: $f(x)$를 $(x-a)$로 나눈 나머지는 $f(a)$",standard:"[10공수01-03] 나머지 정리를 이해하고 활용할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$f(x)$를 $(x+2)$로 나누었을 때 나머지가 $5$이다. $f(-2)$의 값은?",choices:["$5$","$-5$","$2$","$-2$","$0$"],correct_idx:0,answer:"$5$",short_answer:"5",solution:"$(x+2)=(x-(-2))$이므로 나머지 $=f(-2)=5$",hints:["$(x+2)=(x-(-2))$이므로 $a=-2$","나머지 정리에 의해 나머지 $=f(-2)$","나머지 $=5$"],terms:"나머지 정리: $f(x)$를 $(x-a)$로 나눈 나머지는 $f(a)$",standard:"[10공수01-03] 나머지 정리를 이해하고 활용할 수 있다"}
    ],
    3:[
      {type:["객관식","단답형","서술형"],q:"$f(x)=x^3+ax+b$가 $(x-1)$로 나누어 떨어지고, $(x+2)$로 나누면 나머지가 $-6$이다. $a+b$의 값은?",choices:["$-1$","$1$","$0$","$-3$","$3$"],correct_idx:0,answer:"$-1$",short_answer:"-1",solution:"$f(1)=0$ → $1+a+b=0$ ···①\n$f(-2)=-6$ → $-8-2a+b=-6$ ···②\n풀면 $a=-1$, $b=0$, $a+b=-1$",hints:["나누어 떨어지면 $f(1)=0$ (인수정리)","$(x+2)$로 나눈 나머지: $f(-2)=-6$","연립방정식으로 $a$, $b$를 구한다"],terms:"인수정리: $f(a)=0\\Leftrightarrow f(x)$는 $(x-a)$를 인수로 갖는다",standard:"[10공수01-03] 나머지 정리를 이해하고 활용할 수 있다"}
    ],
    4:[
      {type:["단답형","서술형"],q:"$f(x)$를 $(x-1)(x+1)$로 나누었을 때 나머지가 $3x+1$이다. $f(x)$를 $(x-1)$로 나누었을 때의 나머지를 구하시오.",choices:[],correct_idx:-1,answer:"$4$",short_answer:"4",solution:"$f(x)=(x-1)(x+1)Q(x)+3x+1$\n$(x-1)$로 나눈 나머지 $=f(1)=0+3+1=4$",hints:["$f(x)=(x-1)(x+1)Q(x)+3x+1$로 표현한다","$(x-1)$로 나눈 나머지 $=f(1)$","$f(1)$에서 첫 항은 $0$"],terms:"나머지 정리: $f(x)$를 $(x-a)$로 나눈 나머지는 $f(a)$",standard:"[10공수01-03] 나머지 정리를 이해하고 활용할 수 있다"}
    ],
    5:[
      {type:["서술형"],q:"$f(x)$를 $(x-1)^2$으로 나누면 나머지가 $2x-1$이고, $(x+2)$로 나누면 나머지가 $8$이다. $f(x)$를 $(x-1)^2(x+2)$로 나누었을 때의 나머지를 $ax^2+bx+c$로 놓고 $a,b,c$를 구하시오.",choices:[],correct_idx:-1,answer:"$a=-\\dfrac{1}{3},\\ b=\\dfrac{5}{3},\\ c=-\\dfrac{4}{3}$",short_answer:"a=-1/3 b=5/3 c=-4/3",solution:"나머지를 $ax^2+bx+c$로 놓는다.\n$f(1)=a+b+c=1$ ···①\n$f'(1)=2a+b=2$ ···②\n$f(-2)=4a-2b+c=8$ ···③\n연립하면 $a=-1/3$, $b=5/3$, $c=-4/3$",hints:["나머지를 $ax^2+bx+c$ (2차식)로 놓는다","$(x-1)^2$ 조건: $f(1)$과 $f'(1)$ 두 가지","$f(-2)=8$ 조건을 추가하여 연립방정식을 푼다"],terms:"중근과 나머지 정리: $(x-a)^2$으로 나눌 때 $f(a)$와 $f'(a)$ 활용",standard:"[10공수01-03] 나머지 정리를 이해하고 활용할 수 있다"}
    ]
  },
  인수분해:{
    1:[
      {type:["객관식","단답형","서술형"],q:"$x^2-5x+6$을 인수분해하면?",choices:["$(x-2)(x-3)$","$(x+2)(x+3)$","$(x-2)(x+3)$","$(x+2)(x-3)$","$(x-1)(x-6)$"],correct_idx:0,answer:"$(x-2)(x-3)$",short_answer:"(x-2)(x-3)",solution:"곱이 $6$, 합이 $-5$인 두 수: $-2$와 $-3$\n$x^2-5x+6=(x-2)(x-3)$",hints:["$x^2+(a+b)x+ab=(x+a)(x+b)$ 이용","곱이 $6$, 합이 $-5$인 두 수를 찾는다","두 수는 $-2$와 $-3$"],terms:"인수분해: $x^2+(a+b)x+ab=(x+a)(x+b)$",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$x^2-9$를 인수분해하면?",choices:["$(x-3)(x+3)$","$(x-3)^2$","$(x+3)^2$","$(x-9)(x+1)$","$(x+9)(x-1)$"],correct_idx:0,answer:"$(x-3)(x+3)$",short_answer:"(x-3)(x+3)",solution:"$x^2-9=x^2-3^2=(x+3)(x-3)$",hints:["$a^2-b^2=(a+b)(a-b)$ 공식 이용","$9=3^2$","$a=x$, $b=3$"],terms:"합차 공식: $a^2-b^2=(a+b)(a-b)$",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"}
    ],
    2:[
      {type:["객관식","단답형","서술형"],q:"$2x^2+5x+3$을 인수분해하면?",choices:["$(2x+3)(x+1)$","$(2x+1)(x+3)$","$(x+3)(x+1)$","$(2x-3)(x-1)$","$(2x+3)(x-1)$"],correct_idx:0,answer:"$(2x+3)(x+1)$",short_answer:"(2x+3)(x+1)",solution:"$(2x+3)(x+1)=2x^2+5x+3$ ✓",hints:["$(ax+b)(cx+d)$ 형태를 시도한다","$ac=2$, $bd=3$인 경우를 고려한다","교차 검증: $ad+bc=2+3=5$ 확인"],terms:"이차식의 인수분해: $(ax+b)(cx+d)$ 형태로 분해",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$x^2+4x+4$를 인수분해하면?",choices:["$(x+2)^2$","$(x-2)^2$","$(x+4)(x+1)$","$(x+2)(x-2)$","$(x+1)^2$"],correct_idx:0,answer:"$(x+2)^2$",short_answer:"(x+2)²",solution:"$x^2+4x+4=(x+2)^2$",hints:["$a^2+2ab+b^2=(a+b)^2$ 완전제곱식 공식","$4=2^2$, $4x=2\\cdot x\\cdot2$ 확인","$a=x$, $b=2$"],terms:"완전제곱식: $a^2+2ab+b^2=(a+b)^2$",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"}
    ],
    3:[
      {type:["객관식","단답형","서술형"],q:"$x^3-8$을 인수분해하면?",choices:["$(x-2)(x^2+2x+4)$","$(x+2)(x^2-2x+4)$","$(x-2)^3$","$(x-2)(x^2-4)$","$(x-2)(x+2)^2$"],correct_idx:0,answer:"$(x-2)(x^2+2x+4)$",short_answer:"(x-2)(x²+2x+4)",solution:"$x^3-8=x^3-2^3=(x-2)(x^2+2x+4)$",hints:["$a^3-b^3=(a-b)(a^2+ab+b^2)$ 공식 이용","$8=2^3$","$a=x$, $b=2$ 대입"],terms:"세제곱 차이: $a^3-b^3=(a-b)(a^2+ab+b^2)$",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"},
      {type:["객관식","단답형","서술형"],q:"$x^4-5x^2+4$를 인수분해하면?",choices:["$(x-1)(x+1)(x-2)(x+2)$","$(x^2-1)(x^2-4)$","$(x-1)^2(x-2)^2$","$(x+1)^2(x+2)^2$","$(x^2+1)(x^2+4)$"],correct_idx:0,answer:"$(x-1)(x+1)(x-2)(x+2)$",short_answer:"(x-1)(x+1)(x-2)(x+2)",solution:"$t=x^2$로 치환\n$t^2-5t+4=(t-1)(t-4)=(x^2-1)(x^2-4)$\n$=(x-1)(x+1)(x-2)(x+2)$",hints:["$x^2=t$로 치환하면 이차식이 된다","$t^2-5t+4$를 인수분해한다","$x^2-1$과 $x^2-4$를 다시 인수분해한다"],terms:"치환을 이용한 인수분해",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"}
    ],
    4:[
      {type:["단답형","서술형"],q:"$a^2(b-c)+b^2(c-a)+c^2(a-b)$를 인수분해하시오.",choices:[],correct_idx:-1,answer:"$(a-b)(b-c)(c-a)$",short_answer:"(a-b)(b-c)(c-a)",solution:"$a$에 대해 내림차순 정리\n$=(b-c)a^2-(b+c)(b-c)a+bc(b-c)$\n$=(b-c)(a-b)(a-c)=(a-b)(b-c)(c-a)$",hints:["$a$에 대한 내림차순으로 정리한다","공통인수 $(b-c)$를 찾는다","$a^2-(b+c)a+bc=(a-b)(a-c)$"],terms:"순환식 인수분해: 변수를 순환시켜 대칭성 이용",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"}
    ],
    5:[
      {type:["서술형"],q:"$x^4+x^2+1$을 인수분해하시오.",choices:[],correct_idx:-1,answer:"$(x^2+x+1)(x^2-x+1)$",short_answer:"(x²+x+1)(x²-x+1)",solution:"$x^4+x^2+1=(x^2+1)^2-x^2$\n$=(x^2+x+1)(x^2-x+1)$",hints:["$x^2$을 더하고 빼서 완전제곱식을 만든다","$x^4+2x^2+1=(x^2+1)^2$","$(x^2+1)^2-x^2$은 합차 공식으로 인수분해된다"],terms:"항을 더하고 빼서 완전제곱식 생성 후 합차 공식 적용",standard:"[10공수01-04] 다항식의 인수분해를 할 수 있다"}
    ]
  }
};

// ═══════════════════════════════════════════════════
// 상태
// ═══════════════════════════════════════════════════
const st = { subunit:'연산', level:2, levelLabel:'기본', type:'객관식', count:3 };
let problems = [];      // { prob, shuffled_choices, shuffled_correct }
let probStates = [];    // { picked, submitted, isCorrect, userText }
let selectedIdx = -1;

// ═══════════════════════════════════════════════════
// 사이드바
// ═══════════════════════════════════════════════════
document.querySelectorAll('#subunitGroup .subunit-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#subunitGroup .subunit-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active'); st.subunit = btn.dataset.value;
  });
});
function applyLvStyle(btn, on) {
  const c = btn.dataset.color;
  btn.style.borderColor = on ? c : '';
  btn.style.background  = on ? c+'18' : '';
  btn.style.color       = on ? c : '';
  btn.style.fontWeight  = on ? '700' : '';
}
document.querySelectorAll('#levelGroup .level-btn').forEach(btn => {
  if (btn.classList.contains('active')) applyLvStyle(btn, true);
  btn.addEventListener('click', () => {
    document.querySelectorAll('#levelGroup .level-btn').forEach(b => { b.classList.remove('active'); applyLvStyle(b, false); });
    btn.classList.add('active'); applyLvStyle(btn, true);
    st.level = parseInt(btn.dataset.lv); st.levelLabel = btn.dataset.label;
    document.getElementById('levelHint').textContent = btn.dataset.desc;
  });
});
document.querySelectorAll('#typeGroup .type-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#typeGroup .type-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active'); st.type = btn.dataset.value;
  });
});
document.getElementById('countDown').addEventListener('click', () => {
  if (st.count > 1) { st.count--; document.getElementById('countDisplay').textContent = st.count; }
});
document.getElementById('countUp').addEventListener('click', () => {
  if (st.count < 5) { st.count++; document.getElementById('countDisplay').textContent = st.count; }
});

// ═══════════════════════════════════════════════════
// 유틸
// ═══════════════════════════════════════════════════
function renderMath(el) {
  if (typeof renderMathInElement === 'function')
    renderMathInElement(el, {
      delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],
      throwOnError:false
    });
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length-1; i > 0; i--) {
    const j = Math.floor(Math.random()*(i+1));
    [a[i],a[j]] = [a[j],a[i]];
  }
  return a;
}

// ═══════════════════════════════════════════════════
// 오른쪽 패널 토글
// ═══════════════════════════════════════════════════
window.toggleHint = function(id, btn) {
  const el = document.getElementById(id);
  el.classList.toggle('open'); btn.classList.toggle('open');
  const a = btn.querySelector('.arr'); if (a) a.textContent = btn.classList.contains('open') ? '▲' : '▼';
};
window.toggleReveal = function(id, btn) {
  const el = document.getElementById(id);
  el.classList.toggle('open'); btn.classList.toggle('open');
  if (id.endsWith('-ans')) btn.textContent = el.classList.contains('open') ? '✓ 정답 숨기기' : '정답 확인';
  else btn.textContent = el.classList.contains('open') ? '풀이 숨기기' : '풀이 보기';
};

// ═══════════════════════════════════════════════════
// 채점 처리
// ═══════════════════════════════════════════════════
function doSubmit(idx) {
  const ps = probStates[idx];
  if (ps.submitted) return;
  ps.submitted = true;

  const { prob, shuffled_choices, shuffled_correct } = problems[idx];
  const card = document.querySelectorAll('.prob-card')[idx];

  let isCorrect = false;

  if (st.type === '객관식') {
    const picked = ps.picked;
    if (picked === -1) return; // 아무것도 안 골랐으면 무시
    isCorrect = (picked === shuffled_correct);

    // 선지 색상 반영
    card.querySelectorAll('.choice-opt').forEach((opt, i) => {
      opt.classList.remove('picked');
      opt.classList.add('disabled');
      if (i === shuffled_correct) opt.classList.add('revealed-correct');
      else if (i === picked && !isCorrect) opt.classList.add('revealed-wrong');
    });

    // 확인 버튼 비활성화
    const confirmBtn = card.querySelector('.card-confirm-btn');
    if (confirmBtn) confirmBtn.disabled = true;

  } else {
    const userText = (card.querySelector('.short-input') || card.querySelector('.essay-input'))?.value.trim() || '';
    ps.userText = userText;
    const norm = s => s.replace(/[\s\-]/g,'').toLowerCase();
    isCorrect = norm(userText) === norm(prob.short_answer);

    const fb = card.querySelector('.answer-feedback');
    if (fb) {
      fb.classList.add('show');
      if (isCorrect) {
        fb.classList.add('fb-correct');
        fb.innerHTML = '✓ 정답입니다!';
      } else {
        fb.classList.add('fb-wrong');
        fb.innerHTML = `✗ 오답입니다. &nbsp;정답: <strong>${prob.answer}</strong>`;
        renderMath(fb);
      }
    }
    const inp = card.querySelector('.short-input, .essay-input');
    if (inp) inp.disabled = true;
    const btn = card.querySelector('.short-confirm-btn, .essay-confirm-btn');
    if (btn) btn.disabled = true;
  }

  ps.isCorrect = isCorrect;

  // O/X 스탬프
  const stamp = card.querySelector('.ox-stamp');
  if (stamp) {
    stamp.textContent = isCorrect ? '○' : '✕';
    stamp.classList.add(isCorrect ? 'show-o' : 'show-x');
  }

  // 카드 테두리
  card.classList.add(isCorrect ? 'state-correct' : 'state-wrong');

  // 틀렸으면 다시 풀기 버튼 표시
  if (!isCorrect) {
    const retryBtn = card.querySelector('.retry-btn');
    if (retryBtn) retryBtn.classList.add('visible');
  }

  // 오른쪽 패널 갱신
  if (selectedIdx === idx) renderRightPanel(idx);
}

// ═══════════════════════════════════════════════════
// 다시 풀기
// ═══════════════════════════════════════════════════
function retryProblem(idx) {
  probStates[idx] = { picked:-1, submitted:false, isCorrect:null, userText:'' };
  const cp = document.getElementById('centerPanel');
  const cards = cp.querySelectorAll('.prob-card');
  const oldCard = cards[idx];
  const newCard = createCard(idx);
  cp.replaceChild(newCard, oldCard);
  renderMath(newCard);
  if (selectedIdx === idx) {
    newCard.classList.add('selected');
    renderRightPanel(idx);
  }
}

// ═══════════════════════════════════════════════════
// 카드 생성
// ═══════════════════════════════════════════════════
function createCard(idx) {
  const { prob, shuffled_choices, shuffled_correct } = problems[idx];
  const ps = probStates[idx];

  const card = document.createElement('div');
  card.className = 'prob-card';

  let inner = `
    <div class="sel-dot"></div>
    <div class="ox-stamp"></div>
    <div class="card-num">
      <span>문제 ${idx+1}</span>
      <button class="retry-btn" onclick="event.stopPropagation();retryProblem(${idx})">↺ 다시 풀기</button>
    </div>
    <div class="card-q">${prob.q}</div>`;

  if (st.type === '객관식' && shuffled_choices.length) {
    inner += `<div class="choices-list">`;
    '①②③④⑤'.split('').forEach((num, i) => {
      if (!shuffled_choices[i]) return;
      inner += `<div class="choice-opt" data-i="${i}">
        <span class="cn">${num}</span><span>${shuffled_choices[i]}</span>
      </div>`;
    });
    inner += `</div>
    <div class="card-check-row">
      <button class="card-confirm-btn" disabled>정답 확인</button>
    </div>`;

  } else if (st.type === '단답형') {
    inner += `<div class="short-wrap">
      <input class="short-input" type="text" placeholder="답을 입력하세요"/>
      <button class="short-confirm-btn">확인</button>
    </div>
    <div class="answer-feedback"></div>`;

  } else {
    inner += `<div class="essay-wrap">
      <textarea class="essay-input" placeholder="풀이 과정과 답을 입력하세요..."></textarea>
      <button class="essay-confirm-btn">채점하기</button>
    </div>
    <div class="answer-feedback"></div>`;
  }

  card.innerHTML = inner;

  // 카드 클릭 → 오른쪽 패널 선택
  card.addEventListener('click', (e) => {
    if (e.target.closest('.choice-opt,.short-input,.short-confirm-btn,.essay-input,.essay-confirm-btn,.card-confirm-btn,.retry-btn')) return;
    selectCard(idx);
  });

  // 객관식 선지 클릭
  card.querySelectorAll('.choice-opt').forEach(opt => {
    opt.addEventListener('click', (e) => {
      e.stopPropagation();
      selectCard(idx);
      if (probStates[idx].submitted) return;
      card.querySelectorAll('.choice-opt').forEach(o => o.classList.remove('picked'));
      opt.classList.add('picked');
      probStates[idx].picked = parseInt(opt.dataset.i);
      // 정답 확인 버튼 활성화
      const confirmBtn = card.querySelector('.card-confirm-btn');
      if (confirmBtn) confirmBtn.disabled = false;
    });
  });

  // 정답 확인 버튼 (객관식)
  const confirmBtn = card.querySelector('.card-confirm-btn');
  if (confirmBtn) {
    confirmBtn.addEventListener('click', (e) => { e.stopPropagation(); doSubmit(idx); });
  }

  // 단답형 확인
  const shortConfirm = card.querySelector('.short-confirm-btn');
  if (shortConfirm) {
    shortConfirm.addEventListener('click', (e) => { e.stopPropagation(); doSubmit(idx); });
    card.querySelector('.short-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') doSubmit(idx);
    });
  }

  // 서술형 채점
  const essayConfirm = card.querySelector('.essay-confirm-btn');
  if (essayConfirm) {
    essayConfirm.addEventListener('click', (e) => { e.stopPropagation(); doSubmit(idx); });
  }

  return card;
}

// ═══════════════════════════════════════════════════
// 오른쪽 패널
// ═══════════════════════════════════════════════════
function renderRightPanel(idx) {
  const rp = document.getElementById('rightPanel');
  const { prob } = problems[idx];
  const uid = 'rp'+idx;
  const sol = st.type === '서술형'
    ? prob.solution + '\n\n📋 채점 기준\n- 풀이 과정 논리적 전개: 60점\n- 정답 도출: 40점'
    : prob.solution;

  rp.innerHTML = `
    <div class="rp-label">💡 문제 ${idx+1} 풀이</div>
    <div>
      <div class="field-label" style="margin-bottom:6px">힌트</div>
      ${prob.hints.map((h,i)=>`
        <div class="hint-item">
          <button class="hint-toggle" onclick="toggleHint('${uid}-h${i}',this)">
            힌트 ${i+1} <span class="arr">▼</span>
          </button>
          <div class="hint-body" id="${uid}-h${i}">${h}</div>
        </div>`).join('')}
    </div>
    <div>
      <button class="reveal-btn ans-btn" onclick="toggleReveal('${uid}-ans',this)">정답 확인</button>
      <div class="ans-box" id="${uid}-ans">정답: ${prob.answer}</div>
    </div>
    <div>
      <button class="reveal-btn sol-btn" onclick="toggleReveal('${uid}-sol',this)">풀이 보기</button>
      <div class="sol-box" id="${uid}-sol">${sol}</div>
    </div>
    <details><summary>📚 핵심 용어</summary><div class="detail-body">${prob.terms}</div></details>
    <details><summary>🎯 성취기준</summary><div class="detail-body">${prob.standard}</div></details>`;

  renderMath(rp);
}

// ═══════════════════════════════════════════════════
// 카드 선택
// ═══════════════════════════════════════════════════
function selectCard(idx) {
  selectedIdx = idx;
  document.querySelectorAll('.prob-card').forEach((c,i) => c.classList.toggle('selected', i===idx));
  renderRightPanel(idx);
}

// ═══════════════════════════════════════════════════
// 문제 뽑기 + 선지 셔플
// ═══════════════════════════════════════════════════
function pickProblems(sub, lv, type, n) {
  const pool = (BANK[sub]?.[lv] || []).filter(p => p.type.includes(type));
  if (!pool.length) return [];
  const shuffledPool = [...pool].sort(() => Math.random()-.5);
  const result = [];
  for (let i = 0; i < n; i++) {
    const prob = shuffledPool[i % shuffledPool.length];
    let shuffled_choices = [];
    let shuffled_correct = -1;
    if (type === '객관식' && prob.choices && prob.choices.length) {
      // 인덱스 배열을 섞어서 정답 위치 추적
      const indices = prob.choices.map((_,i) => i);
      const shuffledIdx = shuffle(indices);
      shuffled_choices = shuffledIdx.map(i => prob.choices[i]);
      shuffled_correct = shuffledIdx.indexOf(prob.correct_idx);
    }
    result.push({ prob, shuffled_choices, shuffled_correct });
  }
  return result;
}

// ═══════════════════════════════════════════════════
// 생성 버튼
// ═══════════════════════════════════════════════════
document.getElementById('generateBtn').addEventListener('click', () => {
  const cp = document.getElementById('centerPanel');
  const rp = document.getElementById('rightPanel');

  // 상태 완전 초기화
  problems = pickProblems(st.subunit, st.level, st.type, st.count);
  probStates = problems.map(() => ({ picked:-1, submitted:false, isCorrect:null, userText:'' }));
  selectedIdx = -1;

  cp.innerHTML = '';
  rp.innerHTML = `<div class="right-empty">
    <div class="right-empty-icon">👆</div>
    <div class="right-empty-text">문제를 클릭하면<br>힌트·정답·풀이가<br>여기에 나옵니다</div>
  </div>`;

  if (!problems.length) {
    cp.innerHTML = `<div class="empty-state">
      <div class="empty-icon">😅</div>
      <div class="empty-text">해당 조건의 문제가 준비 중입니다.<br>다른 유형이나 소단원을 선택해 주세요.</div>
    </div>`;
    return;
  }

  const subNames = {연산:'다항식의 연산',나머지:'항등식과 나머지 정리',인수분해:'인수분해'};
  const note = document.createElement('div');
  note.className = 'done-note';
  note.textContent = `Lv.${st.level} ${st.levelLabel} · ${subNames[st.subunit]} · ${problems.length}문제`;
  cp.appendChild(note);

  problems.forEach((_, idx) => {
    const card = createCard(idx);
    cp.appendChild(card);
    renderMath(card);
  });

  selectCard(0);
});
</script>
</body>
</html>
