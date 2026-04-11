import streamlit as st
import json
import os

st.set_page_config(page_title="理化 AI 學習診斷系統", layout="centered")

st.markdown("""
<style>
:root { color-scheme: light; }
html, body, [class*="st-"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    font-family: 'Helvetica Neue', Helvetica, sans-serif !important;
}
div.stRadio > div { flex-direction: row; gap: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 理化 AI 學習診斷系統")

@st.cache_data
def load_quiz_data():
    json_path = "data/item_bank.json" 
    if not os.path.exists(json_path):
        return None
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
        # 強制將題號轉為數字排序
        def sort_by_num(item):
            try:
                return int(item.get("q_num", 0))
            except ValueError:
                return 0
        
        return sorted(data, key=sort_by_num)

quiz_data = load_quiz_data()

if not quiz_data:
    st.warning("⚠️ 找不到題庫檔案！請先在 Colab 執行後台程式碼，並等待資料推送至 GitHub。")
    st.stop()

# ================================
# 動態讀取總題數
# ================================
total_q = len(quiz_data)
st.write(f"📂 目前題庫共有：**{total_q}** 題")

current_idx = st.slider("選擇題目", min_value=1, max_value=total_q, value=1, label_visibility="collapsed") - 1

current_q = quiz_data[current_idx]
q_num = current_q.get("q_num", current_idx + 1)
image_path = current_q.get("image", "")

st.markdown("---")

if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.error(f"找不到圖片檔案：{image_path}，請確認 Colab 上傳狀態。")

st.markdown("---")
st.write("請選擇答案：")

user_ans = st.radio("答案選項", options=["A", "B", "C", "D"], index=None, label_visibility="collapsed", horizontal=True)

if st.button("送出答案並獲取 AI 診斷"):
    if not user_ans:
        st.warning("請先選擇一個答案！")
    else:
        correct_ans = current_q["analysis"].get("ans", "")
        
        if user_ans == correct_ans:
            st.success(f"🎉 答對了！正確答案就是 {correct_ans}")
        else:
            st.error(f"❌ 答錯了喔。正確答案是 {correct_ans}")
            
        st.info(f"💡 **考點：** {current_q['analysis'].get('point', '')}")
        st.write(f"**📝 AI 診斷提示：** {current_q['analysis'].get('diag', '')}")
