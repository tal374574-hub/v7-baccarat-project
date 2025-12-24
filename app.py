import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import random

# --- 0. 網頁基本設定與 CSS 優化 ---
st.set_page_config(page_title="V7 Intelligence 5.6", layout="wide", page_icon="🎲")

# 隱藏 Streamlit 官方選單與頁尾，讓畫面更專業
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 緊湊佈局 CSS */
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
        display: inline-block; width: 40px; height: 40px; line-height: 40px;
        border-radius: 50%; text-align: center; color: white;
        font-weight: bold; margin: 3px; font-size: 16px;
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
        
        # 修正試算表連線邏輯
        sheet_url = "https://docs.google.com/spreadsheets/d/1uNWgRDty4hMOKt71UATZA5r4WcHVDN5ZaC9yQ030Nto/edit#gid=1622652027"
        sh = client.open_by_url(sheet_url)
        worksheet = sh.worksheet("Sheet1") # 確保對應大寫 Sheet1
        data = worksheet.get_all_records()
        df = pd.DataFrame(data).astype(str)

        if 'Account' in df.columns:
            valid_users = df['Account'].dropna().str.strip().tolist()
        else:
            valid_users = []
    except Exception as e:
        st.error(f"系統連線錯誤: {e}")
        valid_users = []

    # 處理 URL 直接登入邏輯
    url_uid = st.query_params.get("uid", None)
    if url_uid and url_uid in valid_users:
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = url_uid
        st.rerun()

    # 登入表單介面
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔒 V7 系統驗證")
        with st.form("login_form"):
            input_user = st.text_input("會員帳號 (Account)")
            input_pass = st.text_input("系統通行碼 (Passcode)", type="password")
            if st.form_submit_button("登入系統", type="primary"):
                system_pass = st.secrets["system_password"]
                if input_user in valid_users and input_pass == system_pass:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = input_user
                    st.rerun()
                else:
                    st.error("❌ 帳號未授權或密碼錯誤")
    return False

# --- 核心 2: AI 多策略運算大腦 (智能權重切換版) ---
class BaccaratBrain:
    def __init__(self):
        self.history_db = {'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65, 'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068}

    def calculate_final_decision(self, history_list):
        if len(history_list) < 3:
            return {"strategies": [0.5, 0.5, 0.5], "final_b": 0.5, "final_p": 0.5, "streak_count": 0, "is_reversal_active": False, "latest_val": None}

        # 1. Big Data (歷史大數據)
        r1, r2, r3 = history_list[-1], history_list[-2], history_list[-3]
        p_bd = self.history_db.get(r3+r2+r1, self.history_db['default'])

        # 2. Streak (趨勢/長龍)
        streak = 0
        latest = history_list[-1]
        for v in reversed(history_list):
            if v == latest: streak += 1
            else: break
        p_st = 0.85 if latest == 'B' else 0.15 if streak >= 3 else 0.55 if latest == 'B' else 0.45

        # 3. Chop (單跳/規律偵測)
        p_cp = 0.50
        r4 = history_list[-4] if len(history_list) >= 4 else None
        if r1 != r2 and r2 != r3: p_cp = 0.20 if r1 == 'B' else 0.80 # 單跳規律
        elif r1 == r2 and r3 == r4 and r1 != r3: p_cp = 0.15 if r1 == 'B' else 0.85 # 雙跳規律

        # 智能權重切換
        is_rev = (streak >= 6 and random.random() < 0.6) or streak >= 8
        if is_rev:
            w = {"bd": 0.20, "st": 0.10, "cp": 0.70} # 斷龍時大幅提升 Chop 權重
            target_p = 0.10 if latest == 'B' else 0.90
            final_b = (p_bd * w["bd"]) + (target_p * w["st"]) + (p_cp * w["cp"])
        else:
            w = {"bd": 0.40, "st": 0.35, "cp": 0.25} # 標準模式
            final_b = (p_bd * w["bd"]) + (p_st * w["st"]) + (p_cp * w["cp"])

        return {
            "strategies": [p_bd, p_st, p_cp],
            "final_b": final_b, "final_p": 1.0 - final_b,
            "streak_count": streak, "is_reversal_active": is_rev,
            "latest_val": latest, "is_tie_triggered": random.random() < 0.09
        }

# --- 輔助功能 ---
def get_betting_advice(win_rate, is_tie=False):
    if is_tie: return "🌟 高賠率信號 (Lucky Shot)", "#28a745"
    p = win_rate * 100
    if p > 80: return "🔥🔥🔥 重注 (3單位)", "#4CAF50"
    elif p > 60: return "🔥 加注 (2單位)", "#FF9800"
    elif p > 50: return "💰 平注 (1單位)", "#2196F3"
    return "👀 觀望 (Pass)", "#9E9E9E"

# --- 主程式執行 ---
if check_auth():
    if "game_history" not in st.session_state:
        st.session_state["game_history"] = ['B', 'B', 'B', 'P', 'P'] # 初始範例

    # 側邊欄：管理員工具
    with st.sidebar:
        if st.session_state["user_id"] == "admin":
            with st.expander("🛠️ 開通通知模板"):
                new_u = st.text_input("會員帳號")
                if new_u:
                    msg = f"✅ [開通成功]\n網址：https://v7-baccarat-project-pyhivmxmirvwp3cskxj2pu.streamlit.app/\n帳號：{new_u}\n密碼：v7888"
                    st.code(msg)
        if st.button("登出系統"):
            st.session_state["logged_in"] = False
            st.rerun()

    # 主畫面渲染
    brain = BaccaratBrain()
    res = brain.calculate_final_decision(st.session_state["game_history"])
    
    # 決定顏色與文字
    color = "#FF4B4B" if res['final_b'] > res['final_p'] else "#1E90FF"
    rec_text = "莊 BANKER" if res['final_b'] > res['final_p'] else "閒 PLAYER"
    if res['is_tie_triggered']: 
        rec_text = "和 TIE"
        color = "#28a745"
    
    bet_title, border_color = get_betting_advice(max(res['final_b'], res['final_p']), res['is_tie_triggered'])

    # 預測框
    st.markdown(f"""
    <div class="main-box" style="border-color: {color};">
        <div style="font-size: 14px; color: #888;">下一局預測 ({len(st.session_state['game_history'])+1})</div>
        <div class="main-rec" style="color: {color};">{rec_text.split(' ')[0]}</div>
        <div class="main-sub" style="color: {color};">({rec_text.split(' ')[1]})</div>
        <div style="font-size: 12px; color: gray;">綜合勝率: {max(res['final_b'], res['final_p'])*100:.1f}%</div>
    </div>
    <div class="bet-box" style="border-color: {border_color};">
        <div style="font-size: 16px; color: {border_color}; font-weight: bold;">{bet_title}</div>
    </div>
    """, unsafe_allow_html=True)

    # 回報按鈕 (縮小間距)
    st.caption("📝 實戰結果回報")
    bc, pc, tc = st.columns(3)
    if bc.button("🔴 莊"): 
        st.session_state["game_history"].append("B")
        st.rerun()
    if pc.button("🔵 閒"): 
        st.session_state["game_history"].append("P")
        st.rerun()
    if tc.button("🟢 和"): 
        st.session_state["game_history"].append("T")
        st.rerun()

    # 歷史紀錄球
    display_history = st.session_state["game_history"][-10:]
    balls_html = "".join([f'<div class="history-ball ball-{h.lower()}">{"莊" if h=="B" else "閒" if h=="P" else "和"}</div>' for h in display_history])
    st.markdown(f'<div style="background:#f0f0f0; padding:10px; border-radius:10px; overflow-x:auto; white-space:nowrap;">{balls_html}</div>', unsafe_allow_html=True)

    # AI 決策數據圖表
    with st.expander("📊 查看 AI 詳細決策數據"):
        fig, ax = plt.subplots(figsize=(10, 2.5))
        strat_names = ['Big Data (大數據)', 'Streak (趨勢)', 'Chop (單跳/規律)']
        ax.barh(strat_names, [p * 100 for p in res['strategies']], color='#FF4B4B', label='Banker')
        ax.barh(strat_names, [(1-p) * 100 for p in res['strategies']], left=[p * 100 for p in res['strategies']], color='#1E90FF', label='Player')
        ax.set_xlim(0, 100)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3), ncol=2, frameon=False)
        st.pyplot(fig)
