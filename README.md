# yt2karaoke
Converts a YouTube music video to a Karaoke video


## Install dependencies

```Shell

brew install ImageMagick
brew install ffmpeg

pip3 install git+https://github.com/openai/whisper.git
pip3 install pytube
pip3 install moviepy

python3 -m pip install -U git+https://github.com/facebookresearch/demucs#egg=demucs

```

## Usage

```Shell
 yt2karaoke.py [-h] [--video VIDEO] [--model MODEL]
```

 ## Example

```Shell
 python3 yt2karaoke.py --video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
 ```
