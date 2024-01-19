# whisper
import whisper
import textwrap

import os
import glob
import re

import yt_dlp

# pid = os.getpid()
# print(pid)

text = ""
youtube_video_name = ""

# create temp directory
if not os.path.exists("temp"):
    os.makedirs("temp")

# create output directory
if not os.path.exists("output"):
    os.makedirs("output")

output_directory = "output"
temp_directory = "temp"

# find current directory and specify the removal of ".webm" files
main_path = os.getcwd()
webm_files = glob.glob(os.path.join(main_path, "*.webm"))
wav_files = glob.glob(os.path.join(main_path, temp_directory, "*.wav"))


# -= Calling the main audio transcription function
def transcribe_audio(file_path_mp3, youtube_video_name):
    model = whisper.load_model("base")
    result = model.transcribe(file_path_mp3)
    del model

    if isinstance(result, dict) and "text" in result:
        result = result["text"]
    else:
        result = str(result)

    # Reformatting the output text
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", result)
    paragraphs = []
    paragraph = []

    for sentence in sentences:
        paragraph.append(sentence)
        if len(paragraph) == 4:
            paragraphs.append(" ".join(paragraph))
            paragraph = []

    if paragraph:
        paragraphs.append(" ".join(paragraph))

    formatted = "\n\n".join(paragraphs)

    # Word-wrapping without modifying the existing newlines
    wrapped = "\n\n".join(
        ["  " + textwrap.fill(p, width=80) for p in formatted.split("\n\n")]
    )

    # Add an extra newline between paragraphs
    wrapped_with_extra_newline = "\n\n".join([wrapped, ""])

    # Sanitizing YouTube name output
    video_name = re.sub(r"[\W_]+", " ", youtube_video_name)

    # Establishing output directory and file name
    output_dir = r"output"
    file_name = f"{video_name}.txt"
    file_path = os.path.join(output_dir, file_name)

    # Writing output to file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(wrapped_with_extra_newline)


if __name__ == "__main__":
    youtube_url = input("Youtube video url:")

    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_url)

    youtube_video_name = info["title"]

    ydl_opts = {
        "format": "bestaudio",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "fragment_requests": 100,  # try increasing this
        "outtmpl": "temp/temp.%(ext)s",
        "output_namplate": "temp.%(ext)s",
        "cachedir": "temp",  # set cache dir to output dir
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    file_path_mp3 = os.path.join(temp_directory, "temp.wav")

    transcribe_audio(file_path_mp3, youtube_video_name)

    ### cleanup ###

    # removal of leftover .webm processing file
    # sometimes doesn't work
    if webm_files:
        for webm_file in webm_files:
            os.remove(webm_file)
    if wav_files:
        for wav_file in wav_files:
            os.remove(wav_file)
