import streamlit as st
import fitz  # PyMuPDF
import cv2
import numpy as np
import google.generativeai as genai
from PIL import Image
import json
import os
import shutil

# ================================
# 視覺規範與設備適配
# ================================
st.set_page_config(page_title="理化題庫解析 POC", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light; }
html, body, [class*="st-"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    font-family: 'HanziPen SC', sans-serif !important;
}
.stAlert p { color: #FF0000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("理化 AI 實驗室：混合解析架構 (測試前 2 頁)")

# ================================
# 安全性檢測與 API 設置
# ================================
api_key = st.text_input("輸入 Gemini API Key", type="password")
if not api_key:
    st.warning("請輸入 API Key 以啟動解析服務。")
    st.stop()

if api_key.startswith("AIza") and len(api_key) > 30 and "github" in os.getcwd().lower():
    st.markdown("<p style='color:red; font-weight:bold;'>[安全警報] 偵測到 API Key 暴露於代碼庫，請立即撤銷並更新金鑰！</p>", unsafe_allow_html=True)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# ================================
# 核心邏輯
# ================================
def convert_normalized_to_pixel(normalized_box, img_height):
    ymin, _, ymax, _ = normalized_box
    return int((ymin / 1000) * img_height), int((ymax / 1000) * img_height)

uploaded_file = st.file_uploader("上傳 PDF 題庫", type=["pdf"])

if uploaded_file and st.button("開始 POC 測試 (切割 2 頁)"):
    # 清理舊輸出
    if os.path.exists("output"):
        shutil.rmtree("output")
    os.makedirs("output/images", exist_ok=True)

    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    all_q_data = []
    q_counter = 1
    
    TEST_PAGE_LIMIT = 2

    with st.spinner("執行 AI 定位與實體切割..."):
        for page_idx, page in enumerate(doc):
            if page_idx >= TEST_PAGE_LIMIT:
                st.info(f"已達測試上限 ({TEST_PAGE_LIMIT} 頁)，停止處理後續頁面。")
                break
                
            st.write(f"### 處理第 {page_idx+1} 頁...")
            
            pix = page.get_pixmap(dpi=200)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
            
            img_height = img_array.shape[0]
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # 步驟一：AI 定位
            prompt_locate = """
            找出圖中所有題目「題號」位置（如: 1.、(二)、Q1）。忽略頁首尾。
            輸出 JSON 陣列：[{"q_num": "題號", "box_2d": [ymin, xmin, ymax, xmax]}]
            """
            y_cuts = [0]
            try:
                response_locate = model.generate_content([prompt_locate, pil_img])
                clean_json = response_locate.text.replace("```json", "").replace("```", "").strip()
                location_data = json.loads(clean_json)
                
                for item in location_data:
                    actual_ymin, _ = convert_normalized_to_pixel(item["box_2d"], img_height)
                    y_cuts.append(max(0, actual_ymin - 10))
            except Exception as e:
                st.error(f"第 {page_idx+1} 頁定位失敗: {e}")
                continue

            y_cuts.append(img_height)
            y_cuts = sorted(list(set(y_cuts)))

            # 步驟二：切割與解析
            with st.expander(f"第 {page_idx+1} 頁單題細節", expanded=True):
                for i in range(len(y_cuts)-1):
                    y1, y2 = y_cuts[i], y_cuts[i+1]
                    if y2 - y1 < 40: continue

                    chunk_cv2 = img_array[y1:y2, :]
                    img_path = f"output/images/q_{q_counter}.png"
                    cv2.imwrite(img_path, chunk_cv2)

                    chunk_rgb = cv2.cvtColor(chunk_cv2, cv2.COLOR_BGR2RGB)
                    chunk_pil = Image.fromarray(chunk_rgb)

                    prompt_parse = """
                    提取題目文字，精確還原理化公式與上下標。表格轉 Markdown。
                    輸出 JSON：{"text": "完整題目與公式", "options": ["A...", "B..."], "answer": ""}
                    """
                    try:
                        res_parse = model.generate_content([prompt_parse, chunk_pil])
                        clean_parse = res_parse.text.replace("```json", "").replace("```", "").strip()
                        q_text_data = json.loads(clean_parse)
                        
                        col1, col2 = st.columns([2, 3])
                        with col1: st.image(img_path, caption=f"題號 {q_counter}")
                        with col2: st.json(q_text_data)
                        
                        all_q_data.append({"id": q_counter, "image_path": img_path, "parsed_text": q_text_data})
                        q_counter += 1
                    except Exception as e:
                        st.warning(f"碎片 {q_counter} 解析失敗: {e}")

    if all_q_data:
        st.success("測試完成。")
        json_str = json.dumps(all_q_data, indent=2, ensure_ascii=False)
        with open("output/ai_bundle.json", "w", encoding="utf-8") as f:
            f.write(json_str)
            
        shutil.make_archive("output_poc", 'zip', "output")
        with open("output_poc.zip", "rb") as f:
            st.download_button("下載 POC 實驗包 (圖片+JSON)", f, file_name="output_poc.zip", mime="application/zip")
