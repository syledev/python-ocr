import re
from gtts import gTTS
from datetime import datetime, timedelta
from pydub import AudioSegment

# Đọc file SRT
with open('translated_subtitles.srt', 'r', encoding='utf-8') as file:
    srt_content = file.read().strip()

# Tách từng block phụ đề
blocks = re.split(r'\n\s*\n', srt_content)


def srt_time_to_seconds(time_str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S,%f")
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute,
                     seconds=time_obj.second, microseconds=time_obj.microsecond).total_seconds()


# Danh sách audio clips
audio_clips = []

total_duration = 0
for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) >= 3:
        time_range = lines[1]
        text = " ".join(lines[2:])
        start_time, end_time = time_range.split(' --> ')
        start_sec = srt_time_to_seconds(start_time)
        end_sec = srt_time_to_seconds(end_time)
        duration = end_sec - start_sec
        total_duration += duration

        # Tạo giọng nói nhanh hơn
        tts = gTTS(text, lang='vi')
        tts.save("temp_clip.mp3")
        audio = AudioSegment.from_mp3("temp_clip.mp3").speedup(playback_speed=1.35)  # Tăng tốc 1.3x

        # Nếu audio ngắn hơn khoảng thời gian sub, thêm khoảng lặng
        if len(audio) / 1000 < duration:
            silence = AudioSegment.silent(duration=(duration - len(audio) / 1000) * 1000)
            audio += silence

        audio_clips.append(audio)

# Ghép các đoạn lại
final_audio = sum(audio_clips)

# Xuất file âm thanh hoàn chỉnh
final_audio.export("gemini_response_stretched.mp3", format="mp3")
print("Đã tạo file gemini_response_stretched.mp3 với tốc độ đọc nhanh hơn và kéo dài đúng thời gian yêu cầu.")