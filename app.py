import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import random

# --- 0. 網頁基本設定與 CSS 極致優化 ---
st.set_page_config(page_title="V7 Intelligence 5.6", layout="wide", page_icon="🎲")

# CSS: 隱藏官方元素 + 手機版面極致壓縮
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 主容器：預測框 */
    .main-card {
        text-align: center;
        border: 2px solid #ddd;
        padding: 5px;
        border-radius: 12px;
        background: #fff;
        margin-bottom: 5px; /* 減少與下方間距 */
    }
    .predict-zh { font-size: 55px; font-weight: 900; line-height: 1.0; margin-top: 5px; }
    .predict-en { font-size: 20px; font-weight: bold; opacity: 0.9; margin-top: -5px; margin-bottom: 5px; }
    .win-rate { font-size: 12px; color: #888; margin-top: 0px; }
    
    /* 配注建議框 */
    .advice-box {
        text-align: center;
        border: 1.5px dashed #ccc;
        padding: 6px;
        border-radius: 8px;
        background: #fcfcfc;
        margin-bottom: 8px; /* 緊貼按鈕區 */
        font-weight: bold;
        font-size: 16px;
    }

    /* 按鈕與球優化 */
    .stButton>button { height: 45px !important; font-size: 16px !important; width: 100%; margin-top: 0px; }
    .history-ball {
        display: inline-block; width: 32px; height: 32px; line-height: 32px;
        border-radius: 50%; text-align: center; color: white;
        font-weight: bold; margin: 2px; font-size: 12px;
    }
    .ball-b { background-color: #FF4B4B; }
    .ball-p { background-color: #1E90FF; }
    .ball-t { background-color: #28a745; }
    
    /* 調整 streamlit 預設間距 */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
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
        worksheet = sh.worksheet("Sheet1") # 確保大寫
        data = worksheet.get_all_records()
        df = pd.DataFrame(data).astype(str)
        valid_users = df['Account'].dropna().str.strip().tolist() if 'Account' in df.columns else []
    except Exception as e:
        st.error(f"系統連線錯誤: {e}")
        valid_users = []

    # 網址參數登入
    url_uid = st.query_params.get("uid", None)
    if url_uid and url_uid in valid_users:
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = url_uid
        st.rerun()

    # 手動登入介面
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("🔒 V7 系統驗證")
        with st.form("login_form"):
            input_user = st.text_input("會員帳號")
            input_pass = st.text_input("通行碼", type="password")
            if st.form_submit_button("登入系統"):
                system_pass = st.secrets["system_password"]
                if input_user in valid_users and input_pass == system_pass:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = input_user
                    st.rerun()
                else:
                    st.error("❌ 驗證失敗")
    return False

# --- 核心 2: AI 邏輯大腦 (Chaos Factor + Chop Logic) ---
class BaccaratBrain:
    def __init__(self):
        self.history_db = {'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65, 'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068}

    def calculate_final_decision(self, full_history):
        # 1. 強制只取最新 10 筆
        history = full_history[-10:]
        if len(history) < 3:
            return {"strategies": [0.5, 0.5, 0.5, 0.5], "final_b": 0.5, "final_p": 0.5}

        latest = history[-1]
        
        # --- 2. Big Data (歷史排列) ---
        p_bd = self.history_db.get(history[-3]+history[-2]+history[-1], self.history_db['default'])

        # --- 3. Streak & Chaos (長龍與亂數斷龍) ---
        streak = 0
        for v in reversed(history):
            if v == latest: streak += 1
            else: break
            
        p_st = 0.5 # 預設
        is_chaos_cut = False
        
        if streak >= 3:
            # 正常追龍
            p_st = 0.85 if latest == 'B' else 0.15
            # Chaos Factor: 龍越長，斷龍機率越高 (3~7)
            if streak <= 7:
                cut_chance = 0.15 + (streak - 3) * 0.12 # 3:15%, 4:27%, 5:39%...
                if random.random() < cut_chance:
                    is_chaos_cut = True
            else:
                is_chaos_cut = True # 8連以上強制視為高危險

        # --- 4. Chop Logic (多元單跳偵測) ---
        p_cp = 0.50
        chop_strength = 0
        
        # 取得最後 6 局 (若不足則補 None)
        h_rev = history[::-1] + [None]*6
        r1, r2, r3, r4, r5, r6 = h_rev[0], h_rev[1], h_rev[2], h_rev[3], h_rev[4], h_rev[5]

        # 邏輯 A: 標準單跳 (BPBP...)
        if r1 != r2 and r2 != r3:
            chop_strength = 0.8
            p_cp = 0.20 if r1 == 'B' else 0.80 # 預測跳
        
        # 邏輯 B: 雙跳 (BBPP...)
        elif r1 == r2 and r3 == r4 and r1 != r3:
            chop_strength = 0.7
            p_cp = 0.15 if r1 == 'B' else 0.85 # 預測換色

        # 邏輯 C: 2-1 跳 (BBP BBP)
        elif r1 == r2 and r3 != r2 and r4 != r3 and r5 == r4:
             chop_strength = 0.6
             p_cp = 0.30 if r1 == 'B' else 0.70 # 預測換色

        # Chaos Factor for Chop: 單跳 4-6 把後隨機轉龍
        is_chop_break = False
        # 簡單計算單跳長度
        chop_len = 0
        for i in range(len(history)-1):
            if history[-(i+1)] != history[-(i+2)]: chop_len += 1
            else: break
            
        if 4 <= chop_len <= 6:
            # 隨機決定是否這把連龍
            if random.random() < (0.3 + (chop_len-4)*0.2):
                is_chop_break = True # 預測會連 (Breaking the chop)

        # --- 5. 綜合權重計算 ---
        # 權重分配
        w_bd, w_st, w_cp, w_chaos = 0.25, 0.25, 0.25, 0.25
        
        # Chaos 修正 (斷龍信號)
        p_chaos = 0.5
        if is_chaos_cut: # 斷龍
            p_chaos = 0.10 if latest == 'B' else 0.90
            w_st = 0.10 # 降低追龍權重
            w_chaos = 0.40 # 提高 Chaos 權重
            
        if is_chop_break: # 斷單跳 (轉龍)
            p_cp = 0.80 if latest == 'B' else 0.20 # 預測跟隨上局 (連)
            w_cp = 0.50 # 大幅提升 Chop 變盤權重

        final_b = (p_bd * w_bd) + (p_st * w_st) + (p_cp * w_cp) + (p_chaos * w_chaos)
        
        # 和局鎖定 9.5%
        is_tie = random.random() < 0.095

        return {
            "strategies": [p_bd, p_st, p_cp, p_chaos],
            "final_b": final_b, "final_p": 1.0 - final_b,
            "is_tie": is_tie
        }

# --- 配注建議邏輯 ---
def get_betting_advice(prob, is_tie):
    if is_tie: return "🌟 Lucky Shot (小注和)", "#28a745"
    p = prob * 100
    if p > 85: return "🔥🔥🔥 強力重注", "#d32f2f" # 深紅
    elif p > 65: return "🔥 加注進攻", "#f57c00" # 橘
    elif p > 50: return "💰 平注跟隨", "#1976d2" # 藍
    return "👀 暫停觀望", "#757575" # 灰

# --- 主介面 ---
if check_auth():
    # 側邊欄：功能區
    with st.sidebar:
        st.success(f"👤 會員: {st.session_state['user_id']}")
        rid = st.text_input("房號", "VIP-01")
        
        with st.expander("⚙️ 初始牌局設定", expanded=True):
            st.caption("輸入前 5 局 (左舊 -> 右新)")
            opt = ["莊", "閒", "和"]
            map_v = {"莊": "B", "閒": "P", "和": "T"}
            c1, c2, c3, c4, c5 = st.columns(5)
            s1 = c1.selectbox("1", opt, key="s1")
            s2 = c2.selectbox("2", opt, key="s2")
            s3 = c3.selectbox("3", opt, key="s3")
            s4 = c4.selectbox("4", opt, index=1, key="s4")
            s5 = c5.selectbox("5", opt, index=1, key="s5")
            
            if st.button("🔄 重置分析"):
                st.session_state["game_history"] = [map_v[s1], map_v[s2], map_v[s3], map_v[s4], map_v[s5]]
                st.rerun()

        if st.session_state["user_id"] == "admin":
            st.info("管理員模式")
            u_name = st.text_input("開通帳號")
            if u_name:
                st.code(f"網址：https://v7-baccarat-project-pyhivmxmirvwp3cskxj2pu.streamlit.app/\n帳號：{u_name}\n密碼：v7888")

        if st.button("登出"):
            st.session_state["logged_in"] = False
            st.rerun()

    # 主畫面邏輯
    if "game_history" not in st.session_state:
        st.session_state["game_history"] = ['B', 'B', 'B', 'P', 'P']

    brain = BaccaratBrain()
    res = brain.calculate_final_decision(st.session_state["game_history"])
    
    # 視覺呈現
    win_b = res['final_b'] > res['final_p']
    main_color = "#FF4B4B" if win_b else "#1E90FF"
    zh_text = "莊" if win_b else "閒"
    en_text = "(BANKER)" if win_b else "(PLAYER)"
    
    if res['is_tie']:
        main_color = "#28a745"
        zh_text = "和"
        en_text = "(TIE)"

    prob_val = max(res['final_b'], res['final_p'])
    advice, advice_color = get_betting_advice(prob_val, res['is_tie'])

    # --- UI 佈局: 預測 + 配注 + 按鈕 (緊湊排列) ---
    # 1. 預測結果卡片
    st.markdown(f"""
    <div class="main-card" style="border-color: {main_color};">
        <div style="font-size: 13px; color: #888; margin-bottom: -5px;">{rid} | 下一局預測 ({len(st.session_state['game_history'])+1})</div>
        <div class="predict-zh" style="color: {main_color};">{zh_text}</div>
        <div class="predict-en" style="color: {main_color};">{en_text}</div>
        <div class="win-rate">綜合勝率: {prob_val*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 配注建議
    st.markdown(f"""
    <div class="advice-box" style="color: {advice_color}; border-color: {advice_color};">
        {advice}
    </div>
    """, unsafe_allow_html=True)

    # 3. 操作按鈕 (三欄緊湊)
    b_col, p_col, t_col = st.columns(3)
    if b_col.button("🔴 莊贏"): 
        st.session_state["game_history"].append("B")
        st.rerun()
    if p_col.button("🔵 閒贏"): 
        st.session_state["game_history"].append("P")
        st.rerun()
    if t_col.button("🟢 和局"): 
        st.session_state["game_history"].append("T")
        st.rerun()
        
    st.caption("👆 點擊上方按鈕回報結果，系統即時更新分析")

    # 4. 歷史路單 (10顆球)
    history_view = st.session_state["game_history"][-10:]
    balls_html = "".join([f'<div class="history-ball ball-{h.lower()}">{"莊" if h=="B" else "閒" if h=="P" else "和"}</div>' for h in history_view])
    st.markdown(f'<div style="background:#f5f5f5; padding:8px; border-radius:10px; text-align:center; margin-top: 5px;">{balls_html}</div>', unsafe_allow_html=True)

    # 5. 四維決策圖表 (新增 Chop 欄位)
    with st.expander("📊 AI 四維詳細決策數據 (Big Data / Streak / Chop / Chaos)"):
        labels = ['Big Data (歷史)', 'Streak (趨勢)', 'Chop (規律)', 'Chaos (亂數)']
        vals = [p * 100 for p in res['strategies']]
        
        fig, ax = plt.subplots(figsize=(10, 3.5))
        ax.barh(labels, vals, color='#FF4B4B', label='Banker')
        ax.barh(labels, [100-v for v in vals], left=vals, color='#1E90FF', label='Player')
        ax.set_xlim(0, 100)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, frameon=False)
        st.pyplot(fig)
