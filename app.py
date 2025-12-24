import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import random

# --- 0. 網頁基本設定與 CSS 優化 ---
st.set_page_config(page_title="V7 Intelligence 5.6", layout="wide", page_icon="🎲")

# 隱藏 Streamlit 官方裝飾，讓介面更專業
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
    .main-rec { font-size: 48px; font-weight: 900; line-height: 1; margin: 10px 0; }
    .main-sub { font-size: 18px; margin-top: -5px; font-weight: bold; }
    .bet-box {
        text-align: center; border: 1.5px dashed #ccc;
        padding: 8px; border-radius: 8px; background: #fcfcfc; margin-bottom: 10px;
    }
    .history-ball {
        display: inline-block; width: 38px; height: 38px; line-height: 38px;
        border-radius: 50%; text-align: center; color: white;
        font-weight: bold; margin: 2px; font-size: 14px;
    }
    .ball-b { background-color: #FF4B4B; }
    .ball-p { background-color: #1E90FF; }
    .ball-t { background-color: #28a745; }
    .stButton>button { height: 45px !important; font-size: 16px !important; width: 100%; }
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

    url_uid = st.query_params.get("uid", None)
    if url_uid and url_uid in valid_users:
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = url_uid
        st.rerun()

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔒 V7 系統驗證")
        with st.form("login_form"):
            input_user = st.text_input("會員帳號")
            input_pass = st.text_input("通行碼", type="password")
            if st.form_submit_button("登入"):
                if input_user in valid_users and input_pass == st.secrets["system_password"]:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = input_user
                    st.rerun()
                else:
                    st.error("❌ 驗證失敗")
    return False

# --- 核心 2: AI 四維運算大腦 (滾動 10 局分析) ---
class BaccaratBrain:
    def __init__(self):
        self.history_db = {'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65, 'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068}

    def calculate_final_decision(self, full_history):
        # 僅取最新 10 局進行綜合評估
        history = full_history[-10:]
        if len(history) < 3:
            return {"strategies": [0.5, 0.5, 0.5, 0.5], "final_b": 0.5, "final_p": 0.5, "streak": 0, "rev": False}

        # 1. Big Data (歷史排列)
        p_bd = self.history_db.get(history[-3]+history[-2]+history[-1], self.history_db['default'])

        # 2. Streak (追龍強度)
        streak = 0
        latest = history[-1]
        for v in reversed(history):
            if v == latest: streak += 1
            else: break
        p_st = 0.85 if latest == 'B' else 0.15 if streak >= 3 else 0.55 if latest == 'B' else 0.45

        # 3. Chop (單跳/規律)
        p_cp = 0.50
        if history[-1] != history[-2] and history[-2] != history[-3]:
            p_cp = 0.20 if history[-1] == 'B' else 0.80

        # 4. Reversal (斷龍隨機訊號)
        is_rev = (streak >= 6 and random.random() < 0.65) or streak >= 8
        p_rev = (0.10 if latest == 'B' else 0.90) if is_rev else 0.50

        # 綜合評估權重
        if is_rev:
            w = [0.15, 0.10, 0.45, 0.30] # 斷龍時 Reversal 與 Chop 優先
        else:
            w = [0.30, 0.30, 0.25, 0.15] # 平時 Big Data 與 Streak 優先
            
        final_b = (p_bd * w[0]) + (p_st * w[1]) + (p_cp * w[2]) + (p_rev * w[3])
        
        return {
            "strategies": [p_bd, p_st, p_cp, p_rev],
            "final_b": final_b, "final_p": 1.0 - final_b,
            "streak_count": streak, "is_reversal_active": is_rev, "latest_val": latest
        }

# --- 主程式 ---
if check_auth():
    # 側邊欄：所有設定欄位回歸
    with st.sidebar:
        st.success(f"👤 User: {st.session_state['user_id']}")
        rid = st.text_input("房號", "VIP-01")
        st.divider()
        st.header("⚙️ 初始設定")
        st.caption("輸入前 5 局資料 (左舊至右新)")
        options = ["莊", "閒", "和"]
        trans = {"莊": "B", "閒": "P", "和": "T"}
        c1, c2, c3, c4, c5 = st.columns(5)
        l1 = c1.selectbox("1", options, key="l1")
        l2 = c2.selectbox("2", options, key="l2")
        l3 = c3.selectbox("3", options, key="l3")
        l4 = c4.selectbox("4", options, index=1, key="l4")
        l5 = c5.selectbox("5", options, index=1, key="l5")
        
        if st.button("🔄 設定/重置牌局"):
            st.session_state["game_history"] = [trans[l1], trans[l2], trans[l3], trans[l4], trans[l5]]
            st.rerun()

        if st.session_state["user_id"] == "admin":
            with st.expander("🛠️ 開通通知模板"):
                new_u = st.text_input("會員帳號")
                if new_u:
                    st.code(f"✅ [開通成功]\n網址：{st.query_params.get('app_url', '請手動複製網址')}\n帳號：{new_u}\n密碼：v7888")
        
        if st.button("登出"):
            st.session_state["logged_in"] = False
            st.rerun()

    if "game_history" not in st.session_state:
        st.session_state["game_history"] = ['B', 'B', 'B', 'P', 'P']

    # 運算與渲染
    brain = BaccaratBrain()
    res = brain.calculate_final_decision(st.session_state["game_history"])
    color = "#FF4B4B" if res['final_b'] > res['final_p'] else "#1E90FF"
    rec_text = "莊 BANKER" if res['final_b'] > res['final_p'] else "閒 PLAYER"
    if random.random() < 0.08: # 和局隨機訊號觸發
        rec_text = "和 TIE"
        color = "#28a745"

    st.markdown(f"""
    <div class="main-box" style="border-color: {color};">
        <div style="font-size: 14px; color: #888;">{rid} 下一局預測 ({len(st.session_state['game_history'])+1})</div>
        <div class="main-rec" style="color: {color};">{rec_text.split(' ')[0]}</div>
        <div class="main-sub" style="color: {color};">({rec_text.split(' ')[1]})</div>
        <div style="font-size: 12px; color: gray;">綜合勝率: {max(res['final_b'], res['final_p'])*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    # 配注建議 (緊湊)
    p_val = max(res['final_b'], res['final_p'])
    bet_title, b_color = ("🔥🔥🔥 重注", "#4CAF50") if p_val > 0.8 else ("🔥 加注", "#FF9800") if p_val > 0.6 else ("💰 平注", "#2196F3")
    st.markdown(f'<div class="bet-box" style="border-color:{b_color}; color:{b_color}; font-weight:bold;">{bet_title}</div>', unsafe_allow_html=True)

    # 回報按鈕
    st.caption("📝 實戰結果回報")
    bc, pc, tc = st.columns(3)
    if bc.button("🔴 莊"): st.session_state["game_history"].append("B"); st.rerun()
    if pc.button("🔵 閒"): st.session_state["game_history"].append("P"); st.rerun()
    if tc.button("🟢 和"): st.session_state["game_history"].append("T"); st.rerun()

    # 歷史紀錄球 (10局)
    display = st.session_state["game_history"][-10:]
    balls = "".join([f'<div class="history-ball ball-{h.lower()}">{"莊" if h=="B" else "閒" if h=="P" else "和"}</div>' for h in display])
    st.markdown(f'<div style="background:#f0f0f0; padding:8px; border-radius:10px; text-align:center;">{balls}</div>', unsafe_allow_html=True)

    # 四維決策數據圖表
    with st.expander("📊 查看 AI 詳細決策數據"):
        strat_names = ['Big Data (歷史大數據)', 'Streak (趨勢)', 'Chop (規律/單跳)', 'Reversal (斷龍訊號)']
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.barh(strat_names, [p * 100 for p in res['strategies']], color='#FF4B4B', label='Banker')
        ax.barh(strat_names, [(1-p) * 100 for p in res['strategies']], left=[p * 100 for p in res['strategies']], color='#1E90FF', label='Player')
        ax.set_xlim(0, 100)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=2, frameon=False)
        st.pyplot(fig)
