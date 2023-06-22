import sys
import argparse
import logging
import pytube
import whisper
import demucs.separate
import shutil
import re
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from datetime import timedelta

parser = argparse.ArgumentParser(description='Convert a YouTube music video to Karaoke')

parser.add_argument("--video", help = "YouTube URL to convert")
parser.add_argument("--model", help = "Whisper model", default="large")

args = parser.parse_args()

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
  handlers=[
    logging.StreamHandler(sys.stdout)
  ]
)

if not args.video:
  logging.error("YouTube URL is needed")
  exit()

logging.info("Downloading Whisper model...")
model = whisper.load_model(args.model)

logging.info("Downloading the video from YouTube...")
youtubeVideo = pytube.YouTube(args.video)

logging.info("Extract the audio from the video...")
audio = youtubeVideo.streams.get_audio_only()
audio.download(filename='tmp.mp4')

logging.info("Remove vocals from audio...")
demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", "tmp.mp4"])

logging.info("Transcribe the vocals...")
result = model.transcribe('separated/mdx_extra/tmp/vocals.mp3', fp16=False)

logging.info("Generate lyrics subs...")
words_per_row = 5
for segment in result["segments"]:
  startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
  endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
  segmentId = segment['id']+1
  text = segment['text'].split()
  text = '\n'.join([' '.join(text[i:i+words_per_row]) for i in range(0,len(text),words_per_row)])
  segment = f"{segmentId}\n{startTime} --> {endTime}\n{text}\n\n"
  with open("subtitles.srt", 'a', encoding='utf-8') as srtFile:
    srtFile.write(segment)

logging.info("Generate video template...")
videoclip = VideoFileClip("template.mp4")
videoclip = videoclip.subclip(0, youtubeVideo.length)

audioclip = AudioFileClip('separated/mdx_extra/tmp/no_vocals.mp3')
videoclip = videoclip.set_audio(CompositeAudioClip([audioclip]))

logging.info("Add lyrics to video template...")
generator = lambda txt: TextClip(txt, font='Arial-Bold', fontsize=60, color='DeepPink')
subs = SubtitlesClip('subtitles.srt', generator)
subtitles = SubtitlesClip(subs, generator)

videoclip = CompositeVideoClip([videoclip, subtitles.set_pos(('center','center'))])

videoclip.write_videofile("output.mp4",
  codec='libx264',
  audio_codec='aac',
  temp_audiofile='temp-audio.m4a',
  remove_temp=True,
  fps=24
)

logging.info("Cleanup...")

os.remove('tmp.mp4')
os.remove('subtitles.srt')
shutil.rmtree('separated', ignore_errors=True)

logging.info("DONE!")
