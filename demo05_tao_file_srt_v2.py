import cv2
import numpy as np
from paddleocr import PaddleOCR
from moviepy.video.io.VideoFileClip import VideoFileClip
import difflib

# Khởi tạo OCR với ngôn ngữ Trung (ch)
ocr = PaddleOCR(lang='ch')

# Đường dẫn video
video_path = 'input.mp4'
clip = VideoFileClip(video_path)

# Thông số video
video_fps = clip.fps

# Ngưỡng cài đặt
SIMILARITY_THRESHOLD = 0.8    # Text giống nhau >80% thì coi là cùng nội dung
STABILIZATION_THRESHOLD = 0.5  # Giữ nguyên text ít nhất 0.5 giây mới ghi phụ đề mới
MIN_TEXT_LENGTH = 3            # Bỏ qua dòng quá ngắn (noise)

# Biến lưu phụ đề
subtitles = []

# Biến trạng thái
previous_text = ""
start_time = 0.0
last_change_time = 0.0

# Hàm tính độ giống nhau giữa 2 chuỗi
def text_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

# Hàm format timestamp kiểu SRT
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds * 1000) % 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# Duyệt từng frame của video (FPS gốc)
for frame_number, frame in enumerate(clip.iter_frames(fps=video_fps, dtype='uint8')):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Lấy vùng phụ đề (dưới màn hình)
    h, w = gray.shape
    bottom_half = gray[int(h * 3 / 4):, :]

    # OCR lấy text
    result = ocr.ocr(bottom_half)

    if not result or not isinstance(result, list) or len(result) == 0 or not result[0]:
        continue  # Bỏ qua nếu OCR không nhận diện được text nào

    # Ghép text từ kết quả OCR
    current_text = " ".join(
        [line[1][0] for line in result[0] if line and len(line) > 1 and line[1] and line[1][0].strip()])

    # Loại bỏ text quá ngắn (chống noise OCR)
    if len(current_text.strip()) < MIN_TEXT_LENGTH:
        continue

    # Tính timestamp hiện tại (s)
    current_time = frame_number / video_fps

    # Nếu text thay đổi
    if current_text != previous_text:
        similarity = text_similarity(current_text, previous_text)

        if similarity < SIMILARITY_THRESHOLD:
            # Text khác hẳn => ghi lại đoạn cũ (nếu đủ lâu)
            if previous_text and (current_time - last_change_time > STABILIZATION_THRESHOLD):
                subtitles.append((start_time, current_time, previous_text))

            # Reset sang đoạn mới
            start_time = current_time
            previous_text = current_text
            last_change_time = current_time
        # Nếu chỉ khác nhẹ thì bỏ qua (coi như noise nhỏ)
    # Nếu text giống nhau: không làm gì cả (đang trong cùng 1 đoạn phụ đề)

# Kết thúc: Ghi đoạn cuối cùng (nếu còn)
if previous_text:
    subtitles.append((start_time, clip.duration, previous_text))

# Ghi ra file SRT
with open('subtitles.srt', 'w', encoding='utf-8') as srt_file:
    for idx, (start, end, text) in enumerate(subtitles):
        srt_file.write(f"{idx+1}\n")
        srt_file.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
        srt_file.write(f"{text}\n\n")

print("Đã tạo subtitles.srt với timestamp chuẩn milliseconds và chống trùng lặp.")
