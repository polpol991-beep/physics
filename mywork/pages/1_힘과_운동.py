import streamlit as st
import streamlit.components.v1 as components
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder) 
st.set_page_config(page_title="1. 힘과 운동", page_icon="🚀", layout="wide")

# =====================================================================
# 🚨 로그인 수문장 (로그인 안 하면 얄짤없이 쫓아냅니다!)
# =====================================================================
if not st.session_state.get('logged_in', False):
    st.error("⚠️ 로그인이 필요한 페이지입니다.")
    st.info("👈 왼쪽 사이드바에서 'app' (또는 메인 페이지)으로 이동하여 먼저 로그인해 주세요!")
    st.stop()

# =====================================================================
# 🛠️ 구글 시트 연동 세팅
# =====================================================================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
# 🌟 똑똑한 열쇠 탐색기 (클라우드와 내 컴퓨터 모두 호환)
if "google_creds" in st.secrets:
    # 1. 인터넷(스트림릿)에서 실행될 때: 비밀 금고에서 열쇠를 꺼냅니다.
    creds_dict = json.loads(st.secrets["google_creds"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # 2. 내 컴퓨터(VS Code)에서 실행될 때: 기존처럼 파일을 찾습니다.
    key_path = os.path.join(parent_folder, "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("2026 물리학")
result_sheet = spreadsheet.worksheet("1단원_결과")
user_sheet = spreadsheet.worksheet("회원정보") # 🌟 회원정보 시트 추가 연결!

s_id = str(st.session_state.student_id)
s_name = st.session_state.student_name

st.success(f"현재 로그인된 학생: **{s_id} {s_name}**")

# =====================================================================
# 🌟 [신규 기능] 시험 개방 여부 확인 (API 과부하 방지를 위해 10초 캐싱)
# =====================================================================
@st.cache_data(ttl=10)
def check_exam_open(_sheet):
    try:
        val = _sheet.acell('D1').value
        return str(val).strip() if val else "0"
    except Exception:
        return "0"

exam_open_flag = check_exam_open(user_sheet)

# =====================================================================
# 📑 탭(Tabs) 생성
# =====================================================================
tab_learn, tab_quiz = st.tabs(["📚 개념 학습", "📝 형성평가 (퀴즈)"])

# ---------------------------------------------------------
# [탭 1] 개념 학습 화면 
# ---------------------------------------------------------
with tab_learn:
    if st.session_state.get('exam_started', False):
        st.error("🚨 [경고] 현재 형성평가가 진행 중입니다!")
        st.warning("부정행위 방지를 위해 시험 중에는 개념 학습을 펼쳐볼 수 없습니다.")
    else:
        st.header("📖 핵심 개념 요약")
        
        with st.expander("1. 힘의 평형과 돌림힘", expanded=True):
            st.markdown("### 가. 힘의 평형")
            st.markdown("* **알짜힘:** 물체에 작용하는 모든 힘을 합친 것을 의미합니다.")
            st.image(os.path.join(parent_folder, "img", "image_e81eaa.png"), caption="힘의 평형과 돌림힘의 평형을 모두 만족하는 선반", use_container_width=True)
            st.markdown("* **힘의 평형:** 물체에 작용하는 알짜힘이 0인 상태를 말합니다. 평형 상태이면 물체는 정지해 있거나 등속 직선 운동을 합니다.")
            st.image(os.path.join(parent_folder, "img", "image02.png"), use_container_width=True)
            st.markdown("* **선반의 평형** ")
            st.markdown("* 힘의 평형: 아랫방향 힘 : $F_{물체}$, $F_{선반}$, 윗방향 힘 : $F_A$, $F_B$")
            st.markdown("* 돌림힘의 평형: 선반의 무게 중심을 회전축으로 잡았을 때 각 돌림힘(힘의 거리×힘의 크기) 가 같음")

            st.divider()
            st.markdown("### 나. 돌림힘 (Torque)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(os.path.join(parent_folder, "img", "image_e81bfe.png"), caption="돌림힘의 크기", use_container_width=True)
            with col2:
                st.image(os.path.join(parent_folder, "img", "image_e81c02.png"), caption="팔 길이에 따른 힘의 크기 변화", use_container_width=True)
                
            st.markdown("* **돌림힘:** 물체의 회전 상태를 변화시키는 원인이 되는 물리량입니다.")
            st.markdown("* **돌림힘의 크기:** 돌림힘($\\tau$)은 팔의 길이($r$)와 작용하는 힘($F$)의 곱으로 나타냅니다.")
            st.markdown("  ▶ **공식: $\\tau = r \\times F$**")
            st.markdown("* **팔 길이:** 회전축에서 힘의 연장선에 내린 수선의 발까지의 거리입니다.")
            st.markdown("* **문손잡이의 원리:** 문손잡이가 회전축(경첩)에서 멀리 있는 이유는, 거리가 멀어야 작은 힘으로도 큰 돌림힘을 만들어 문을 쉽게 열 수 있기 때문입니다.")

            st.divider()
            st.markdown("### 다. 돌림힘의 평형")
            st.image(os.path.join(parent_folder, "img", "image_e81ea5.png"), caption="돌림힘의 평형을 이룬 시소", use_container_width=True)
            st.markdown("* **시소의 원리:** 가벼운 사람은 받침점(회전축)에서 멀리, 무거운 사람은 가까이 앉아야 양쪽의 돌림힘 크기가 같아져 수평을 이룹니다.")
            st.markdown("* **구조물의 평형 조건:** 구조물이 쓰러지지 않으려면 알짜힘이 0이어야 하고, 알짜 돌림힘도 0이어야 합니다.")

            st.divider()
            st.markdown("### 라. 무게 중심과 구조물의 안정성")
            
            col3, col4 = st.columns(2)
            with col3:
                st.image(os.path.join(parent_folder, "img", "image_e81ec2.png"), caption="막대의 무게 중심", use_container_width=True)
            with col4:
                st.image(os.path.join(parent_folder, "img", "image_e81ec5.png"), caption="기울기에 따른 구조물의 안정성", use_container_width=True)
                
            st.markdown("* **무게 중심:** 물체를 이루는 모든 입자의 전체 무게가 한 점에 있는 것으로 볼 수 있는 가상의 점입니다.")
            st.markdown("* **안정성 조건:** 구조물이 안정해지려면 물체의 무게중심이 낮을수록, 그리고 물체의 바닥 면적(지지면)이 넓을수록 좋습니다. 넘어뜨리기 위해 기울여야 하는 각도가 클수록 안정적입니다.")

        with st.expander("2. 물체의 운동", expanded=True):
            st.markdown("### 가. 이동 거리와 변위")
            st.image(os.path.join(parent_folder, "img", "image03.png"), caption="경로에 따른 이동 거리와 변위의 차이", use_container_width=True)
            st.markdown("* **이동 거리:** 물체가 실제로 움직인 총거리입니다.")
            st.markdown("* **변위:** 처음 위치와 나중 위치의 변화로, 방향이 있습니다.")
            
            st.divider()
            st.markdown("### 나. 평균 속도와 순간 속도")
            st.image(os.path.join(parent_folder, "img", "image04.png"), caption="위치-시간 그래프에서의 평균 속도와 순간 속도", use_container_width=True)
            st.markdown("* **평균 속도:** 어느 시간 동안의 속도로, 점과 점을 잇는 직선의 기울기를 의미합니다.")
            st.markdown("* **순간 속도:** 어느 순간의 속도로, 그 점에서 그은 접선의 기울기를 의미합니다.")
            
            st.divider()
            st.markdown("### 다. 물체의 운동 그래프 분석")
            col1, col2 = st.columns(2)
            with col1:
                st.image(os.path.join(parent_folder, "img", "image05.png"), caption="등속도 운동 그래프", use_container_width=True)
                st.markdown("* **등속도 운동:** 속도가 일정한 운동입니다.")
            with col2:
                st.image(os.path.join(parent_folder, "img", "image06.png"), caption="등가속도 운동 그래프", use_container_width=True)
                st.markdown("* **등가속도 운동:** 가속도가 일정한 운동입니다.")
                
            st.markdown("* **💡 그래프 해석 꿀팁:** 그래프 아래의 '넓이(가로축×세로축)'와 '기울기(세로축/가로축)'가 어떤 물리량을 의미하는지 파악하는 가장 중요합니다.")
            
            st.image(os.path.join(parent_folder, "img", "image07.png"), caption="등가속도 직선 운동의 평균 속도 구하기", use_container_width=True)
            st.markdown("* **등가속도 운동의 평균 속도:** 등가속도 직선 운동을 하는 물체의 평균 속도는 처음 속도와 나중 속도의 중간값($\\frac{v_0+v}{2}$)과 같습니다.")

            st.divider()
            st.markdown("### 라. 등가속도 운동 공식 3가지 ⭐️")
            st.info("💡 물리학에서 가장 많이 쓰이는 핵심 공식입니다. ($v_0$: 처음 속도, $v$: 나중 속도, $a$: 가속도, $t$: 시간, $s$: 변위)")
            st.markdown("1. **속도와 시간의 관계:** $v = v_0 + at$")
            st.markdown("2. **변위와 시간의 관계:** $s = v_0 t + \\frac{1}{2}at^2$")
            st.markdown("3. **속도와 변위의 관계 (시간 $t$가 없을 때):** $2as = v^2 - v_0^2$")

        with st.expander("뉴턴의 운동 법칙", expanded=True):
            st.markdown("### 마. 뉴턴의 운동 법칙")
            st.markdown("#### (1) 제1법칙: 관성 법칙")
            st.markdown("* **관성:** 물체가 원래의 운동 상태를 그대로 유지하려는 성질입니다. 질량이 클수록 관성이 큽니다.")
            
            st.markdown("#### (2) 제2법칙: 가속도 법칙")
            st.markdown("* **공식:** $F = ma$ (알짜힘 = 질량 $\\times$ 가속도).")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.image(os.path.join(parent_folder, "img", "image08.png"), caption="수평면 위 실로 연결된 물체", use_container_width=True)
            with col_f2:
                st.image(os.path.join(parent_folder, "img", "image09.png"), caption="도르래로 연결된 물체", use_container_width=True)
            st.info("💡 **$F=ma$ 문제 풀이법:** 1. 모든 힘 표시 2. 전체 알짜힘 구하기 3. 전체 질량과 알짜힘으로 가속도 구하기 4. 개별 물체의 알짜힘 구하기.")

            st.markdown("#### (3) 제3법칙: 작용 반작용 법칙")
            st.markdown("* 한 물체가 다른 물체에 힘을 가하면, 크기가 같고 방향이 반대인 힘을 동시에 가합니다.")
            st.image(os.path.join(parent_folder, "img", "image10.png"), caption="작용 반작용의 다양한 예시", use_container_width=True)

        with st.expander("3. 운동량과 충격량"):
            st.markdown("### 가. 운동량과 운동량 보존 법칙")
            st.image(os.path.join(parent_folder, "img", "image11.png"), caption="두 물체의 충돌 전후", use_container_width=True)
            st.markdown("* **운동량:** 운동하는 물체가 가진 운동하는 정도를 나타내는 물리량입니다 ($p = m \\times v$).")
            st.markdown("* **운동량 보존 법칙:** 두 물체가 충돌할 때 운동량의 총합은 충돌 전과 충돌 후 똑같습니다.")
            
            st.divider()
            st.markdown("### 나. 충격량과 힘-시간 그래프")
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                st.image(os.path.join(parent_folder, "img", "image12.png"), caption="힘-시간 그래프와 충격량", use_container_width=True)
            with col_i2:
                st.image(os.path.join(parent_folder, "img", "image13.png"), caption="그래프 넓이와 평균 힘", use_container_width=True)
            st.markdown("* **충격량:** 물체가 받은 충격의 정도로, 힘과 작용 시간의 곱입니다 ($I = F \\times \\Delta t$).")
            st.markdown("* **충격량과 운동량의 관계:** 충격량은 운동량의 변화량과 같습니다 ($I = \\Delta p$).")
            st.markdown("* 그래프 아랫부분의 넓이는 충격량을 나타냅니다.")
            
            st.divider()
            st.markdown("### 다. 일상생활 속 충격량의 활용")
            st.markdown("#### (1) 충격량을 늘리는 경우 (스포츠)")
            st.image(os.path.join(parent_folder, "img", "image14.png"), caption="힘을 받는 시간을 길게 하여 충격량을 늘리는 예", use_container_width=True)
            st.markdown("* 대포의 포신을 길게 하거나 야구 방망이를 끝까지 휘두르면, 힘이 작용하는 시간이 길어져 충격량이 커지므로 물체가 멀리 날아갑니다.")
            
            st.markdown("#### (2) 충격력을 줄이는 경우 (안전 장치)")
            st.image(os.path.join(parent_folder, "img", "image15.png"), caption="충돌 시간에 따른 충격력 비교", use_container_width=True)
            st.image(os.path.join(parent_folder, "img", "image16.png"), caption="충돌 시간을 늘려 충격력을 줄이는 안전 장치들", use_container_width=True)
            st.markdown("* **안전 장치의 원리:** 에어백, 자동차 범퍼, 매트 등은 푹신하게 들어가면서 **충돌하는 시간을 길게 하여 물체가 받는 평균 힘(충격력)을 줄여줍니다**.") 

# ---------------------------------------------------------
# [탭 2] 형성평가 화면
# ---------------------------------------------------------
with tab_quiz:
    st.header("✅ 1단원 형성평가")
    
    # 🌟 [신규] 선생님이 회원정보 D1 셀에 1을 입력하지 않았다면 차단!
    if exam_open_flag != '1':
        st.error("🔒 **현재 시험이 비활성화되어 있습니다.**")
        st.info("선생님께서 구글 시트의 [회원정보] 탭 **D1 셀**에 숫자 **1**을 입력하셔야 시험이 시작됩니다.")
    else:
        # 시험이 열려있을 때만 아래 로직 실행
        if 'db_checked' not in st.session_state:
            st.session_state.db_checked = True
            st.session_state.db_status = None
            st.session_state.row_index = None
            st.session_state.cheating_penalty = 0
            st.session_state.exam_started = False
            st.session_state.quiz_results = None
            
            all_rows = result_sheet.get_all_values()
            for i, row in enumerate(all_rows):
                if len(row) > 0 and row[0] == s_id:
                    st.session_state.row_index = i + 1 
                    st.session_state.db_status = row[2] 
                    st.session_state.cheating_penalty = int(row[3]) if len(row) > 3 and row[3].isdigit() else 0
                    
                    if st.session_state.db_status == "진행중":
                        st.session_state.cheating_penalty += 10
                        result_sheet.update_cell(st.session_state.row_index, 4, st.session_state.cheating_penalty) 
                        st.session_state.exam_started = True
                        st.toast("🚨 비정상적인 새로고침이 감지되어 10점 감점되었습니다!")
                    
                    elif st.session_state.db_status == "완료":
                        st.session_state.exam_started = True
                        st.session_state.quiz_results = {
                            "correct_count": int(row[4]),
                            "base_score": int(row[5])
                        }
                    break

        if 'quiz_questions' not in st.session_state:
            all_questions = [
                {"level": "중", "q": "길이가 $L$인 질량이 균일한 막대가 줄 A, B에 매달려 정지해 있다. 줄 A는 왼쪽 끝에, 줄 B는 오른쪽 끝에서 $\\frac{1}{3}L$ 떨어진 곳에 있다. A, B가 막대를 당기는 힘의 크기 비 $\\frac{F_A}{F_B}$는?", "img": "img/스크린샷 2026-08-31 154719.png", "options": ["1/3", "1/2", "1", "2", "3"], "answer": "1/2"},
                {"level": "상", "q": "바닥면 한 변의 길이가 10 cm이고 높이가 12 cm인 균일한 직육면체 구조물의 한끝을 민다. 구조물이 넘어지지 않기 위한 $\\tan \\theta$의 최댓값은?", "img": "img/스크린샷 2026-08-31 154725.png", "options": ["1/6", "2/5", "1/2", "2/3", "5/6"], "answer": "5/6"},
                {"level": "하", "q": "직선상에서 운동하는 네 물체 A~D의 속도-시간 그래프에서 A와 C는 기울기가 양수인 직선, B와 D는 기울기가 0인 직선이다 (B의 속도>0, D의 속도=0). 이에 대한 설명으로 옳은 것은?", "img": "img/스크린샷 2026-08-31 154734.png", "options": ["A와 C의 속도는 항상 같다.", "A와 C는 속도가 일정한 운동을 한다.", "B와 D는 정지해 있다.", "B와 D의 가속도는 0이다.", "3초 동안 변위의 크기는 B가 가장 크다."], "answer": "B와 D의 가속도는 0이다."},
                {"level": "중", "q": "마찰이 없는 수평면에 질량이 각각 $m, 2m, m$인 물체 A, B, C가 있다. 이들에게 각각 $F, F, 3F$의 알짜힘이 작용할 때, 세 물체의 가속도 비 $a_A : a_B : a_C$ 는?", "img": "img/스크린샷 2026-08-31 154745.png", "options": ["1 : 1 : 3", "2 : 1 : 6", "1 : 2 : 3", "2 : 2 : 6", "3 : 1 : 2"], "answer": "2 : 1 : 6"},
                {"level": "상", "q": "속도 $v$로 달리던 자동차가 브레이크를 밟아 정지할 때까지의 이동 거리를 $s$라 하자. 알짜힘이 일정할 때, 속도가 $3v$가 되면 제동거리 $s$는 몇 배가 되는가?", "img": "img/스크린샷 2026-08-31 154803.png", "options": ["3배", "6배", "9배", "12배", "15배"], "answer": "9배"},
                {"level": "중", "q": "물체 A, B를 손바닥으로 받쳐 정지해 있다. A가 B를 누르는 힘 $F_{AB}$, B가 손을 누르는 힘 $F_{B손}$, 손이 B를 떠받치는 힘 $F_{손B}$의 크기를 옳게 비교한 것은?", "img": "img/스크린샷 2026-08-31 154822.png", "options": ["$F_{AB} > F_{B손} > F_{손B}$", "$F_{AB} > F_{B손} = F_{손B}$", "$F_{AB} = F_{B손} < F_{손B}$", "$F_{AB} < F_{B손} < F_{손B}$", "$F_{AB} < F_{B손} = F_{손B}$"], "answer": "$F_{AB} < F_{B손} = F_{손B}$"},
                {"level": "상", "q": "질량 $m$인 선수 A가 $2v$의 속도로 운동하다가, $v$의 속도로 운동하는 질량 $0.8m$인 선수 B를 밀었다. 밀고 난 직후 A의 속도가 $0.5v$가 되었다면, B의 속도는?", "img": "img/스크린샷 2026-08-31 154849.png", "options": ["0", "2/3 v", "23/8 v", "13/4 v", "15/4 v"], "answer": "23/8 v"},
                {"level": "중", "q": "고무줄로 연결된 수레 A(질량 2m)와 B(질량 m)를 잡고 있다가 동시에 놓았다. 두 수레가 충돌하여 한 덩어리가 되었다. 충돌 직전 A의 속도가 0.2 m/s라면 충돌 직후 한 덩어리가 된 A, B의 속도는?", "img": "img/스크린샷 2026-08-31 154831.png", "options": ["0 m/s", "0.05 m/s", "0.07 m/s", "0.12 m/s", "0.15 m/s"], "answer": "0 m/s"},
                {"level": "하", "q": "크기가 같은 두 힘 $F_1, F_2$를 정지해있는 막대의 두 지점에 그림과 같이 작용할 때 옳은 것은? (막대의 알짜힘은 0, 돌림힘은 0이 아님)", "img": "img/스크린샷 2026-08-31 154701.png", "options": ["막대에 작용하는 알짜힘은 0이 아니다.", "막대는 직선 운동을 한다.", "막대는 회전 운동을 한다.", "돌림힘의 평형을 이룬다.", "아무런 운동도 하지 않는다."], "answer": "막대는 회전 운동을 한다."},
                {"level": "하", "q": "직선상에서 운동하는 물체의 속도-시간 그래프에서 0~10초 구간은 속도가 증가하고, 10~20, $t$~30초는 등속, 20~$t$, 30~40초는 속도가 감소한다. 가속도의 크기가 가장 큰 구간은?", "img": "img/스크린샷 2026-08-31 154751.png", "options": ["0~10초", "10~20초", "20~30초", "30~40초", "모두 같다"], "answer": "30~40초"},
                {"level": "하", "q": "길이가 $3L$인 균일한 막대에 수직 방향으로 여러 힘이 작용할 때 막대가 회전하지 않는 조건은?", "img": None, "options": ["알짜힘만 0이면 된다.", "알짜 돌림힘만 0이면 된다.", "알짜힘과 알짜 돌림힘이 모두 0이어야 한다.", "무게중심에 힘이 작용해야 작용해야 한다.", "힘의 크기가 모두 같아야 한다."], "answer": "알짜힘과 알짜 돌림힘이 모두 0이어야 한다."}
            ]
            
            random.seed(s_id)
            
            easy_qs = [q for q in all_questions if q["level"] == "하"]
            med_qs = [q for q in all_questions if q["level"] == "중"]
            hard_qs = [q for q in all_questions if q["level"] == "상"]
            
            selected_qs = random.sample(easy_qs, 2) + random.sample(med_qs, 2) + random.sample(hard_qs, 1)
            random.shuffle(selected_qs)
            
            st.session_state.quiz_questions = selected_qs
            random.seed() 

        is_completed = (st.session_state.db_status == "완료")
        
        # 🌟 [수정 완료] 스위치 내부 버그를 고치기 위해 key 옵션을 제거했습니다!
        start_exam = st.toggle("✍️ 형성평가 응시 시작 (주의: 새로고침하거나 끄면 10점 감점)", 
                               value=st.session_state.exam_started, 
                               disabled=is_completed)
            
        # 스위치가 켜졌을 때
        if start_exam and not st.session_state.exam_started:
            st.session_state.exam_started = True
            if st.session_state.db_status is None:
                st.session_state.db_status = "진행중"
                try:
                    result_sheet.append_row([s_id, s_name, "진행중", 0, "", "", ""])
                    st.session_state.row_index = len(result_sheet.get_all_values())
                except Exception as e:
                    st.error(f"구글 시트 저장 실패: {e}")
            st.rerun() 

        # 스위치가 꺼졌을 때 (도망침)
        elif not start_exam and st.session_state.exam_started:
            st.session_state.exam_started = False
            if st.session_state.db_status == "진행중":
                st.session_state.cheating_penalty += 10
                try:
                    result_sheet.update_cell(st.session_state.row_index, 4, st.session_state.cheating_penalty)
                except Exception:
                    pass
                st.error("🚨 [경고] 시험 스위치를 임의로 껐습니다. 10점이 감점되었습니다! 퀴즈를 보려면 다시 켜세요.")
            st.rerun()

        if st.session_state.exam_started and st.session_state.db_status == "진행중":
            st.warning("🚨 [주의] 평가가 진행 중입니다. 화면을 이탈하면 경고 알림이 발생합니다.")
            
            components.html(
                """
                <script>
                document.addEventListener("visibilitychange", function() {
                    if (document.hidden) {
                        window.parent.alert("🚨 [경고] 화면 이탈이 감지되었습니다! 부정행위로 간주될 수 있습니다.");
                    }
                });
                </script>
                """,
                height=0
            )
            
            with st.form("quiz_form"):
                st.markdown("---")
                user_answers = []
                for i, q in enumerate(st.session_state.quiz_questions):
                    st.markdown(f"#### 문제 {i+1}.")
                    if q.get("img"):
                        img_path = os.path.join(parent_folder, q["img"])
                        st.image(img_path, use_container_width=True)
                    st.write(q["q"])
                    ans = st.radio("선택해 주세요.", q["options"], key=f"q_{i}", index=None)
                    user_answers.append(ans)
                
                st.markdown("---")
                submitted = st.form_submit_button("답안 제출하기")
                
                if submitted:
                    if None in user_answers:
                        st.error("⚠️ 풀지 않은 문제가 있습니다. 모든 문제의 답을 선택해 주세요!")
                    else:
                        correct_count = 0
                        for i, q in enumerate(st.session_state.quiz_questions):
                            if user_answers[i] == q["answer"]:
                                correct_count += 1
                        
                        base_score = 100 - ((5 - correct_count) * 10)
                        final_score = base_score - st.session_state.cheating_penalty
                        
                        try:
                            result_sheet.update_cell(st.session_state.row_index, 3, "완료")
                            result_sheet.update_cell(st.session_state.row_index, 4, st.session_state.cheating_penalty)
                            result_sheet.update_cell(st.session_state.row_index, 5, correct_count)
                            result_sheet.update_cell(st.session_state.row_index, 6, base_score)
                            result_sheet.update_cell(st.session_state.row_index, 7, final_score)
                            
                            st.session_state.db_status = "완료"
                            st.session_state.quiz_results = {"correct_count": correct_count, "base_score": base_score}
                            st.rerun() 
                        except Exception as e:
                            st.error(f"구글 시트 저장 실패! 오류 내용: {e}")

        if st.session_state.db_status == "완료" and st.session_state.quiz_results is not None:
            base_score = st.session_state.quiz_results["base_score"]
            final_score = base_score - st.session_state.cheating_penalty
            
            st.divider()
            st.subheader("📊 채점 결과")
            st.write(f"* 맞힌 문제: **5문제 중 {st.session_state.quiz_results['correct_count']}문제**")
            st.write(f"* 기본 점수: **{base_score}점** (100점 만점 / 틀린 문제당 -10점)")
            if st.session_state.cheating_penalty > 0:
                st.write(f"* 스위치 OFF / 새로고침 감점: **-{st.session_state.cheating_penalty}점**")
            st.write(f"### 최종 점수: {final_score}점")
            
            if final_score == 100:
                st.success("🎉 완벽합니다! 만점입니다!")
            elif final_score >= 80:
                st.info("👍 잘했습니다! 조금만 더 복습해 볼까요?")
            else:
                st.error("💪 개념 학습 탭으로 돌아가서 내용을 다시 한번 꼼꼼히 확인해 보세요!")
