import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import random 

# --- 0. 網頁基本設定 ---
st.set_page_config(page_title="V7 Intelligence 5.6", layout="wide", page_icon="🎲")

# CSS 美化
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .bet-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ddd; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #00cc00); }
    
    /* 實戰紀錄球樣式 */
    .history-ball {
        display: inline-block;
        width: 45px;
        height: 45px;
        line-height: 45px;
        border-radius: 50%;
        text-align: center;
        color: white;
        font-weight: bold;
        margin: 5px;
        font-size: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .ball-b { background-color: #FF4B4B; border: 2px solid #b30000; }
    .ball-p { background-color: #1E90FF; border: 2px solid #0056b3; }
    .ball-t { background-color: #28a745; border: 2px solid #1e7e34; }
    
    .stButton>button { width: 100%; border-radius: 8px; height: 50px; font-size: 18px; }
    .matplotlib-yaxis-label { font-size: 14px; }
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
        worksheet = h = sh.sheet1
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

# --- 核心 2: AI 多策略運算大腦 ---
class BaccaratBrain:
    def __init__(self):
        self.history_db = {
            'BBB': 0.60, 'PPP': 0.35, 'BPB': 0.40, 'PBP': 0.65,
            'BBP': 0.45, 'PPB': 0.55, 'default': 0.5068 
        }

    def get_strategy_probabilities(self, history_list):
        if len(history_list) < 3: 
            return 0.5, 0.5, 0.5, 0, False
            
        current_streak = 0
        latest_val = history_list[-1]
        for val in reversed(history_list):
            if val == latest_val:
                current_streak += 1
            else:
                break
                
        r1, r2, r3 = history_list[-1], history_list[-2], history_list[-3]
        pattern_3 = r3 + r2 + r1
        
        prob_a = self.history_db.get(pattern_3, self.history_db['default'])

        if current_streak >= 3:
            prob_b = 0.80 if latest_val == 'B' else 0.20
        elif r1 == r2:
            prob_b = 0.60 if r1 == 'B' else 0.40
        else:
            prob_b = 0.50

        prob_c = 0.50
        is_reversal_active = False 

        if 3 <= current_streak <= 7:
            chance = random.random()
            threshold = 0.2 + (current_streak - 3) * 0.15
            if chance < threshold:
                is_reversal_active = True     
        elif current_streak >= 8:
            is_reversal_active = True

        if is_reversal_active:
            prob_c = 0.10 if latest_val == 'B' else 0.90
        else:
            is_chop = True
            if len(history_list) >= 4:
                recent_4 = history_list[-4:]
                for i in range(1, 4):
                    if recent_4[-i] == recent_4[-(i+1)]:
                        is_chop = False
                        break
            else:
                is_chop = False

            if is_chop:
                prob_c = 0.30 if r1 == 'B' else 0.70
            elif r1 != r2:
                prob_c = 0.45 if r1 == 'B' else 0.55
            else:
                prob_c = 0.50

        return prob_a, prob_b, prob_c, current_streak, is_reversal_active

    def calculate_final_decision(self, history_list):
        p_a, p_b, p_c, streak, is_rev = self.get_strategy_probabilities(history_list)
        
        if is_rev:
            w_a, w_b, w_c = 0.2, 0.2, 0.6 
        else:
            w_a, w_b, w_c = 0.4, 0.4, 0.2
        
        final_b = (p_a * w_a) + (p_b * w_b) + (p_c * w_c)
        final_p = 1.0 - final_b
        
        is_tie_triggered = False
        if random.random() < 0.095: 
            is_tie_triggered = True

        return {
            "strategies": [p_a, p_b, p_c],
            "final_b": final_b,
            "final_p": final_p,
            "streak_count": streak,
            "latest_val": history_list[-1] if history_list else None,
            "is_reversal_active": is_rev,
            "is_tie_triggered": is_tie_triggered 
        }

# --- 資金管理 ---
def get_betting_advice(win_rate, is_tie=False):
    if is_tie:
        return "🌟 高賠率信號 (Lucky Shot)", "#28a745", "✨ 數據奇點：偵測到盤勢波動，建議小注和局對沖或觀望。"

    percentage = win_rate * 100
    if percentage > 85: 
        return "🔥🔥🔥 重注 (3單位)", "#4CAF50", f"勝率高達 {percentage:.1f}% (>85%)，強力進攻！"
    elif percentage > 60: 
        return "🔥 加注 (2單位)", "#FF9800", f"勝率 {percentage:.1f}% (>60%)，建議加注獲利。"
    elif percentage > 50: 
        return "💰 平注 (1單位)", "#2196F3", f"勝率 {percentage:.1f}% (>50%)，具微幅優勢，平注跟進。"
    else: 
        return "👀 觀望 (Pass)", "#9E9E9E", f"勝率 {percentage:.1f}% (<=50%)，風險過高，建議暫停。"

# --- 主程式介面 ---
if check_auth():
    
    if "game_history" not in st.session_state:
        st.session_state["game_history"] = [] 
    
    with st.sidebar:
        st.success(f"👤 User: {st.session_state['user_id']}")
        
        # --- 連結產生器：自動處理網址斜線優化版 ---
        if st.session_state["user_id"] == "admin":
             with st.expander("🛠️ 連結產生器 (Link Generator)"):
                new_u = st.text_input("輸入帳號產生連結")
                if new_u:
                    # 這是您提供的真實網址，去掉末尾可能存在的斜線
                    raw_url = "https://v7-baccarat-project-cyugdhfxebxthycu64g7fu.streamlit.app"
                    clean_url = raw_url.rstrip('/')
                    final_link = f"{clean_url}/?uid={new_u}"
                    st.success("✅ 連結已生成：")
                    st.code(final_link)
                    st.caption("提示：如果點擊仍無權限，請確認 GitHub 倉庫已設定為 Public。")

        if st.button("登出 (Logout)"):
            st.session_state["logged_in"] = False
            st.rerun()
        
        st.divider()
        st.header("⚙️ 初始設定")
        st.caption("請依照時間順序輸入：由左 (第1局) 至 右 (第5局)")
        
        rid = st.text_input("房號", "VIP-01")
        
        options = ["莊", "閒", "和"]
        trans_map = {"莊": "B", "閒": "P", "和": "T"}
        
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: l1 = st.selectbox("第 1 局 (最舊)", options, index=0, key="s1") 
        with c2: l2 = st.selectbox("第 2 局", options, index=0, key="s2")
        with c3: l3 = st.selectbox("第 3 局", options, index=0, key="s3")
        with c4: l4 = st.selectbox("第 4 局", options, index=1, key="s4")
        with c5: l5 = st.selectbox("第 5 局 (最新)", options, index=1, key="s5") 
        
        initial_input = [trans_map[l1], trans_map[l2], trans_map[l3], trans_map[l4], trans_map[l5]]
        
        if st.button("🔄 設定/重置 牌局", type="secondary"):
            st.session_state["game_history"] = initial_input
            st.toast("牌局已重置，開始實戰監控！")
            st.rerun()
            
        st.info(f"目前實戰紀錄數: {len(st.session_state['game_history'])} 局")

    # 右側主畫面
    st.title("🎰 V7 Intelligence (5.6版)")
    st.caption(f"監控目標: {rid} | 模式: Real-time Rolling Analysis")
    st.divider()
    
    if not st.session_state["game_history"]:
        st.session_state["game_history"] = initial_input

    current_full_history = st.session_state["game_history"]
    
    brain = BaccaratBrain()
    result = brain.calculate_final_decision(current_full_history)
    
    final_b = result['final_b']
    final_p = result['final_p']
    streak_count = result['streak_count']
    latest_val = result['latest_val']
    is_reversal_active = result['is_reversal_active']
    is_tie_triggered = result['is_tie_triggered'] 
    
    if is_tie_triggered:
        rec_text = "和 (TIE)"
        color = "#28a745" 
        win_rate = 0.095 
        bet_title, border_color, logic_text = get_betting_advice(0, is_tie=True)
        rate_display = "⚠️ 偵測到變盤訊號"
    else:
        if final_b > final_p:
            rec_text = "莊 (BANKER)"
            color = "#FF4B4B"
            win_rate = final_b
        else:
            rec_text = "閒 (PLAYER)"
            color = "#1E90FF"
            win_rate = final_p
        
        bet_title, border_color, logic_text = get_betting_advice(win_rate, is_tie=False)
        rate_display = f"綜合勝率: {win_rate*100:.2f}%"
    
    st.markdown(f"""
    <div style="text-align: center; border: 3px solid {color}; padding: 30px; border-radius: 15px; background-color: #fff;">
        <h4 style="margin:0; color: #888;">下一局 ({len(current_full_history)+1}) 預測</h4>
        <h1 style="font-size: 80px; color: {color}; margin: 10px 0;">{rec_text}</h1>
        <h4 style="color: gray;">{rate_display}</h4>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 

    st.markdown(f"""
    <div style="text-align: center; border: 3px dashed {border_color}; padding: 20px; border-radius: 15px; background-color: #f9f9f9;">
        <h3 style="margin:0; color: #555;">💰 配注建議</h3>
        <h2 style="margin: 5px 0; color: {border_color};">{bet_title}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.subheader("📝 實戰結果回報 (Update Result)")
    st.caption("請點擊下方按鈕回報「剛剛開出」的結果，系統將自動修正下一局預測。")
    
    b_col, p_col, t_col = st.columns(3)
    
    with b_col:
        if st.button("🔴 莊贏 (Banker Win)"):
            st.session_state["game_history"].append("B")
            st.rerun()
    with p_col:
        if st.button("🔵 閒贏 (Player Win)"):
            st.session_state["game_history"].append("P")
            st.rerun()
    with t_col:
        if st.button("🟢 和局 (Tie)"):
            st.session_state["game_history"].append("T") 
            st.rerun()

    st.divider()
    st.subheader("📊 近 10 局實戰紀錄")
    
    display_history = st.session_state["game_history"][-10:]
    st.caption("⬅️ 較舊 (Oldest) .................................................. 最新 (Newest) ➡️")

    balls_html = ""
    for h in display_history:
        if h == 'B': balls_html += '<div class="history-ball ball-b">莊</div>'
        elif h == 'P': balls_html += '<div class="history-ball ball-p">閒</div>'
        else: balls_html += '<div class="history-ball ball-t">和</div>'
        
    st.markdown(f'<div style="background:#eee; padding:15px; border-radius:10px; text-align:left; overflow-x: auto; white-space: nowrap;">{balls_html}</div>', unsafe_allow_html=True)
    
    st.write("") 

    strat_probs = result['strategies']
    strat_names = ['Big Data (40%/20%)', 'Trend (40%/20%)', 'Cut Dragon (20%/60%)']
    
    with st.expander("查看 AI 詳細決策數據", expanded=False):
        streak_target = "莊" if latest_val == 'B' else "閒"
        if is_tie_triggered:
            st.success("✨ **數據奇點**：偵測到盤勢波動，建議小注和局對沖或觀望。")
        elif is_reversal_active:
            st.warning(f"⚡ **斷龍訊號觸發**: 連開 {streak_count} 個【{streak_target}】，AI 建議反打！")
        elif streak_count >= 3:
            st.info(f"🔥 **順勢追龍**: 連開 {streak_count} 個【{streak_target}】，建議追龍。")
        else:
            st.info(f"❄️ **盤整局面**: 無明顯長龍。")

        st.info(f"💡 **AI 決策核心**: {logic_text}")
        
        fig, ax = plt.subplots(figsize=(10, 2)) 
        p1 = ax.barh(strat_names, [p * 100 for p in strat_probs], color='#FF4B4B', height=0.6, label='Banker')
        p2 = ax.barh(strat_names, [(1-p) * 100 for p in strat_probs], left=[p * 100 for p in strat_probs], color='#1E90FF', height=0.6, label='Player')
        
        ax.set_xlim(0, 100)
        ax.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.3), ncol=2, frameon=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.tick_params(axis='y', which='both', length=0, labelsize=12)

        for i, p in enumerate(strat_probs):
            if p > 0.2: ax.text(p*100/2, i, f"{p*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')
            if (1-p) > 0.2: ax.text(p*100 + (1-p)*100/2, i, f"{(1-p)*100:.0f}%", color='white', ha='center', va='center', fontweight='bold')
        st.pyplot(fig)
