import cv2
from paddleocr import PaddleOCR
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Đọc tất cả file có danh lower_frame_*.png trong thư mục frames_cut
frame_dir_cut = "output/frames_cut"
os.makedirs(frame_dir_cut, exist_ok=True)

# Lấy danh sách file hình ảnh và sắp xếp theo tên
filenames = sorted([f for f in os.listdir(frame_dir_cut) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
num_files = len(filenames)
print(f"Tìm thấy {num_files} file hình ảnh.")

# Nếu số file quá lớn, chỉ xử lý một mẫu (ví dụ: 100 file)
max_frames = 100
if num_files > max_frames:
    step = num_files // max_frames
    selected_files = [filenames[i] for i in range(0, num_files, step)]
    selected_files = selected_files[:max_frames]
else:
    selected_files = filenames

print(f"Đang xử lý {len(selected_files)} file hình ảnh được chọn:")

# Khởi tạo PaddleOCR một lần ngoài vòng lặp để tiết kiệm thời gian
ocr = PaddleOCR(lang='ch')  # 'ch' nhận cả giản thể + phồn thể

# Nếu cần xóa file SRT cũ, mở file ở chế độ write (w) một lần trước
srt_path = "output.srt"
with open(srt_path, "w", encoding="utf-8") as f:
    f.write("")  # Xóa nội dung cũ

# Duyệt qua từng file hình ảnh và xử lý
index = 1 
for filename in selected_files:
    image_path = os.path.join(frame_dir_cut, filename)
    print(f"Đang xử lý {filename}...")
    try:
        img = cv2.imread(image_path)
        # --- Tiền xử lý ảnh (chuyển sang grayscale và tăng tương phản)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # OCR nhận diện phụ đề từ ảnh
        result = ocr.ocr(gray)

        # Ghi kết quả ra file SRT ở chế độ append
        with open(srt_path, "a", encoding="utf-8") as f:
             # Bạn có thể điều chỉnh index nếu muốn tăng dần qua các file
            for line in result:
                for word in line:
                    text = word[1][0]
                    f.write(f"{index}\n")
                    f.write(f"00:00:0{index} --> 00:00:0{index+1}\n")
                    f.write(f"{text}\n\n")
                    index += 1

        print("Đã xuất nội dung từ file này vào output.srt")
        # --- In ra màn hình xem kết quả ---
        print("\nNội dung nhận diện:")
        for line in result:
            for word in line:
                print(word[1][0])

    except Exception as e:
        print(f"Không thể đọc file {filename}: {e}")
        continue
