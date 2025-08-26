import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI
import sqlite3
import os

# ================== SETUP ==================
load_dotenv()  
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DB_PATH = "results.db"

# ================== CONFIG ==================
st.set_page_config(page_title="PDF Flashcards & Summary", layout="wide")

# ================== FUNCTIONS ==================
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def ask_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI hữu ích."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT,
            lang TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_result(mode, lang, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO results (mode, lang, content) VALUES (?, ?, ?)", (mode, lang, content))
    conn.commit()
    conn.close()

def load_results():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, mode, lang, content, created_at FROM results ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_result(rid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM results WHERE id = ?", (rid,))
    conn.commit()
    conn.close()

# ================== INIT ==================
init_db()

# ================== UI ==================
st.markdown("<h1 style='text-align:center;color:#7C3AED;'>PDF to Flashcards & Summary</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([2,2])

with col1:
    uploaded_file = st.file_uploader("Kéo thả file PDF hoặc click để chọn", type="pdf")
    mode = st.radio("Chế độ:", ["Flashcards", "Câu hỏi", "Tóm tắt"], horizontal=True)
    num_items = st.selectbox("Số lượng thẻ", [5,10,20,30,50], index=1)
    lang = st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English"])

with col2:
    pdf_text = ""
    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.text_area("Xem trước:", pdf_text[:2000], height=250)
    else:
        st.info("Chưa có nội dung. Vui lòng upload file PDF.")

# ================== XỬ LÝ ==================
if st.button("Tạo kết quả"):
    if not pdf_text:
        st.warning("⚠️ Vui lòng upload PDF trước.")
    else:
        with st.spinner("⏳ Đang xử lý..."):
            try:
                if mode == "Flashcards":
                    prompt = f"Tạo {num_items} flashcards bằng {lang} từ nội dung sau:\n\n{pdf_text}"
                    result = ask_openai(prompt)
                    save_result(mode, lang, result)

                    # Parse flashcards
                    cards = []
                    for block in result.split("\n\n"):
                        lines = block.strip().split("\n")
                        if len(lines) >= 2:
                            q = lines[0].replace("Câu hỏi:", "").strip()
                            a = lines[1].replace("Trả lời:", "").strip()
                            cards.append((q, a))

                    # Hiển thị flashcards (flip)
                    html_cards = """
<style>
.flip-card {
  background-color: transparent;
  width: 300px;
  height: 180px;
  perspective: 1000px;
  display: inline-block;
  margin: 10px;
}
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  border-radius: 12px;
}
.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
}
.flip-card-front {
  background-color: #F3E8FF;
  color: black;
  font-weight: bold;
}
.flip-card-back {
  background-color: #7C3AED;
  color: white;
  transform: rotateY(180deg);
}
</style>
"""
                    for q, a in cards:
                        html_cards += f"""
                        <div class="flip-card">
                          <div class="flip-card-inner">
                            <div class="flip-card-front">{q}</div>
                            <div class="flip-card-back">{a}</div>
                          </div>
                        </div>
                        """
                    st.markdown(html_cards, unsafe_allow_html=True)

                elif mode == "Câu hỏi":
                    prompt = f"Tạo {num_items} câu hỏi trắc nghiệm bằng {lang} từ nội dung sau.\n" \
                             f"Định dạng:\nCâu hỏi: ...\nA. ...\nB. ...\nC. ...\nD. ...\nĐáp án: X\n\n{pdf_text}"
                    result = ask_openai(prompt)
                    save_result(mode, lang, result)

                    st.markdown("### Câu hỏi trắc nghiệm")
                    questions = []
                    blocks = result.strip().split("\n\n")
                    for block in blocks:
                        lines = block.strip().split("\n")
                        if len(lines) >= 6:
                            q = lines[0].replace("Câu hỏi:", "").strip()
                            opts = [l.strip() for l in lines[1:5]]
                            ans = lines[5].replace("Đáp án:", "").strip().upper()
                            questions.append((q, opts, ans))

                    if "user_answers" not in st.session_state:
                        st.session_state.user_answers = {}
                    if "checked" not in st.session_state:
                        st.session_state.checked = False

                    for i,(q,opts,ans) in enumerate(questions):
                        st.write(f"**Câu {i+1}: {q}**")
                        st.session_state.user_answers[i] = st.radio("Chọn đáp án:", opts, key=f"q{i}")

                    if st.button("Chấm điểm"):
                        st.session_state.checked = True
                        correct = 0
                        for i,(_,_,ans) in enumerate(questions):
                            chosen = st.session_state.user_answers[i]
                            if chosen and chosen.startswith(ans):
                                correct += 1
                        st.success(f"🎯 Bạn trả lời đúng {correct}/{len(questions)} câu!")

                else:  # Tóm tắt
                    prompt = f"Tóm tắt nội dung bằng {lang}:\n\n{pdf_text}"
                    result = ask_openai(prompt)
                    save_result(mode, lang, result)
                    st.text_area("Tóm tắt:", result, height=300)

            except Exception as e:
                st.error(f"Lỗi: {e}")

# ================== LỊCH SỬ ==================
st.markdown("## 📜 Lịch sử kết quả")
rows = load_results()
for r in rows:
    st.write(f"[{r[0]}] ({r[1]} | {r[2]} | {r[4]})")
    st.text_area("", r[3], height=100)
    if st.button(f"Xóa {r[0]}", key=f"del{r[0]}"):
        delete_result(r[0])
        st.experimental_rerun()
