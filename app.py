import streamlit as st
import fitz  # PyMuPDF
import PIL.Image
import json
import os
import google.generativeai as genai

# 設定儲存路徑
FIGURE_DIR = "assets/figures"
os.makedirs(FIGURE_DIR, exist_ok=True)

def process_exam_page(pdf_file, page_index):
    """
    處理指定頁數：將 PDF 轉圖片並交給 AI 拆解
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc[page_index]
    
    # 將 PDF 頁面轉為高解析度圖片 (DPI 300)
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    img_path = f"temp_page_{page_index}.png"
    pix.save(img_path)
    img = PIL.Image.open(img_path)

    # 準備 AI 指令 (針對理化圖形題優化)
    prompt = """
    你是一個專業的理化題庫數位化助手。請分析這張考卷圖片，並將其拆解為結構化的 JSON 格式。
    針對每一道題，你需要提取：
    1. 題號與完整題幹文字。
    2. 選項 (A, B, C, D)。
    3. 關聯圖形：如果題目提到「如圖(一)」，請說明該圖形在圖片中的位置區域 (x, y, w, h)。
    4. 知識點標籤：例如「浮力」、「電學」、「牛頓定律」。
    
    請務必保持 JSON 格式嚴謹。
    """

    # 呼叫 Gemini 3 Flash (多模態輸入)
    model = genai.GenerativeModel('gemini-3-flash')
    response = model.generate_content([prompt, img])
    
    return response.text

# --- Streamlit 介面層 ---
st.title("🧪 理化 AI 題庫自動化入庫系統")
uploaded_file = st.file_uploader("上傳會考或練習題 PDF", type="pdf")

if uploaded_file:
    page_num = st.number_input("欲處理的頁碼 (從 0 開始)", min_value=0, value=1)
    if st.button("🚀 開始 AI 圖文拆解"):
        with st.spinner("AI 正在掃描圖形並提取題目..."):
            result = process_exam_page(uploaded_file, page_num)
            st.code(result, language="json")
            st.success("拆解完成！請核對數據後存入倉庫。")
