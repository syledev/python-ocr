import cv2
from paddleocr import PaddleOCR
import sys

# Đảm bảo in UTF-8 khi chạy trên Windows
sys.stdout.reconfigure(encoding='utf-8')

# Đọc ảnh gốc
img = cv2.imread("img.png")

# --- Tiền xử lý ảnh (có thể bỏ nếu ảnh rõ sẵn) ---
# Chuyển ảnh sang grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Tăng contrast nhẹ (có thể bỏ nếu không cần)
gray = cv2.equalizeHist(gray)

# Không cắt hay binarize — PaddleOCR nhận ảnh gốc (hoặc gray)

# --- Khởi tạo PaddleOCR ---
ocr = PaddleOCR(lang='ch')  # 'ch' nhận cả giản thể + phồn thể

# --- OCR nhận diện phụ đề ---
result = ocr.ocr(gray)

# --- Ghi kết quả ra file SRT ---
with open("output.srt", "w", encoding="utf-8") as f:
    index = 1
    for line in result:
        for word in line:
            text = word[1][0]
            f.write(f"{index}\n")
            f.write(f"00:00:0{index} --> 00:00:0{index+1}\n")
            f.write(f"{text}\n\n")
            index += 1

print("✅ Đã xuất file output.srt")

# --- In ra màn hình xem luôn ---
print("\nNội dung nhận diện:")
for line in result:
    for word in line:
        print(word[1][0])
