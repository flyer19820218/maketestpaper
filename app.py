import streamlit as st
import json
import os

# 1. 載入我們從 Colab 產出的核武庫
def load_vault():
    with open('item_bank_page2.json', 'r', encoding='utf-8') as f:
        return json.load(f)

st.title("🔬 理化 AI 學習診斷系統")

if os.path.exists('item_bank_page2.json'):
    questions = load_vault()
    
    # 使用序號選擇題目
    q_idx = st.select_slider("選擇練習題號", options=range(len(questions)))
    q = questions[q_idx]
    
    st.divider()
    
    # 呈現題幹
    st.subheader(f"第 {q['question_number']} 題")
    st.write(q['question_stem'])
    
    # 呈現圖形（如果有圖的話）
    # 這裡對應我們在 Colab 切好的檔名格式 [cite: 34, 58]
    fig_name = f"Q{q['question_number']}_圖_一_" # 舉例，需與檔案對應
    if os.path.exists(f"{fig_name}.png"):
        st.image(f"{fig_name}.png", caption="實驗參考圖")
        
    # 呈現選項
    ans = st.radio("請選擇答案：", options=list(q['options'].values()), key=f"q_{q_idx}")
    
    if st.button("送出答案並獲取 AI 診斷"):
        if ans == q['options'][q['answer']]:
            st.success("✅ 太強了！答案正確。")
        else:
            st.error(f"❌ 差一點點！正確答案是 {q['answer']}。")
            st.info(f"💡 知識點提醒：這題考的是「{q['knowledge_point']}」")
else:
    st.warning("⚠️ 題庫尚未入庫，請先由 Colab 兵工廠進行處理。")
