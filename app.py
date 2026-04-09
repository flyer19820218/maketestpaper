import streamlit as st
import json
import os

# 定義檔案路徑，對應您的 GitHub 資料夾結構
JSON_PATH = 'data/item_bank_page2.json'
FIGURE_BASE_PATH = 'assets/figures/'

def load_vault():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

st.title("🔬 理化 AI 學習診斷系統")

# 檢查資料夾內的 JSON 是否存在
if os.path.exists(JSON_PATH):
    questions = load_vault()
    
    # 建立一個友善的題號清單
    q_labels = [f"第 {q['question_number']} 題" for q in questions]
    selected_label = st.select_slider("選擇練習題目", options=q_labels)
    
    # 找出對應的題目數據
    q_idx = q_labels.index(selected_label)
    q = questions[q_idx]
    
    st.divider()
    
    # 呈現題幹
    st.subheader(selected_label)
    st.write(q['question_stem'])
    
    # 🖼️ 自動尋找圖片邏輯
    # 根據您的截圖，檔名可能是 Q2_圖_一_.png [cite: 34, 38] 或 Q5_圖_二_.png [cite: 58, 66]
    # 我們遍歷該題目下所有的圖片座標 Key
    if q.get('image_coordinates'):
        for fig_key in q['image_coordinates'].keys():
            # 將 AI 產出的「圖(一)」轉換為您的檔案格式「圖_一_」
            safe_fig_name = fig_key.replace("(", "_").replace(")", "_")
            file_name = f"Q{q['question_number']}_{safe_fig_name}.png"
            full_img_path = os.path.join(FIGURE_BASE_PATH, file_name)
            
            if os.path.exists(full_img_path):
                st.image(full_img_path, caption=f"參考圖表：{fig_key}")
    
    # 呈現選項
    ans = st.radio("請選擇答案：", options=list(q['options'].values()), key=f"q_{q_idx}")
    
    if st.button("送出答案並獲取 AI 診斷"):
        correct_ans_text = q['options'][q['answer']]
        if ans == correct_ans_text:
            st.success("✅ 太強了！答案正確。")
        else:
            st.error(f"❌ 差一點點！正確答案是 {q['answer']} ({correct_ans_text})。")
            st.info(f"💡 知識點提醒：這題考的是「{q['knowledge_point']}」")
else:
    # 顯示目前搜尋的路徑方便除錯
    st.warning(f"⚠️ 找不到題庫檔案。請確認 GitHub 上的 {JSON_PATH} 是否存在。")
    st.write(f"目前工作目錄內容：{os.listdir('.')}")
