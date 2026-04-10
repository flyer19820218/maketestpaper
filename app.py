import streamlit as st
import json
import os
from PIL import Image as PILImage

# 路徑設定
JSON_PATH = 'data/item_bank_page2.json'
FIGURE_BASE_PATH = 'assets/figures/'

def load_vault():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

st.title("🔬 理化 AI 學習診斷系統")

if os.path.exists(JSON_PATH):
    questions = load_vault()
    
    q_labels = [f"第 {q.get('question_number', i+1)} 題" for i, q in enumerate(questions)]
    selected_label = st.select_slider("選擇練習題目", options=q_labels)
    
    q_idx = q_labels.index(selected_label)
    q = questions[q_idx]
    
    st.divider()
    
    # 🖼️ 直接顯示整題的截圖
    img_filename = f"Q{q.get('question_number')}_full.png"
    full_img_path = os.path.join(FIGURE_BASE_PATH, img_filename)
    
    if os.path.exists(full_img_path):
        st.image(full_img_path, use_container_width=True)
    else:
        st.error(f"⚠️ 找不到題目截圖：{img_filename}")
    
    # ==========================================
    # 🔘 固定的 A, B, C, D 答題區塊
    # ==========================================
    st.write("---")
    ans = st.radio("請選擇答案：", options=["A", "B", "C", "D"], horizontal=True, key=f"q_{q_idx}")
    
    if st.button("送出答案並獲取 AI 診斷"):
        # 獲取正確答案並轉大寫確保比對正確
        correct_ans = str(q.get('answer', '')).strip().upper()
        
        if ans == correct_ans:
            st.success("✅ 太強了！答案正確。")
        else:
            st.error(f"❌ 差一點點！正確答案是：{correct_ans}")
            
        st.info(f"💡 知識點提醒：這題考的是「{q.get('knowledge_point', '未標註')}」")
else:
    st.warning("⚠️ 題庫載入中，請確認 GitHub 中的 JSON 檔案是否存在。")
