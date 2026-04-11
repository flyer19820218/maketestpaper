import streamlit as st
import json
import os

# ================================
# 視覺規範與設備適配
# ================================
st.set_page_config(page_title="理化 AI 學習診斷系統", layout="centered")

st.markdown("""
<style>
:root { color-scheme: light; }
html, body, [class*="st-"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    font-family: 'Helvetica Neue', Helvetica, sans-serif !important;
}
/* 自訂按鈕與選項樣式 */
div.stRadio > div { flex-direction: row; gap: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 理化 AI 學習診斷系統")

# ================================
# 1. 讀取 Colab 處理好的題庫資料
# ================================
@st.cache_data
def load_quiz_data():
    json_path = "data/item_bank.json" # 假設您的 colab 將 json 存在 data 資料夾
    if not os.path.exists(json_path):
        return None
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

quiz_data = load_quiz_data()

if not quiz_data:
    st.warning("⚠️ 找不到題庫檔案 (data/item_bank.json)！請先在 Colab 執行切割與 AI 解析，並將結果推送到 GitHub。")
    st.stop()

# ================================
# 2. 測驗介面 UI (參考教官截圖設計)
# ================================
st.write("選擇練習題目")

# 使用 Slider 選擇題號
total_q = len(quiz_data)
current_idx = st.slider("選擇題目", min_value=1, max_value=total_q, value=1, label_visibility="collapsed") - 1

current_q = quiz_data[current_idx]
q_num = current_q.get("q_num", current_idx + 1)
image_path = current_q.get("image", "")

st.markdown("---")

# 顯示題目圖片
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.error(f"找不到圖片檔案：{image_path}，請確認圖片是否已正確上傳至 GitHub。")

st.markdown("---")
st.write("請選擇答案：")

# 選擇題 Radio Button
user_ans = st.radio("答案選項", options=["A", "B", "C", "D"], index=None, label_visibility="collapsed", horizontal=True)

# 送出與診斷按鈕
if st.button("送出答案並獲取 AI 診斷"):
    if not user_ans:
        st.warning("請先選擇一個答案！")
    else:
        correct_ans = current_q["analysis"].get("ans", "")
        
        if user_ans == correct_ans:
            st.success(f"🎉 答對了！正確答案就是 {correct_ans}")
        else:
            st.error(f"❌ 答錯了喔。正確答案是 {correct_ans}")
            
        # 顯示 AI 知識點與解析 (來自 Colab 預先生成的 JSON)
        st.info(f"💡 **考點：** {current_q['analysis'].get('point', '無紀錄')}")
        st.write(f"**📝 AI 診斷提示：** {current_q['analysis'].get('diag', '無紀錄')}")
