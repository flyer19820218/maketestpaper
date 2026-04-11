import streamlit as st
import json
import os

st.set_page_config(page_title="理化 AI 學習診斷系統", layout="centered")

st.markdown("""
<style>
div.stSlider > div[data-baseweb="slider"] > div > div { background: linear-gradient(90deg, #4CAF50, #2196F3, #FF9800) !important; }
div.stSlider > div[data-baseweb="slider"] > div > div > div { background-color: #FFFFFF !important; border: 2px solid #FF5722 !important; }
div.stRadio > div { flex-direction: row; gap: 20px; }
.q-title { text-align: center; color: #1565C0; font-weight: bold; font-size: 24px; margin-bottom: 15px; padding: 12px; background-color: #E3F2FD; border-left: 8px solid #2196F3; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 理化 AI 超級題庫")

@st.cache_data
def load_quiz_data():
    json_path = "data/item_bank.json" 
    if not os.path.exists(json_path): return None
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data

full_data = load_quiz_data()

if not full_data:
    st.warning("⚠️ 找不到題庫資料！請在 Colab 執行兵工廠上傳考卷。")
    st.stop()

# ================================
# 📂 考卷分類選擇器
# ================================
# 撈出所有不重複的考卷名稱
paper_names = list(set([q.get("paper", "未分類考卷") for q in full_data]))
paper_names.sort()

selected_paper = st.selectbox("📚 請選擇要練習的考卷：", paper_names)

# 過濾出該份考卷的題目，並依照題號排序
quiz_data = [q for q in full_data if q.get("paper", "未分類考卷") == selected_paper]
quiz_data = sorted(quiz_data, key=lambda x: int(x.get("q_num", 0)))

total_q = len(quiz_data)
st.write(f"📂 本卷共有：**{total_q}** 題")

if total_q > 0:
    current_idx = st.slider("切換題目", min_value=1, max_value=total_q, value=1) - 1
    st.progress((current_idx + 1) / total_q, text=f"進度：{current_idx + 1} / {total_q}")

    current_q = quiz_data[current_idx]
    q_num = current_q.get("q_num", current_idx + 1)
    image_path = current_q.get("image", "")

    st.markdown("---")
    st.markdown(f"<div class='q-title'>🎯 第 {q_num} 題</div>", unsafe_allow_html=True)

    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.error(f"圖片遺失：{image_path}")

    st.markdown("---")
    st.write("選擇答案：")
    user_ans = st.radio("Options", options=["A", "B", "C", "D"], index=None, label_visibility="collapsed", horizontal=True)

    if st.button("查看解析 / 顯示答案"):
        ans = current_q["analysis"].get("ans", "")
        if user_ans:
            if user_ans == ans:
                st.success(f"正確！答案是 {ans}")
            else:
                st.error(f"錯誤。正確答案是 {ans}")
        else:
            st.info(f"👉 本題正確答案預設測試為：{ans}")
            
        st.write(f"💡 **考點：** {current_q['analysis'].get('point', '')}")
        st.write(f"📝 **解析：** {current_q['analysis'].get('diag', '')}")
