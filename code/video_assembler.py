from moviepy.editor import AudioFileClip, ImageClip
import numpy as np


# Import the audio(Insert to location of your audio instead of audioClip.mp3)
audio = AudioFileClip("data_output/packages/d8498acc-a632-4d1b-8938-2448fc4fd17c/audio/audio_0.mp3")
# Import the Image and set its duration same as the audio (Insert the location of your photo instead of photo.jpg)
clip = ImageClip("data_output/packages/d8498acc-a632-4d1b-8938-2448fc4fd17c/images/image_0.png").set_duration(audio.duration)
# Set the audio of the clip
clip = clip.set_audio(audio)
# Export the clip

clip.write_videofile("video.mp4", fps=24)









