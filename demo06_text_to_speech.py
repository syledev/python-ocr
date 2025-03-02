import re
from gtts import gTTS
from datetime import datetime, timedelta
from pydub import AudioSegment

# Đọc file SRT
with open('translated_subtitles.srt', 'r', encoding='utf-8') as file:
    srt_content = file.read().strip()

# Tách từng block phụ đề
blocks = re.split(r'\n\s*\n', srt_content)

# Lấy nội dung hội thoại
dialogue_lines = []
timestamps = []

for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) >= 3:
        timestamps.append(lines[1])  # Dòng thời gian
        dialogue = "\n".join(lines[2:])
        dialogue_lines.append(dialogue)

# Ghép thành đoạn hội thoại
full_text = "\n".join(dialogue_lines).strip()

# Tạo giọng nói gốc
tts = gTTS(full_text, lang='vi')
tts.save("temp_audio.mp3")

# Tính tổng thời gian cần kéo
def srt_time_to_seconds(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S,%f")
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second, microseconds=time_obj.microsecond).total_seconds()

start_time = srt_time_to_seconds(timestamps[0].split(' --> ')[0])
end_time = srt_time_to_seconds(timestamps[-1].split(' --> ')[1])
total_duration = end_time - start_time

# Đọc file gốc để kéo dài (stretch)
original_audio = AudioSegment.from_mp3("temp_audio.mp3")

# Tính tốc độ mới (ratio)
original_duration = len(original_audio) / 1000  # pydub trả về ms, cần chuyển thành giây
stretch_ratio = total_duration / original_duration

# Kéo giãn (time stretch)
stretched_audio = original_audio.speedup(playback_speed=1/stretch_ratio)

# Xuất file cuối cùng
stretched_audio.export("gemini_response_stretched.mp3", format="mp3")

print(f"✅ Đã tạo file gemini_response_stretched.mp3 với độ dài chính xác: {total_duration:.2f} giây")
