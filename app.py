import streamlit as st
import fitz
import PIL.Image
import google.generativeai as genai

def test_decoupling(pdf_file):
    # 1. 讀取第二頁並轉圖片
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc[1] # 指向第二頁
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = PIL.Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # 2. 設計「切割測試」指令
    test_prompt = """
    請分析這張理化考卷頁面，並執行以下任務：
    1. 找出所有包含『圖(一)』、『圖(二)』字樣的影像區塊。
    2. 回傳這些影像區塊在圖片中的歸一化座標 [ymin, xmin, ymax, xmax]。
    3. 提取對應的題幹文字。
    
    格式要求：
    Question_Number: [題號]
    Text: [題幹內容]
    Image_Box: [ymin, xmin, ymax, xmax]
    Figure_Label: [如圖一]
    """

    model = genai.GenerativeModel('gemini-3-flash')
    response = model.generate_content([test_prompt, img])
    
    return response.text, img

# Streamlit 測試介面
st.title("🛡️ 拆解壓力測試儀")
uploaded = st.file_uploader("上傳 114 會考 PDF", type="pdf")

if uploaded:
    if st.button("🔍 執行圖文對位測試"):
        result_text, page_img = test_decoupling(uploaded)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(page_img, caption="原始頁面掃描")
        with col2:
            st.markdown("### AI 拆解邏輯結果")
            st.text(result_text)
