AI-Flashcard (PDF → Flashcards + Tóm tắt)

Tạo flashcard và tóm tắt tự động từ file PDF bằng mô hình GPT, lưu trữ kết quả vào SQLite và xuất ra định dạng thuận tiện để học (Anki/CSV). Hỗ trợ giao diện web đơn giản bằng Streamlit.

🌐 Giới thiệu & Tham khảo
	•	Đây là dự án học tập, phát triển dựa trên nhu cầu tự động hóa việc ôn tập từ tài liệu PDF.
	•	Liên kết tham khảo: [Khoa Công nghệ thông tin – Đại học Đại Nam](https://dainam.edu.vn/vi/khoa/khoa-cong-nghe-thong-tin)

✨ Tính năng chính
	•	📄 Trích xuất văn bản từ PDF (PyPDF2)
	•	🧠 Sinh flashcard Q&A và tóm tắt theo từng mục/đoạn
	•	🗃️ Lưu kết quả vào SQLite để tra cứu, lọc, chỉnh sửa
	•	📤 Xuất CSV/TSV để nhập vào Anki hoặc các app flashcard khác
	•	🖥️ Giao diện Streamlit chạy local, thao tác kéo-thả PDF và xem kết quả ngay

⚙️ Yêu cầu hệ thống
	•	Python 3.10+
	•	API key hợp lệ (OpenAI API Key)

🔑 Cấu hình môi trường

Tạo file .env ở thư mục gốc (sao chép từ .env.example):
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
TEMPERATURE=0.5
MAX_TOKENS=1200
DB_PATH=db/flashcards.db
Cài đặt
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
Chạy ứng dụng:
Giao diện web (Streamlit):
streamlit run app/app.py
Chạy dạng CLI:
python scripts/pdf2anki_v2.py --input "data/inputs/sample.pdf" --export "data/exports/cards.csv" --summary
Xuất dữ liệu sang Anki
	•	Xuất file CSV/TSV với cột Front, Back, Tags
	•	Import vào Anki → chọn Type = Basic → map cột
 
