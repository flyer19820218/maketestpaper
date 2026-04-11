import streamlit as st
import fitz  # PyMuPDF
import cv2
import numpy as np
import google.generativeai as genai
from PIL import Image
import json
import os
import shutil
import re

# ================================
# 視覺規範與設備適配
# ================================
st.set_page_config(page_title="理化題庫 AI 診斷系統", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light; }
html, body, [class*="st-"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    font-family: 'Helvetica Neue', Helvetica, sans-serif !important;
}
/* 答案區紅色顯示 */
.stAlert p { color: #FF0000 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 理化 AI 實驗室：雷射物理切割版")

# ================================
# 安全性檢測與 API 設置
# ================================
api_key = st.text_input("輸入 Gemini API Key", type="password")
if not api_key:
    st.warning("請輸入 API Key 以啟動解析服務。")
    st.stop()

genai.configure(api_key=api_key)
# 建議使用最新版 Flash 以獲得最佳解析力
model = genai.GenerativeModel('gemini-2.0-flash')

# ================================
# 核心邏輯：雷射定位與切割
# ================================
uploaded_file = st.file_uploader("上傳 PDF 題庫", type=["pdf"])

if uploaded_file and st.button("🚀 開始精準解析 (測試前 2 頁)"):
    # 清理舊輸出
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output/images", exist_ok=True)

    # 讀取 PDF
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_q_data = []
    q_counter = 1
    TEST_PAGE_LIMIT = 2

    with st.spinner("雷射掃描中，正在執行物理精準切割..."):
        for page_idx in range(min(TEST_PAGE_LIMIT, len(doc))):
            page = doc[page_idx]
            st.write(f"### 📍 處理第 {page_idx+1} 頁...")
            
            # 1. 【雷射定位】從 PDF 底層抓取題號物理座標
            words = page.get_text("words")
            anchors = []
            for w in words:
                x0, y0, x1, y1, text, block_no, line_no, word_no = w
                # 尋找「數字 + 點」(如 3.)，且在左半邊 (避開干擾)
                if re.match(r"^\d+\.$", text.strip()) and x0 < page.rect.width * 0.3:
                    anchors.append({"num": text.strip("."), "y": y0})
            
            # 排序確保由上到下
            anchors = sorted(anchors, key=lambda x: x['y'])
            
            # 2. 【渲染底圖】
            dpi = 300 # 提高到 300 DPI 讓 AI 看得更清楚
            pix = page.get_pixmap(dpi=dpi)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4: img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
            
            h, w = img_array.shape[:2]
            scale = h / page.rect.height
            padding_up = 25 * scale # 往上退約一個字的高度
            
            # 3. 【無縫切割】
            with st.expander(f"第 {page_idx+1} 頁裁切細節", expanded=True):
                for i in range(len(anchors)):
                    curr = anchors[i]
                    # 起點：題號 Y 減去墊片
                    y_start = max(0, int(curr['y'] * scale - padding_up))
                    
                    # 終點：下一題的起點 (或是頁尾)
                    if i < len(anchors) - 1:
                        y_end = int(anchors[i+1]['y'] * scale - padding_up)
                    else:
                        y_end = int(h * 0.98)
                    
                    if y_end <= y_start: continue

                    # 裁切整欄寬度 (4%~96% 避開裝訂線)
                    chunk_cv2 = img_array[y_start:y_end, int(w*0.04):int(w*0.96)]
                    img_path = f"output/images/q_{curr['num']}.png"
                    cv2.imwrite(img_path, chunk_cv2)

                    # 4. 【AI 大腦分析】
                    chunk_pil = Image.fromarray(cv2.cvtColor(chunk_cv2, cv2.COLOR_BGR2RGB))
                    prompt_parse = """
                    你是專業理化老師。請閱讀此截圖並輸出 JSON 格式：
                    {
                      "ans": "正確答案字母",
                      "point": "此題考點/知識點",
                      "summary": "20字內題目簡述",
                      "diag": "給學生的診斷提示"
                    }
                    """
                    try:
                        response = model.generate_content([prompt_parse, chunk_pil])
                        clean_json = response.text.replace("```json", "").replace("```", "").strip()
                        analysis = json.loads(clean_json)
                        
                        col1, col2 = st.columns([1.5, 1])
                        with col1: st.image(img_path, caption=f"題號 {curr['num']}")
                        with col2: st.json(analysis)
                        
                        all_q_data.append({"q_num": curr['num'], "image": img_path, "analysis": analysis})
                    except:
                        st.warning(f"題號 {curr['num']} 解析失敗，可能是 AI 塞車。")

    if all_q_data:
        st.success("✅ 混合架構測試完成！")
        # 存成題庫 JSON
        with open("output/item_bank.json", "w", encoding="utf-8") as f:
            json.dump(all_q_data, f, ensure_ascii=False, indent=2)
        
        # 打包下載
        shutil.make_archive("quiz_poc", 'zip', "output")
        with open("quiz_poc.zip", "rb") as f:
            st.download_button("📥 下載精準解析包", f, file_name="quiz_poc.zip")
