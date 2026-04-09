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
    st.subheader(selected_label)
    st.write(q.get('question_stem', '題幹讀取失敗'))
    
    # ==========================================
    # 🖼️ 防黑圖機制：過濾 AI 裁切失敗的殘骸
    # ==========================================
    if q.get('image_coordinates'):
        for fig_key in q['image_coordinates'].keys():
            safe_fig_name = fig_key.replace("(", "_").replace(")", "_")
            file_name = f"Q{q.get('question_number')}_{safe_fig_name}.png"
            full_img_path = os.path.join(FIGURE_BASE_PATH, file_name)
            
            if os.path.exists(full_img_path):
                try:
                    with PILImage.open(full_img_path) as check_img:
                        # 只要圖片太小 (例如我們防呆的 10x10 黑塊)，就直接隱藏不顯示！
                        if check_img.width > 30 and check_img.height > 30:
                            st.image(full_img_path, caption=f"參考圖表：{fig_key}")
                        else:
                            st.info("⚠️ 提醒：本題附圖 AI 擷取失敗，已自動隱藏。")
                except Exception:
                    pass
    
    # ==========================================
    # 🛡️ 格式自動相容：不管 AI 給 List 還是 Dict 都能讀
    # ==========================================
    raw_options = q.get('options', [])
    correct_ans_raw = q.get('answer', '')
    
    # 如果 AI 給的是字典 (Dict)
    if isinstance(raw_options, dict):
        display_options = list(raw_options.values())
        correct_ans_text = raw_options.get(correct_ans_raw, str(correct_ans_raw))
    # 如果 AI 給的是列表 (List)
    elif isinstance(raw_options, list):
        display_options = raw_options
        # 嘗試把正確答案 A, B, C, D 轉成索引 0, 1, 2, 3 來對應文字
        if isinstance(correct_ans_raw, str) and correct_ans_raw.upper() in ['A', 'B', 'C', 'D']:
            idx = ord(correct_ans_raw.upper()) - 65
            correct_ans_text = display_options[idx] if idx < len(display_options) else correct_ans_raw
        else:
            correct_ans_text = str(correct_ans_raw)
    else:
        display_options = ["選項解析異常"]
        correct_ans_text = "無"

    # 呈現選項
    ans = st.radio("請選擇答案：", options=display_options, key=f"q_{q_idx}")
    
    if st.button("送出答案並獲取 AI 診斷"):
        if ans == correct_ans_text:
            st.success("✅ 太強了！答案正確。")
        else:
            st.error(f"❌ 差一點點！正確答案是：{correct_ans_text}")
            st.info(f"💡 知識點提醒：這題考的是「{q.get('knowledge_point', '未標註')}」")
else:
    st.warning("⚠️ 題庫載入中，請確認 GitHub 中的 JSON 檔案是否存在。")
