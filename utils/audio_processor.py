import os
import yt_dlp
from pydub import AudioSegment


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio and convert it to WAV.

    Requirements:
        - yt-dlp[default]
        - FFmpeg
    """

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    ydl_opts = {
        # Download best available audio
        "format": "bestaudio/best",

        # Output filename
        "outtmpl": output_path,

        # Convert audio to WAV
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        # Don't use browser cookies
        "cookiefile": None,

        # Don't download playlists
        "noplaylist": True,

        # Keep Streamlit logs reasonably clean
        "quiet": True,
        "no_warnings": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # Download YouTube audio
            info = ydl.extract_info(
                url,
                download=True
            )

            # Get downloaded filename
            original_path = ydl.prepare_filename(info)

            # FFmpeg converts it to WAV
            wav_path = (
                os.path.splitext(original_path)[0]
                + ".wav"
            )

            if not os.path.exists(wav_path):
                raise FileNotFoundError(
                    f"WAV file was not created: {wav_path}"
                )

            return wav_path

    except Exception as e:
        print(
            f"YouTube download failed: {e}"
        )
        raise


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio/video file to mono 16 kHz WAV.
    """

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(
        input_path
    )

    # Convert to mono 16 kHz
    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(
        output_path,
        format="wav"
    )

    return output_path


def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    audio = AudioSegment.from_wav(
        wav_path
    )

    chunk_ms = (
        chunk_minutes * 60 * 1000
    )

    chunks = []

    for i, start in enumerate(
        range(0, len(audio), chunk_ms)
    ):

        chunk = audio[
            start:start + chunk_ms
        ]

        chunk_path = (
            f"{wav_path}_chunk_{i}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:

    if (
        source.startswith("http://")
        or source.startswith("https://")
    ):

        print(
            "Detected YouTube URL. "
            "Downloading audio..."
        )

        wav_path = download_youtube_audio(
            source
        )

    else:

        print(
            "Detected local file. "
            "Converting to WAV..."
        )

        wav_path = convert_to_wav(
            source
        )

    print("Chunking audio...")

    chunks = chunk_audio(
        wav_path
    )

    print(
        f"Audio ready — "
        f"{len(chunks)} chunk(s) created."
    )

    return chunks