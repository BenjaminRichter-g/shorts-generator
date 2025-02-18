
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    # Pillow 10+ removed ANTIALIAS in favor of Resampling.LANCZOS.
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import (
    AudioFileClip, ImageClip, concatenate_videoclips,
    TextClip, CompositeVideoClip, VideoFileClip
)
from moviepy.video.tools.subtitles import SubtitlesClip
import json
import sys
from math import ceil
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "magick"})


class Video_Editor():

    def __init__(self):
        self.clips = []
        self.width = 1080
        self.height = 1920
    
    def add_captions(self, video, subs):
        """
        Adds subtitles (subs) on top of the given 'video'.
        Ensures we don't pass an empty string to TextClip.
        """
        def textclip_generator(txt):
            if not txt.strip():
                txt = " "
            return TextClip(txt, font='Arial', fontsize=70, color='white')
        
        subtitles = SubtitlesClip(subs, textclip_generator)
        result = CompositeVideoClip([video, subtitles.set_pos(('center','center'))])
        return result 

    def generate_video(self, path, story=None):
        clips = []
        durations = []

        image_files = [f"{path}/images/image_{i}.png" for i in range(0, 5)]
        audio_files = [f"{path}/audio/audio_{i}.mp3" for i in range(0, 5)]
    
        for img_path, aud_path in zip(image_files, audio_files):
            audio = AudioFileClip(aud_path)
            duration = audio.duration
            durations.append(duration)
        
            clip = ImageClip(img_path).set_duration(duration)
            clip = clip.set_audio(audio)
        
            clip = clip.resize(height=self.height)
        
            if clip.w > self.width:
                max_shift = clip.w - self.width
        
                def crop_func(get_frame, t):
                    frame = get_frame(t)
                    current_x = int(max_shift * t / duration)
                    return frame[0:self.height, current_x:current_x+self.width]
        
                clip = clip.fl(crop_func, apply_to=['mask'])
            else:
                clip = clip.on_color(size=(self.width, self.height),
                                     color=(0, 0, 0),
                                     pos='center')
            clips.append(clip)
        
        final_clip = concatenate_videoclips(clips)

        if story is not None:
            subtitles = self.prepare_subs(story['lines'], durations)
            final_clip = self.add_captions(final_clip, subtitles)
        
        final_clip.write_videofile(f"{path}/video.mp4", fps=24)


    def prepare_subs(self, lines, durations):
        """
        For each text line in 'lines', figure out how to split it into
        multiple subtitle segments (if needed) so each segment can show
        up to 2 lines of text, each line up to 30 characters, never cutting words.
        """
        subs = []
        for i, line in enumerate(lines):
            new_duration_start = sum(durations[:i])
            new_duration_end = sum(durations[:i+1])
            total_line_duration = new_duration_end - new_duration_start
            
            sub_parts = self.format_sub_per_line(
                line=line,
                char_per_lines=30,            # max 30 chars per single line
                max_lines_per_segment=2,      # up to 2 lines per on-screen subtitle
                start_time=new_duration_start,
                total_line_duration=total_line_duration
            )
            subs.extend(sub_parts)
        return subs


    def format_sub_per_line(self, line, char_per_lines, max_lines_per_segment, start_time, total_line_duration):
        """
        1) Split the text into "single lines" (each up to 'char_per_lines' chars).
        2) Bundle those lines in groups of 'max_lines_per_segment' (2 lines).
        3) Each group is shown for (total_line_duration / num_groups).
        """
        words = line.split()
        single_lines = []
        current_line = ""

        for word in words:
            if not current_line:
                current_line = word
            else:
                if len(current_line) + 1 + len(word) <= char_per_lines:
                    current_line += " " + word
                else:
                    single_lines.append(current_line)
                    current_line = word
        if current_line:
            single_lines.append(current_line)

        if not single_lines:
            single_lines = [" "]

        segments = []
        for i in range(0, len(single_lines), max_lines_per_segment):
            chunk_lines = single_lines[i:i+max_lines_per_segment]
            segment_text = "\n".join(chunk_lines)
            segments.append(segment_text)

        num_segments = len(segments)
        segment_duration = total_line_duration / max(num_segments, 1)

        subs = []
        current_start = start_time

        for text_chunk in segments:
            subs.append(((current_start, current_start + segment_duration), text_chunk))
            current_start += segment_duration

        return subs




