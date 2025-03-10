import re
import pysrt
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, vfx
from pydub import AudioSegment
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16\\magick.exe"})

def srt_time_to_seconds(time_obj):
    """Chuyển đổi datetime.time thành tổng số giây"""
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6

def adjust_srt_to_audio(srt_file, audio_file, output_srt):
    """Cập nhật thời gian SRT để khớp với audio"""
    subs = pysrt.open(srt_file, encoding="utf-8")
    audio = AudioSegment.from_file(audio_file)
    total_audio_duration = len(audio) / 1000  # Đổi ms -> giây

    last_srt_time = srt_time_to_seconds(subs[-1].end.to_time())
    factor = total_audio_duration / last_srt_time if last_srt_time > 0 else 1

    for sub in subs:
        new_start = srt_time_to_seconds(sub.start.to_time()) * factor
        new_end = srt_time_to_seconds(sub.end.to_time()) * factor
        sub.start = pysrt.SubRipTime(seconds=new_start)
        sub.end = pysrt.SubRipTime(seconds=new_end)

    subs.save(output_srt, encoding="utf-8")
    print(f"Adjusted SRT saved to {output_srt}")

def process_video(video_file, audio_file, srt_file, output_video):
    """Ghép audio và phụ đề vào video"""
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    w, h = video.size

    new_duration = audio.duration
    video = video.fx(vfx.speedx, video.duration / new_duration)
    video = video.set_audio(audio)

    black_bar = ColorClip(size=(w, 100), color=(0, 0, 0), duration=new_duration)
    black_bar = black_bar.set_position(("center", h - 100))

    subs = pysrt.open(srt_file, encoding="utf-8")
    sub_clips = []
    for sub in subs:
        start_time = srt_time_to_seconds(sub.start.to_time())
        duration = srt_time_to_seconds(sub.end.to_time()) - start_time

        txt_clip = TextClip(
            sub.text, fontsize=35, color='yellow', font="Liberation-Sans",
            size=(w - 100, None), method='caption', bg_color="black"
        ).set_start(start_time).set_duration(duration).set_position(('center', h - 120))

        sub_clips.append(txt_clip)

    if not sub_clips:
        print("Warning: No subtitles were added!")
    else:
        print(f"Generated {len(sub_clips)} subtitle clips.")

    final_clip = CompositeVideoClip([video, black_bar] + sub_clips)
    final_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    print(f"Final video saved as {output_video}")

# Chạy các hàm
adjust_srt_to_audio("translated_subtitles.srt", "gemini_response_stretched.mp3", "adjusted_subtitles.srt")
process_video("input.mp4", "gemini_response_stretched.mp3", "adjusted_subtitles.srt", "final_with_cleaned_sub.mp4")
