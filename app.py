import streamlit as st
import json
import os

st.set_page_config(page_title="理化 AI 學習診斷系統", layout="centered")

# ================================
# 🎨 視覺美化：彩色滑桿與進度條
# ================================
st.markdown("""
<style>
/* 彩色滑桿軌道 */
div.stSlider > div[data-baseweb="slider"] > div > div {
    background: linear-gradient(90deg, #4CAF50, #2196F3, #FF9800) !important;
}
/* 滑桿圓鈕 */
div.stSlider > div[data-baseweb="slider"] > div > div > div {
    background-color: #FFFFFF !important;
    border: 2px solid #FF5722 !important;
}
/* 單選按鈕橫向 */
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
        # 強制數字排序：保證第 10 題在第 9 題後面
        return sorted(data, key=lambda x: int(x.get("q_num", 0)))

quiz_data = load_quiz_data()

if not quiz_data:
    st.warning("⚠️ 找不到題庫資料！請執行 Colab 兵工廠並推送到 GitHub。")
    st.stop()

# ================================
# 📊 進度與操作
# ================================
total_q = len(quiz_data)
st.write(f"📂 目前題庫共有：**{total_q}** 題")

# 彩色滑桿
current_idx = st.slider("切換題目", min_value=1, max_value=total_q, value=1) - 1

# 彩色進度條
progress_pct = (current_idx + 1) / total_q
st.progress(progress_pct, text=f"進度：{current_idx + 1} / {total_q}")

current_q = quiz_data[current_idx]
image_path = current_q.get("image", "")

st.markdown("---")

if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.error(f"圖片遺失：{image_path}")

st.markdown("---")
st.write("選擇答案：")
user_ans = st.radio("Options", options=["A", "B", "C", "D"], index=None, label_visibility="collapsed", horizontal=True)

if st.button("查看解析"):
    if not user_ans:
        st.warning("請先選一個答案")
    else:
        ans = current_q["analysis"].get("ans", "")
        if user_ans == ans:
            st.success(f"正確！答案是 {ans}")
        else:
            st.error(f"錯誤。正確答案是 {ans}")
        st.info(f"💡 考點：{current_q['analysis'].get('point', '')}")
        st.write(f"📝 解析：{current_q['analysis'].get('diag', '')}")
