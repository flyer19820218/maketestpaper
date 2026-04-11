import streamlit as st
import json
import os

st.set_page_config(page_title="理化 AI 學習診斷系統", layout="centered")

# ================================
# 🎨 視覺美化區：彩色滑桿與進度條
# ================================
st.markdown("""
<style>
:root { color-scheme: light; }
html, body, [class*="st-"] {
    background-color: #FAFAFA !important;
    color: #333333 !important;
    font-family: 'Helvetica Neue', Helvetica, sans-serif !important;
}
/* 美化單選按鈕排列 */
div.stRadio > div { flex-direction: row; gap: 20px; }

/* 🌈 彩色滑桿 (軌道加粗、變色) */
div.stSlider > div[data-baseweb="slider"] > div > div {
    background: linear-gradient(90deg, #4CAF50, #00BCD4) !important;
}
div.stSlider > div[data-baseweb="slider"] > div > div > div {
    background-color: #FF9800 !important; /* 滑動的圓球顏色 */
    border: 2px solid #FFF !important;
}
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
        # 強制數字排序，保證第 10 題排在第 9 題後面
        def sort_by_num(item):
            try:
                return int(item.get("q_num", 0))
            except ValueError:
                return 0
        return sorted(data, key=sort_by_num)

quiz_data = load_quiz_data()

if not quiz_data:
    st.warning("⚠️ 找不到題庫檔案！請確認 Colab 的兵工廠是否已成功將資料推送到 GitHub。")
    st.stop()

# ================================
# 🎛️ 操作區：彩色進度條與滑桿
# ================================
total_q = len(quiz_data)
st.write(f"📂 目前題庫共有：**{total_q}** 題")

# 滑桿選擇題號
current_idx = st.slider("拖曳滑桿選擇題目：", min_value=1, max_value=total_q, value=1) - 1

# 顯示彩色進度條
progress_pct = (current_idx + 1) / total_q
st.progress(progress_pct, text=f"完成進度：{current_idx + 1} / {total_q} 題")

current_q = quiz_data[current_idx]
image_path = current_q.get("image", "")

st.markdown("---")

# 顯示題目圖片
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)
else:
    st.error(f"找不到圖片檔案：{image_path}，請等待 GitHub 同步。")

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
