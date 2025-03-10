import pysrt
import os
import ffmpeg
import re
import edge_tts
import asyncio
import tempfile
import shutil

def srt_time_to_milliseconds(srt_time):
    return (srt_time.hours * 3600 + srt_time.minutes * 60 + srt_time.seconds) * 1000 + srt_time.milliseconds

def normalize_text(text):
    """Chuẩn hóa text và xử lý ký tự đặc biệt."""
    text = text.strip()
    text = re.sub(r'([.,!?])([^\s])', r'\1 \2', text)
    return text

def detect_language(text):
    """Phát hiện ngôn ngữ dựa trên ký tự."""
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'  # Tiếng Trung
    return 'vi'      # Mặc định tiếng Việt

def calculate_rate(text, duration_ms):
    """Tính toán tốc độ đọc phù hợp và trả về dưới dạng chuỗi."""
    base_duration = len(text) * 100
    rate = (base_duration / duration_ms) * 100
    rate = max(50, min(rate, 200))
    return f"+{int(rate)}%"

async def text_to_speech(text, output_path, duration_ms, voice="vi-VN-NamMinhNeural"):
    try:
        text = normalize_text(text)
        rate = calculate_rate(text, duration_ms)
        
        if detect_language(text) == 'zh':
            voice = "zh-CN-XiaoxiaoNeural"
        
        print(f"🔹 Đang xử lý TTS: '{text[:50]}...', Voice: {voice}, Rate: {rate}")
        temp_audio = output_path + "_temp.mp3"
        
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(temp_audio)
        await asyncio.sleep(1)

        if not os.path.exists(temp_audio):
            raise Exception("⚠️ Không nhận được file audio. Kiểm tra tham số API.")
        
        os.rename(temp_audio, output_path)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi tạo audio: {str(e)}")
        return False

def merge_audio_files(audio_files, output_file, total_duration):
    with open("file_list.txt", "w", encoding="utf-8") as f:
        for file in audio_files:
            f.write(f"file '{file}'\n")
    
    ffmpeg.input("file_list.txt", format="concat", safe=0)\
        .output(output_file, c="copy")\
        .run(overwrite_output=True)
    os.remove("file_list.txt")

def get_total_video_duration(subs):
    return srt_time_to_milliseconds(subs[-1].end) / 1000

async def process_all(subs, temp_dir, voice):
    temp_files = []
    for sub in subs:
        start_ms = srt_time_to_milliseconds(sub.start)
        end_ms = srt_time_to_milliseconds(sub.end)
        duration = end_ms - start_ms
        temp_filename = os.path.join(temp_dir, f"temp_{start_ms}.mp3")
        success = await text_to_speech(sub.text, temp_filename, duration, voice)
        if success:
            temp_files.append(temp_filename)
    return temp_files

def process_srt_to_audio(srt_file, output_audio_file, voice="vi-VN-NamMinhNeural"):
    subs = pysrt.open(srt_file, encoding="utf-8")
    temp_dir = tempfile.mkdtemp()
    total_duration = get_total_video_duration(subs)
    temp_files = asyncio.run(process_all(subs, temp_dir, voice))
    
    if temp_files:
        print("🔄 Đang gộp các file âm thanh...")
        merge_audio_files(temp_files, output_audio_file, total_duration)

    for temp_file in temp_files:
        os.remove(temp_file)
    
    shutil.rmtree(temp_dir)
    
    print(f"✅ Đã tạo xong file {output_audio_file}!")

if __name__ == "__main__":
    voice_choice = input("Chọn giọng đọc (nam/nữ): ").strip().lower()
    voice = "vi-VN-NamMinhNeural" if voice_choice == "nam" else "vi-VN-HoaiMyNeural"
    process_srt_to_audio("translated_subtitles.srt", "final_audio.mp3", voice)
