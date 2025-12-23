import streamlit as st
import pandas as pd
import time

# 設定網頁標題與圖示
st.set_page_config(page_title="V7 Intelligence", layout="wide", page_icon="🎲")

# --- 核心 1: 權限驗證系統 ---
def check_auth():
    # 初始化登入狀態
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = ""

    # 如果已經登入，直接放行
    if st.session_state["logged_in"]:
        return True

    # 1. 讀取 Google Sheet 會員名單 (雲端 CSV)
    try:
        # ⚠️⚠️⚠️ 請將下方引號內的網址，換成您自己的 Google Sheet CSV 網址 ⚠️⚠️⚠️
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS26fxX0d970pvnevaoY3MgEMla8mVkNP-IAGcJrLHHPo6q86T5mNajEpp8n-bbjcBNwd6S52kkIQi3/pub?gid=1478541708&single=true&output=csv"
        
        # 讀取數據
        df = pd.read_csv(sheet_url, dtype=str)
        
        # 檢查是否有 Account 欄位並轉為清單
        if 'Account' in df.columns:
            valid_users = df['Account'].dropna().str.strip().tolist()
        else:
            valid_users = []
    except:
        # 如果連線失敗 (例如網路問題)，暫時設為空清單
        st.error("系統連線中斷，無法讀取會員名單。")
        valid_users = []

    # 2. 自動登入邏輯 (檢查網址參數 ?uid=xxx)
    # 使用 st.query_params 獲取參數
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

    # 3. 手動登入介面 (如果沒有自動登入)
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
            # 從雲端設定讀取統一密碼 (如果沒設定預設為 0000)
            system_pass = st.secrets.get("system_password", "0000")
            
            if input_user in valid_users and input_pass == system_pass:
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = input_user
                st.rerun()
            else:
                st.error("❌ 帳號未授權或密碼錯誤")
    
    return False

# --- 核心 2: AI 運算大腦 ---
@st.cache_data
def load_brain():
    try:
        # 讀取本地生成的歷史數據
        return pd.read_csv('baccarat_history.csv')
    except:
        return pd.DataFrame()

def predict(r1, r2, r3, df):
    # 組合路數
    pat = r1 + r2 + r3
    # 在大數據中尋找匹配
    matches = df[df['Pattern_3'] == pat]
    
    # 計算基礎機率
    if len(matches) > 0:
        b_count = len(matches[matches['Next_Outcome'] == 'B'])
        total = len(matches)
        b_rate = b_count / total
    else:
        b_rate = 0.5068 # 預設機率

    # 策略加權邏輯
    # 追龍權重: 如果前兩顆一樣，且是莊，加分
    trend = 0.6 if r2==r3 and r3=='B' else 0.4
    # 單跳權重: 如果跳來跳去，且最後是閒，預測反轉(莊)
    rev = 0.6 if r1!=r2 and r2!=r3 and r3=='P' else 0.4
    
    # 綜合運算 (歷史50% + 趨勢30% + 反轉20%)
    final_b = (b_rate * 0.5) + (trend * 0.3) + (rev * 0.2)
    return final_b, 1-final_b, len(matches)

# --- 主程式介面 ---
if check_auth():
    # 登入後才會顯示以下內容
    with st.sidebar:
        st.success(f"👤 User: {st.session_state['user_id']}")
        
        # Admin 工具箱 (只有帳號是 admin 才看得到)
        if st.session_state["user_id"] == "admin":
             with st.expander("🛠️ 連結產生器"):
                new_u = st.text_input("輸入帳號產生連結")
                if new_u:
                    st.code(f"https://v7-project.streamlit.app/?uid={new_u}")

        if st.button("登出 (Logout)"):
            st.session_state["logged_in"] = False
            st.rerun()
        
        st.divider()
        st.header("🕹️ 路單輸入")
        rid = st.text_input("房號 (Room ID)", "VIP-01")
        
        c1, c2, c3 = st.columns(3)
        with c1: r1 = st.selectbox("前3", ["B", "P"], index=0)
        with c2: r2 = st.selectbox("前2", ["B", "P"], index=1)
        with c3: r3 = st.selectbox("前1", ["B", "P"], index=0)
        
        run_btn = st.button("開始預測 (Analyze)", type="primary")

    # 右側主畫面
    st.title("🎰 V7 AI 預測終端")
    st.caption(f"監控目標: {rid} | 系統狀態: 🟢 線上")
    st.divider()
    
    if run_btn:
        df = load_brain()
        with st.spinner("AI 正在計算機率模型..."):
            time.sleep(0.8) # 模擬運算感
            pb, pp, count = predict(r1, r2, r3, df)
            
            # 判斷結果
            if pb > pp:
                rec = "莊 (BANKER)"
                color = "red"
                win_rate = pb
            else:
                rec = "閒 (PLAYER)"
                color = "#1E90FF" # 亮藍色
                win_rate = pp
            
            # 顯示大卡片
            st.markdown(f"""
            <div style="text-align: center; border: 2px solid {color}; padding: 20px; border-radius: 10px;">
                <h3 style="margin:0">AI 建議下注</h3>
                <h1 style="font-size: 60px; color: {color}; margin: 10px 0;">{rec}</h1>
                <h4 style="color: gray;">預測勝率: {win_rate*100:.2f}%</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.progress(pb, text=f"莊贏機率: {pb*100:.1f}%")
            
            with st.expander("查看詳細數據"):
                st.write(f"歷史相似局數: {count} 局")
                st.write(f"當前組合: {r1}-{r2}-{r3}")
    else:
        st.info("👈 請在左側輸入路單數據並點擊開始預測")