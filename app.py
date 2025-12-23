import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt # 新增繪圖庫

# --- 0. 網頁基本設定 (CSS 美化) ---
st.set_page_config(page_title="V7 Intelligence 2.0", layout="wide", page_icon="🎲")

# 注入自定義 CSS
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .win-banker { color: #FF4B4B; }
    .win-player { color: #1E90FF; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #00cc00); }
    </style>
    """, unsafe_allow_html=True)

# --- 核心 1: 權限驗證系統 (保持不變) ---
def check_auth():
    # 初始化登入狀態
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = ""

    # 如果已經登入，直接放行
    if st.session_state["logged_in"]:
        return True

    # 1. 讀取 Google Sheet 會員名單
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["google_sheets_creds"], scopes=scopes)
        client = gspread.authorize(creds)
        
        # ⚠️ 您的專屬網址
        sheet_url = "https://docs.google.com/spreadsheets/d/1uNWgRDty4hMOKt71UATZA5r4WcHVDN5ZaC9yQ030Nto/edit#gid=1622652027"
        
        sh = client.open_by_url(sheet_url)
        worksheet = sh.sheet1
        data = worksheet.get_all_records()
        df = pd.DataFrame(data).astype(str)

        if 'Account' in df.columns:
            valid_users = df['Account'].dropna().str.strip().tolist()
        else:
            valid_users = []

    except Exception as e:
        st.error(f"系統連線錯誤: {e}")
        valid_users = []

    # 2. 自動登入邏輯
    query_params = st.query_params
    url_uid = query_params.get("uid", None)

    if url_uid:
        if url_uid in valid_users:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = url_uid
            st.toast(f"🚀 歡迎回來, {url_uid}")
            time.sleep(1)
            st.rerun()
        else:
            st.toast("❌ 連結失效或會員未開通", icon="⚠️")

    # 3. 手動登入介面
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.title("🔒 V7 系統存取驗證")
        st.info("請輸入授權帳號與通行碼，或使用專屬連結進入。")
        
        with st.form("login_form"):
            input_user = st.text_input("會員帳號 (Account)")
            input_pass = st.text_input("系統通行碼 (Passcode)", type="password")
            submitted = st.form_submit_button("登入系統", type="primary")

        if submitted:
            system_pass = st.secrets.get("system_password", "0000")
            if input_user in valid_users and input_pass == system_pass:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = input_user
                st.rerun()
            else:
                st.error("❌ 帳號未授權或密碼錯誤")
    
    return False

# --- 核心 2: AI 多策略運算大腦 (升級版) ---
class BaccaratBrain:
    def __init__(self):
        # 這裡模擬大數據庫 (實際上您可以讓它去讀取您的 csv)
        self.history_db = {
            'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65,
            'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068 
        }

    def get_strategy_probabilities(self, r1, r2, r3):
        pattern = r1 + r2 + r3
        
        # 策略 A: 歷史大數據 (50%)
        prob_a = self.history_db.get(pattern, self.history_db['default'])

        # 策略 B: 追龍/慣性 (30%) - 前兩把一樣就追
        if r2 == r3:
            prob_b = 0.60 if r3 == 'B' else 0.40
        else:
            prob_b = 0.50

        # 策略 C: 反轉/單跳 (20%) - 跳來跳去就反著買
        if r2 != r3: 
            prob_c = 0.40 if r3 == 'B' else 0.60
        else:
            prob_c = 0.50

        return prob_a, prob_b, prob_c

    def calculate_final_decision(self, r1, r2, r3):
        p_a, p_b, p_c = self.get_strategy_probabilities(r1, r2, r3)
        
        # 動態權重分配
        w_a, w_b, w_c = 0.5, 0.3, 0.2
        
        final_b = (p_a * w_a) + (p_b * w_b) + (p_c * w_c)
        final_p = 1.0 - final_b

        return {
            "strategies": [p_a, p_b, p_c],
            "final_b": final_b,
            "final_p": final_p
        }

# --- 主程式介面 ---
if check_auth():
    # 側邊欄控制區
    with st.sidebar:
        st.success(f"👤 User: {st.session_state['user_id']}")
        
        if st.session_state["user_id"] == "admin":
             with st.expander("🛠️ 連結產生器"):
                new_u = st.text_input("輸入帳號產生連結")
                if new_u:
                    st.code(f"https://v7-public.streamlit.app/?uid={new_u}")

        if st.button("登出 (Logout)"):
            st.session_state["logged_in"] = False
            st.rerun()
        
        st.divider()
        st.header("🕹️ 路單輸入")
        rid = st.text_input("房號 (Room ID)", "VIP-01")
        
        # 中文選項介面
        options = ["莊", "閒", "和"]
        c1, c2, c3 = st.columns(3)
        with c1: r1_label = st.selectbox("前3", options, index=0)
        with c2: r2_label = st.selectbox("前2", options, index=1)
        with c3: r3_label = st.selectbox("前1", options, index=0)
        
        # 翻譯回 AI 代碼
        trans_map = {"莊": "B", "閒": "P", "和": "T"}
        r1 = trans_map[r1_label]
        r2 = trans_map[r2_label]
        r3 = trans_map[r3_label]
        
        run_btn = st.button("🚀 啟動 AI 運算", type="primary")

    # 右側主畫面
    st.title("🎰 V7 Intelligence 2.0")
    st.caption(f"監控目標: {rid} | 運算核心: Multi-Strategy Weighted Model | 狀態: 🟢 線上")
    st.divider()
    
    if run_btn:
        brain = BaccaratBrain()
        
        with st.spinner("AI 正在進行多策略加權分析..."):
            time.sleep(0.8) # 增加一點運算的科技感
            result = brain.calculate_final_decision(r1, r2, r3)
            
            final_b = result['final_b']
            final_p = result['final_p']
            
            # 判斷最終建議
            if final_b > final_p:
                rec_text = "莊 (BANKER)"
                color = "#FF4B4B" # 紅色
                win_rate = final_b
            else:
                rec_text = "閒 (PLAYER)"
                color = "#1E90FF" # 藍色
                win_rate = final_p
            
            # --- 1. 顯示大卡片結果 ---
            st.markdown(f"""
            <div style="text-align: center; border: 3px solid {color}; padding: 25px; border-radius: 15px; background-color: #f9f9f9;">
                <h3 style="margin:0; color: #555;">AI 綜合建議下注</h3>
                <h1 style="font-size: 70px; color: {color}; margin: 15px 0;">{rec_text}</h1>
                <h4 style="color: gray;">綜合勝率: {win_rate*100:.2f}%</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") # 空格

            # --- 2. 能量條視覺化 ---
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**莊家優勢 Banker** ({final_b*100:.1f}%)")
                st.progress(final_b)
            with c2:
                st.write(f"**閒家優勢 Player** ({final_p*100:.1f}%)")
                st.progress(final_p)

            st.divider()

            # --- 3. 策略圖表分析 (Matplotlib) ---
            st.subheader("🧠 策略權重分析 (Strategy Breakdown)")
            
            strat_probs = result['strategies']
            
            # 👇 修改重點：將圖表標籤改為英文，避免亂碼
            strat_names = ['Big Data (50%)', 'Trend (30%)', 'Reversal (20%)']
            
            # 繪製圖表
            fig, ax = plt.subplots(figsize=(10, 2.5))
            
            # 莊的機率條 (紅色)
            p1 = ax.barh(strat_names, [p * 100 for p in strat_probs], color='#FF4B4B', height=0.5, label='Banker')
            
            # 閒的機率條 (藍色，疊加在紅色後面)
            p2 = ax.barh(strat_names, [(1-p) * 100 for p in strat_probs], left=[p * 100 for p in strat_probs], color='#1E90FF', height=0.5, label='Player')
            
            # 美化圖表
            ax.set_xlim(0, 100)
            ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5) # 中線
            
            # 圖例改到右下角或上方，避免遮擋
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, frameon=False)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.get_xaxis().set_visible(False) # 隱藏 X 軸數字
            
            # 在條形圖上標示數字 (保持不變)
            for i, p in enumerate(strat_probs):
                if p > 0.2: ax.text(p*100/2, i, f"{p*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')
                if (1-p) > 0.2: ax.text(p*100 + (1-p)*100/2, i, f"{(1-p)*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')

            st.pyplot(fig)

            # 文字說明 (這裡依然保留中文，不受影響)
            with st.expander("查看詳細策略邏輯"):
                st.write(f"📊 **大數據 (Big Data)**: 檢索歷史庫，該路型 [{r1}-{r2}-{r3}] 莊贏率為 {strat_probs[0]*100:.1f}%")
                st.write(f"📈 **趨勢 (Trend)**: 分析連莊/連閒慣性，判定莊贏率為 {strat_probs[1]*100:.1f}%")
                st.write(f"🔄 **反轉 (Reversal)**: 分析單跳/變盤機率，判定莊贏率為 {strat_probs[2]*100:.1f}%")

    else:
        st.info("👈 請在左側輸入前三局結果，點擊按鈕開始運算。")
