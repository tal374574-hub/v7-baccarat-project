import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt

# --- 0. 網頁基本設定 ---
st.set_page_config(page_title="V7 Intelligence 3.0", layout="wide", page_icon="🎲")

# CSS 美化 (加入配注卡片的樣式)
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .bet-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ddd; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #00cc00); }
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

# --- 核心 2: AI 多策略運算大腦 (升級支援 5 局) ---
class BaccaratBrain:
    def __init__(self):
        # 簡單的大數據庫 (針對前3局的特徵)
        self.history_db = {
            'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65,
            'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068 
        }

    def get_strategy_probabilities(self, history_list):
        # history_list = [前1, 前2, 前3, 前4, 前5]
        # 取出前 3 局用於大數據查表 (因為最接近的影響最大)
        r1, r2, r3 = history_list[0], history_list[1], history_list[2]
        pattern_3 = r1 + r2 + r3
        
        # 1. 大數據策略 (權重 40%)
        prob_a = self.history_db.get(pattern_3, self.history_db['default'])

        # 2. 趨勢策略 (權重 40%) - 升級：看 5 局長龍
        # 計算最近連續一樣的次數
        streak = 1
        current = history_list[0] # 前1
        for i in range(1, 5):
            if history_list[i] == current:
                streak += 1
            else:
                break
        
        # 如果長龍大於 3，強烈建議追龍
        if streak >= 3:
            prob_b = 0.75 if current == 'B' else 0.25
        elif r1 == r2: # 短龍 (連2)
            prob_b = 0.60 if r1 == 'B' else 0.40
        else:
            prob_b = 0.50

        # 3. 反轉策略 (權重 20%) - 升級：看 5 局單跳
        # 判斷是否為單跳局面 (BPBPB)
        is_chop = True
        for i in range(4):
            if history_list[i] == history_list[i+1]:
                is_chop = False
                break
        
        if is_chop:
            # 如果是單跳，下一把預測反轉 (例如前1是B，下把猜P)
            prob_c = 0.30 if r1 == 'B' else 0.70
        elif r1 != r2: # 短跳
            prob_c = 0.45 if r1 == 'B' else 0.55
        else:
            prob_c = 0.50

        return prob_a, prob_b, prob_c

    def calculate_final_decision(self, history_list):
        p_a, p_b, p_c = self.get_strategy_probabilities(history_list)
        
        # 動態權重分配
        w_a, w_b, w_c = 0.4, 0.4, 0.2
        
        final_b = (p_a * w_a) + (p_b * w_b) + (p_c * w_c)
        final_p = 1.0 - final_b

        return {
            "strategies": [p_a, p_b, p_c],
            "final_b": final_b,
            "final_p": final_p
        }

# --- 新增: 資金管理配注建議 ---
def get_betting_advice(win_rate):
    percentage = win_rate * 100
    if percentage >= 85:
        return "🔥🔥🔥 重注 (3單位)", "強力進攻信號，信心極高！"
    elif percentage >= 70:
        return "🔥 加注 (2單位)", "趨勢明顯，建議加碼。"
    elif percentage >= 60:
        return "💰 平注 (1單位)", "優勢微幅領先，穩健下注。"
    else:
        return "👀 觀望 (Pass)", "局勢不明朗，建議暫停一局。"

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
        
        # --- 修改：5個欄位，由左至右為 前1 -> 前5 ---
        c1, c2, c3, c4, c5 = st.columns(5)
        
        # 注意 index 設定：通常默認稍微交錯看起來比較像真實牌局
        with c1: l1 = st.selectbox("前1", options, index=0) # 最新
        with c2: l2 = st.selectbox("前2", options, index=1)
        with c3: l3 = st.selectbox("前3", options, index=0)
        with c4: l4 = st.selectbox("前4", options, index=0)
        with c5: l5 = st.selectbox("前5", options, index=1) # 最舊
        
        # 轉換為列表
        input_history = [trans_map[l1], trans_map[l2], trans_map[l3], trans_map[l4], trans_map[l5]]
        
        run_btn = st.button("🚀 啟動 AI 運算", type="primary")

    # 右側主畫面
    st.title("🎰 V7 Intelligence 3.0 (實戰版)")
    st.caption(f"監控目標: {rid} | 策略核心: 5-Round Trend Analysis | 狀態: 🟢 線上")
    st.divider()
    
    if run_btn:
        brain = BaccaratBrain()
        
        with st.spinner("正在分析 5 局趨勢與計算配注..."):
            time.sleep(0.5)
            result = brain.calculate_final_decision(input_history)
            
            final_b = result['final_b']
            final_p = result['final_p']
            
            # 判斷結果
            if final_b > final_p:
                rec_text = "莊 (BANKER)"
                color = "#FF4B4B" # 紅
                win_rate = final_b
            else:
                rec_text = "閒 (PLAYER)"
                color = "#1E90FF" # 藍
                win_rate = final_p
            
            # 取得配注建議
            bet_title, bet_desc = get_betting_advice(win_rate)
            
            # --- 顯示區塊：並排顯示「預測結果」與「配注建議」 ---
            col_res, col_bet = st.columns([1.5, 1])
            
            with col_res:
                st.markdown(f"""
                <div style="text-align: center; border: 3px solid {color}; padding: 20px; border-radius: 15px; background-color: #f9f9f9; height: 100%;">
                    <h3 style="margin:0; color: #555;">AI 預測方向</h3>
                    <h1 style="font-size: 60px; color: {color}; margin: 10px 0;">{rec_text}</h1>
                    <h4 style="color: gray;">勝率: {win_rate*100:.2f}%</h4>
                </div>
                """, unsafe_allow_html=True)
            
            with col_bet:
                # 根據配注強度改變框框顏色
                border_color = "#4CAF50" if win_rate > 0.7 else "#FFC107"
                if win_rate < 0.6: border_color = "#9E9E9E"
                
                st.markdown(f"""
                <div style="text-align: center; border: 3px solid {border_color}; padding: 20px; border-radius: 15px; background-color: #fff; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <h3 style="margin:0; color: #555;">💰 配注建議</h3>
                    <h2 style="margin: 10px 0; color: {border_color};">{bet_title}</h2>
                    <p style="color: gray; margin:0;">{bet_desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()

            # --- 圖表與詳細數據 ---
            st.subheader("🧠 策略權重分析")
            
            strat_probs = result['strategies']
            strat_names = ['Big Data (40%)', 'Trend (40%)', 'Reversal (20%)']
            
            fig, ax = plt.subplots(figsize=(10, 2))
            p1 = ax.barh(strat_names, [p * 100 for p in strat_probs], color='#FF4B4B', height=0.6, label='Banker')
            p2 = ax.barh(strat_names, [(1-p) * 100 for p in strat_probs], left=[p * 100 for p in strat_probs], color='#1E90FF', height=0.6, label='Player')
            
            ax.set_xlim(0, 100)
            ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=2, frameon=False)
            ax.axis('off') # 隱藏所有座標軸線，更乾淨
            
            # 標示數字
            for i, p in enumerate(strat_probs):
                if p > 0.2: ax.text(p*100/2, i, f"{p*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')
                if (1-p) > 0.2: ax.text(p*100 + (1-p)*100/2, i, f"{(1-p)*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')

            st.pyplot(fig)
            
            with st.expander("查看 5 局趨勢分析詳情"):
                st.write(f"**輸入路單**: {input_history} (左為最新)")
                st.write(f"**長龍分析**: 若前幾局重複出現，趨勢策略分數會提高。")
                st.write(f"**配注邏輯**: 勝率 > 70% 觸發加注信號，> 85% 觸發重注信號。")

    else:
        st.info("👈 請在左側輸入 5 局路單 (最新在左)，點擊按鈕開始運算。")
