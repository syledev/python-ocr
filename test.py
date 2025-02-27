import os
import cv2
import ffmpeg
import pytesseract
from googletrans import Translator
from gtts import gTTS
import subprocess
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


def extract_frames(video_path, output_folder="frames", interval=1):
    """
    Cắt từng khung hình từ video (theo khoảng thời gian) để nhận diện phụ đề.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = 0
    saved_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % (fps * interval) == 0:
            frame_path = os.path.join(output_folder, f"frame_{saved_count}.png")
            cv2.imwrite(frame_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"✅ Đã trích xuất {saved_count} khung hình.")
    return output_folder




def ocr_multilang_subtitles(frame_folder, output_srt="separated_subs.srt", watermark_region=None):
    files = sorted(os.listdir(frame_folder))
    subtitles = []
    index = 1

    for i, file in enumerate(files):
        img_path = os.path.join(frame_folder, file)
        img = cv2.imread(img_path)

        # Nếu có vùng watermark, làm mờ nó
        if watermark_region:
            x, y, w, h = watermark_region
            img[y:y+h, x:x+w] = cv2.GaussianBlur(img[y:y+h, x:x+w], (15, 15), 0)

        data = pytesseract.image_to_data(img, lang="chi_sim+eng+jpn+kor", output_type=pytesseract.Output.DICT)

        # Chỉ giữ chữ ở phần dưới của ảnh
        h, w, _ = img.shape
        min_y_threshold = int(h * 1/2)

        extracted_text = []
        for j in range(len(data["text"])):
            if int(data["top"][j]) >= min_y_threshold and data["text"][j].strip():
                extracted_text.append(data["text"][j])

        text = " ".join(extracted_text).strip()

        if text:
            try:
                detected_lang = detect(text)
            except LangDetectException:
                detected_lang = "unknown"

            start_time = f"00:00:{i:02d},000"
            end_time = f"00:00:{i + 1:02d},000"

            subtitles.append(f"{index}\n{start_time} --> {end_time}\n[{detected_lang.upper()}] {text}\n\n")
            index += 1

    with open(output_srt, "w", encoding="utf-8") as f:
        f.writelines(subtitles)

    print(f"✅ Đã nhận diện phụ đề mà không lấy watermark và xuất ra file: {output_srt}")
    return output_srt


def translate_srt(input_srt="ocr_subtitles.srt", output_srt="translated.srt", dest_lang="vi"):
    """
    Dịch file SRT từ ngôn ngữ gốc sang ngôn ngữ đích.
    """
    translator = Translator()
    translated_lines = []
    with open(input_srt, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        if "-->" in line or line.strip().isdigit() or line.strip() == "":
            translated_lines.append(line)
        else:
            translated_text = translator.translate(line.strip(), dest=dest_lang).text
            translated_lines.append(translated_text + "\n")

    with open(output_srt, "w", encoding="utf-8") as file:
        file.writelines(translated_lines)

    print(f"✅ Phụ đề đã được dịch: {output_srt}")
    return output_srt


def text_to_speech_from_srt(srt_file, output_audio="output.mp3", lang="vi"):
    """
    Chuyển đổi nội dung SRT đã dịch thành giọng nói.
    """
    text = ""
    with open(srt_file, "r", encoding="utf-8") as file:
        for line in file:
            if "-->" not in line and not line.strip().isdigit() and line.strip():
                text += line.strip() + " "

    tts = gTTS(text, lang=lang)
    tts.save(output_audio)
    print(f"✅ Đã tạo file âm thanh từ phụ đề: {output_audio}")
    return output_audio


def add_translated_subtitles(video_path, srt_file, output_video="final_with_subs.mp4"):
    """
    Gắn phụ đề đã dịch vào video.
    """
    command = f'ffmpeg -i "{video_path}" -vf "subtitles={srt_file}" "{output_video}"'
    os.system(command)
    print(f"✅ Video đã có phụ đề dịch: {output_video}")


file_video = "input.mp4"

# 1. Cắt khung hình để nhận diện phụ đề
frame_folder = extract_frames(file_video)

# 2. Nhận diện phụ đề đa ngôn ngữ
ocr_srt = ocr_multilang_subtitles(frame_folder)  # Đã sửa lỗi

# 3. Dịch phụ đề
translated_srt = translate_srt(ocr_srt, "translated.srt", dest_lang="vi")

# 4. Chuyển phụ đề thành giọng nói
audio_output = text_to_speech_from_srt(translated_srt, "translated_audio.mp3")

# 5. Gắn phụ đề đã dịch vào video cuối cùng
add_translated_subtitles(file_video, translated_srt, "final_video.mp4")
