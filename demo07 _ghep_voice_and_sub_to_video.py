import re
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings

# Khai báo đường dẫn ImageMagick
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe"})

# Hàm chuyển SRT time -> giây
def srt_time_to_seconds(time_str):
    h, m, s, ms = re.split('[:|,]', time_str)
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

# Đọc file SRT
with open('translated_subtitles.srt', 'r', encoding='utf-8') as file:
    srt_content = file.read().strip()

blocks = re.split(r'\n\s*\n', srt_content)
subtitles = []
for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) >= 3:
        time_str = lines[1]
        text = "\n".join(lines[2:])
        start, end = time_str.split(' --> ')
        start_time = srt_time_to_seconds(start)
        end_time = srt_time_to_seconds(end)
        subtitles.append((start_time, end_time, text))

# Đọc video và audio
video = VideoFileClip("input.mp4")
audio = AudioFileClip("gemini_response_stretched.mp3")
video = video.set_audio(audio)

w, h = video.size

# Tạo thanh đen che sub cũ
black_bar = ColorClip(size=(w, 150), color=(0, 0, 0), duration=video.duration)
black_bar = black_bar.set_position(("center", h-150))

# Tạo sub mới
sub_clips = []
for start, end, text in subtitles:
    print(f"Sub: {text} từ {start}s đến {end}s")
    txt_clip = TextClip(
        text,
        fontsize=50,
        color='yellow',
        font="Arial",  # Thay bằng font có trong list nếu cần
        size=(w-40, None),
        method='caption'
    ).set_start(start).set_duration(end - start).set_position(('center', h - 90))

    sub_clips.append(txt_clip)

# Gộp video + black bar + sub
final_clip = CompositeVideoClip([video, black_bar] + sub_clips)

# Xuất video
final_clip.write_videofile("final_with_cleaned_sub.mp4", fps=24, codec="libx264", audio_codec="aac")

print("✅ Video xuất thành công!")
