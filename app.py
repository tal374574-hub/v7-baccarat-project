import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt

# --- 0. 網頁基本設定 ---
st.set_page_config(page_title="V7 Intelligence 3.1", layout="wide", page_icon="🎲")

# CSS 美化
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .bet-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ddd; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #00cc00); }
    /* 調整 Expander 樣式 */
    .streamlit-expanderHeader { font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心 1: 權限驗證系統 (保持不變) ---
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

# --- 核心 2: AI 多策略運算大腦 (5局版) ---
class BaccaratBrain:
    def __init__(self):
        self.history_db = {
            'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65,
            'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068 
        }

    def get_strategy_probabilities(self, history_list):
        r1, r2, r3 = history_list[0], history_list[1], history_list[2]
        pattern_3 = r1 + r2 + r3
        
        # 1. 大數據策略
        prob_a = self.history_db.get(pattern_3, self.history_db['default'])

        # 2. 趨勢策略 (看 5 局)
        streak = 1
        current = history_list[0]
        for i in range(1, 5):
            if history_list[i] == current:
                streak += 1
            else:
                break
        
        if streak >= 3:
            prob_b = 0.75 if current == 'B' else 0.25
        elif r1 == r2:
            prob_b = 0.60 if r1 == 'B' else 0.40
        else:
            prob_b = 0.50

        # 3. 反轉策略 (看 5 局)
        is_chop = True
        for i in range(4):
            if history_list[i] == history_list[i+1]:
                is_chop = False
                break
        
        if is_chop:
            prob_c = 0.30 if r1 == 'B' else 0.70
        elif r1 != r2:
            prob_c = 0.45 if r1 == 'B' else 0.55
        else:
            prob_c = 0.50

        return prob_a, prob_b, prob_c

    def calculate_final_decision(self, history_list):
        p_a, p_b, p_c = self.get_strategy_probabilities(history_list)
        
        w_a, w_b, w_c = 0.4, 0.4, 0.2
        
        final_b = (p_a * w_a) + (p_b * w_b) + (p_c * w_c)
        final_p = 1.0 - final_b

        return {
            "strategies": [p_a, p_b, p_c],
            "final_b": final_b,
            "final_p": final_p
        }

# --- 新增: 資金管理與動態建議生成 ---
def get_betting_advice(win_rate):
    percentage = win_rate * 100
    if percentage >= 85:
        return "🔥🔥🔥 重注 (3單位)", "#4CAF50", f"勝率高達 {percentage:.1f}%，多項指標共振，強力進攻！"
    elif percentage >= 70:
        return "🔥 加注 (2單位)", "#4CAF50", f"勝率達 {percentage:.1f}%，趨勢明顯，建議加碼獲利。"
    elif percentage >= 60:
        return "💰 平注 (1單位)", "#2196F3", f"勝率 {percentage:.1f}% 具微幅優勢，建議平注試探。"
    else:
        return "👀 觀望 (Pass)", "#9E9E9E", f"目前勝率僅 {percentage:.1f}% (接近 50/50)，局勢不明朗，建議暫停一局以保本。"

# --- 主程式介面 ---
if check_auth():
    with st.sidebar:
        st.success(f"👤 User: {st.session_state['user_id']}")
        
        if st.button("登出 (Logout)"):
            st.session_state["logged_in"] = False
            st.rerun()
        
        st.divider()
        st.header("🕹️ 路單輸入 (5局)")
        st.caption("順序：左(前1/最新) ➜ 右(前5/最舊)")
        
        rid = st.text_input("房號", "VIP-01")
        
        options = ["莊", "閒", "和"]
        trans_map = {"莊": "B", "閒": "P", "和": "T"}
        
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1: l1 = st.selectbox("前1", options, index=0) # 最新
        with c2: l2 = st.selectbox("前2", options, index=1)
        with c3: l3 = st.selectbox("前3", options, index=0)
        with c4: l4 = st.selectbox("前4", options, index=0)
        with c5: l5 = st.selectbox("前5", options, index=1) # 最舊
        
        input_history = [trans_map[l1], trans_map[l2], trans_map[l3], trans_map[l4], trans_map[l5]]
        
        run_btn = st.button("🚀 啟動 AI 運算", type="primary")

    # 右側主畫面
    st.title("🎰 V7 Intelligence 3.1 (優化實戰版)")
    st.caption(f"監控目標: {rid} | 狀態: 🟢 線上")
    st.divider()
    
    if run_btn:
        brain = BaccaratBrain()
        
        with st.spinner("AI 正在交叉比對 3 大策略模型..."):
            time.sleep(0.5)
            result = brain.calculate_final_decision(input_history)
            
            final_b = result['final_b']
            final_p = result['final_p']
            
            # 1. 判斷預測方向
            if final_b > final_p:
                rec_text = "莊 (BANKER)"
                color = "#FF4B4B" # 紅
                win_rate = final_b
            else:
                rec_text = "閒 (PLAYER)"
                color = "#1E90FF" # 藍
                win_rate = final_p
            
            # 2. 取得配注建議與動態邏輯
            bet_title, border_color, logic_text = get_betting_advice(win_rate)
            
            # --- 區塊 A: AI 預測大卡片 (置頂) ---
            st.markdown(f"""
            <div style="text-align: center; border: 3px solid {color}; padding: 30px; border-radius: 15px; background-color: #fff;">
                <h3 style="margin:0; color: #555;">AI 預測方向</h3>
                <h1 style="font-size: 80px; color: {color}; margin: 10px 0;">{rec_text}</h1>
                <h4 style="color: gray;">綜合勝率: {win_rate*100:.2f}%</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") # 空格

            # --- 區塊 B: 配注建議 (移到下方，與上方呼應) ---
            st.markdown(f"""
            <div style="text-align: center; border: 2px dashed {border_color}; padding: 15px; border-radius: 10px; background-color: #f9f9f9;">
                <h3 style="margin:0; color: #555;">💰 配注建議</h3>
                <h2 style="margin: 5px 0; color: {border_color};">{bet_title}</h2>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # --- 區塊 C: 策略圖表 (維持 2.0 風格) ---
            st.subheader("🧠 策略權重分析 (Strategy Breakdown)")
            
            strat_probs = result['strategies']
            # 使用英文標籤避免亂碼
            strat_names = ['Big Data (40%)', 'Trend (40%)', 'Reversal (20%)']
            
            fig, ax = plt.subplots(figsize=(10, 2))
            p1 = ax.barh(strat_names, [p * 100 for p in strat_probs], color='#FF4B4B', height=0.6, label='Banker')
            p2 = ax.barh(strat_names, [(1-p) * 100 for p in strat_probs], left=[p * 100 for p in strat_probs], color='#1E90FF', height=0.6, label='Player')
            
            ax.set_xlim(0, 100)
            ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=2, frameon=False)
            ax.axis('off') 
            
            for i, p in enumerate(strat_probs):
                if p > 0.2: ax.text(p*100/2, i, f"{p*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')
                if (1-p) > 0.2: ax.text(p*100 + (1-p)*100/2, i, f"{(1-p)*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')

            st.pyplot(fig)
            
            # --- 區塊 D: 智能分析報告 (Expander) ---
            # 這裡我們移除了「輸入路單」，並讓文字動態化
            with st.expander("📊 查看 AI 決策邏輯 (Why?)", expanded=True):
                st.info(f"💡 **AI 決策核心**: {logic_text}")
                
                st.markdown("---")
                st.write("**各策略詳細數據:**")
                st.write(f"- 📊 **大數據策略 (Big Data)**: 歷史庫檢索顯示，該路型莊贏率為 **{strat_probs[0]*100:.1f}%**")
                st.write(f"- 📈 **趨勢策略 (Trend)**: 根據 5 局長龍慣性分析，莊贏率為 **{strat_probs[1]*100:.1f}%**")
                st.write(f"- 🔄 **反轉策略 (Reversal)**: 根據單跳變盤機率分析，莊贏率為 **{strat_probs[2]*100:.1f}%**")

    else:
        st.info("👈 請在左側輸入路單，點擊按鈕開始運算。")
