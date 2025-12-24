import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import random

# --- 0. 網頁基本設定與介面隱藏 ---
st.set_page_config(page_title="V7 Intelligence 5.6", layout="wide", page_icon="🎲")

# 隱藏 Streamlit 官方裝飾與標記
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .main-box {
        text-align: center; border: 2px solid #ddd; padding: 10px;
        border-radius: 12px; background: #fff; margin-bottom: 8px;
    }
    .main-rec { font-size: 40px; font-weight: 900; line-height: 1; margin: 5px 0; }
    .main-sub { font-size: 16px; margin-top: -5px; font-weight: bold; }
    .bet-box {
        text-align: center; border: 1.5px dashed #ccc;
        padding: 5px; border-radius: 8px; background: #fcfcfc; margin-bottom: 10px;
    }
    .history-ball {
        display: inline-block; width: 35px; height: 35px; line-height: 35px;
        border-radius: 50%; text-align: center; color: white;
        font-weight: bold; margin: 2px; font-size: 13px;
    }
    .ball-b { background-color: #FF4B4B; }
    .ball-p { background-color: #1E90FF; }
    .ball-t { background-color: #28a745; }
    .stButton>button { height: 40px !important; font-size: 15px !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心 1: 權限驗證系統 ---
def check_auth():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = ""

    if st.session_state["logged_in"]:
        return True

    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["google_sheets_creds"], scopes=scopes)
        client = gspread.authorize(creds)
        sheet_url = "https://docs.google.com/spreadsheets/d/1uNWgRDty4hMOKt71UATZA5r4WcHVDN5ZaC9yQ030Nto/edit#gid=1622652027"
        sh = client.open_by_url(sheet_url)
        worksheet = sh.worksheet("Sheet1")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data).astype(str)
        valid_users = df['Account'].dropna().str.strip().tolist() if 'Account' in df.columns else []
    except Exception as e:
        st.error(f"系統連線錯誤: {e}")
        valid_users = []

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔒 V7 系統驗證")
        with st.form("login_form"):
            input_user = st.text_input("會員帳號")
            input_pass = st.text_input("通行碼", type="password")
            if st.form_submit_button("登入系統"):
                if input_user in valid_users and input_pass == st.secrets["system_password"]:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = input_user
                    st.rerun()
                else:
                    st.error("❌ 驗證失敗")
    return False

# --- 核心 2: AI 四維滾動評估大腦 ---
class BaccaratBrain:
    def __init__(self):
        self.history_db = {'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65, 'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068}

    def calculate_final_decision(self, full_history):
        # 嚴格執行「最新 10 筆」分析邏輯
        history = full_history[-10:]
        if len(history) < 3:
            return {"strategies": [0.5, 0.5, 0.5, 0.5], "final_b": 0.5, "final_p": 0.5, "streak": 0}

        # 1. Big Data (大數據趨勢)
        p_bd = self.history_db.get(history[-3]+history[-2]+history[-1], self.history_db['default'])

        # 2. Streak (追龍強度)
        streak = 0
        latest = history[-1]
        for v in reversed(history):
            if v == latest: streak += 1
            else: break
        p_st = 0.88 if latest == 'B' else 0.12 if streak >= 3 else 0.52 if latest == 'B' else 0.48

        # 3. Chop (新增: 單跳規律獨立欄位)
        p_cp = 0.50
        if len(history) >= 4:
            if history[-1] != history[-2] and history[-2] != history[-3]: # 標準單跳
                p_cp = 0.15 if history[-1] == 'B' else 0.85
            elif history[-1] == history[-2] and history[-3] == history[-4] and history[-1] != history[-3]: # 雙跳
                p_cp = 0.20 if history[-1] == 'B' else 0.80

        # 4. Reversal (斷龍隨機訊號)
        is_rev_active = (streak >= 6 and random.random() < 0.65) or streak >= 8
        p_rv = (0.12 if latest == 'B' else 0.88) if is_rev_active else 0.50

        # 動態權重分配
        w = [0.15, 0.10, 0.40, 0.35] if is_rev_active else [0.30, 0.35, 0.25, 0.10]
        final_b = (p_bd * w[0]) + (p_st * w[1]) + (p_cp * w[2]) + (p_rv * w[3])
        
        return {
            "strategies": [p_bd, p_st, p_cp, p_rv],
            "final_b": final_b, "final_p": 1.0 - final_b,
            "streak_count": streak, "is_reversal": is_rev_active
        }

# --- 介面執行 ---
if check_auth():
    # 側邊欄重新啟用：確保初始化欄位與房號存在
    with st.sidebar:
        st.success(f"👤 會員: {st.session_state['user_id']}")
        rid = st.text_input("房號設定", "VIP-01")
        st.divider()
        
        st.subheader("⚙️ 初始開局設定")
        st.caption("請輸入前 5 局紀錄 (左為舊)")
        opt = ["莊", "閒", "和"]
        map_t = {"莊": "B", "閒": "P", "和": "T"}
        col1, col2, col3, col4, col5 = st.columns(5)
        s1 = col1.selectbox("1", opt, key="s1")
        s2 = col2.selectbox("2", opt, key="s2")
        s3 = col3.selectbox("3", opt, key="s3")
        s4 = col4.selectbox("4", opt, index=1, key="s4")
        s5 = col5.selectbox("5", opt, index=1, key="s5")
        
        if st.button("🔄 設定並開始分析"):
            st.session_state["game_history"] = [map_t[s1], map_t[s2], map_t[s3], map_t[s4], map_t[s5]]
            st.rerun()

        if st.session_state["user_id"] == "admin":
            with st.expander("🛠️ 管理員工具"):
                u_name = st.text_input("開通帳號")
                if u_name:
                    st.code(f"✅ 帳號設定完成\n網址：https://v7-baccarat-project-pyhivmxmirvwp3cskxj2pu.streamlit.app/\n帳號：{u_name}\n密碼：v7888")

        if st.button("安全登出"):
            st.session_state["logged_in"] = False
            st.rerun()

    # 主畫面邏輯
    if "game_history" not in st.session_state:
        st.session_state["game_history"] = ['B', 'B', 'B', 'P', 'P']

    brain = BaccaratBrain()
    res = brain.calculate_final_decision(st.session_state["game_history"])
    
    # 視覺顏色判定
    win_b = res['final_b'] > res['final_p']
    color = "#FF4B4B" if win_b else "#1E90FF"
    main_text = "莊 BANKER" if win_b else "閒 PLAYER"
    
    st.markdown(f"""
    <div class="main-box" style="border-color: {color};">
        <div style="font-size: 13px; color: #888;">{rid} | 下一局預測 ({len(st.session_state['game_history'])+1})</div>
        <div class="main-rec" style="color: {color};">{main_text.split(' ')[0]}</div>
        <div class="main-sub" style="color: {color};">({main_text.split(' ')[1]})</div>
        <div style="font-size: 12px; color: gray;">綜合評估勝率: {max(res['final_b'], res['final_p'])*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    # 配注建議
    p_win = max(res['final_b'], res['final_p'])
    advice, a_color = ("🔥🔥🔥 重注", "#4CAF50") if p_win > 0.8 else ("🔥 加加注", "#FF9800") if p_win > 0.6 else ("💰 平注", "#2196F3")
    st.markdown(f'<div class="bet-box" style="border-color:{a_color}; color:{a_color}; font-weight:bold;">{advice}</div>', unsafe_allow_html=True)

    # 結果回報區
    st.caption("📝 實戰結果回報 (Update Result)")
    b_c, p_c, t_c = st.columns(3)
    if b_c.button("🔴 莊贏"): st.session_state["game_history"].append("B"); st.rerun()
    if p_c.button("🔵 閒贏"): st.session_state["game_history"].append("P"); st.rerun()
    if t_c.button("🟢 和局"): st.session_state["game_history"].append("T"); st.rerun()

    # 歷史趨勢球
    history_view = st.session_state["game_history"][-10:]
    balls_html = "".join([f'<div class="history-ball ball-{h.lower()}">{"莊" if h=="B" else "閒" if h=="P" else "和"}</div>' for h in history_view])
    st.markdown(f'<div style="background:#f5f5f5; padding:8px; border-radius:10px; text-align:center;">{balls_html}</div>', unsafe_allow_html=True)

    # 四維圖表顯示 (包含單獨的 Chop 欄位)
    with st.expander("📊 查看 AI 四維詳細決策數據"):
        labels = ['Big Data (歷史大數據)', 'Streak (趨勢持平)', 'Chop (單跳/規律偵測)', 'Reversal (斷龍訊號)']
        vals = [p * 100 for p in res['strategies']]
        fig, ax = plt.subplots(figsize=(10, 3.2))
        ax.barh(labels, vals, color='#FF4B4B', label='Banker')
        ax.barh(labels, [100-v for v in vals], left=vals, color='#1E90FF', label='Player')
        ax.set_xlim(0, 100)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.28), ncol=2, frameon=False)
        st.pyplot(fig)
