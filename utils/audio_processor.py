import os
import tempfile

import streamlit as st
import yt_dlp
from pydub import AudioSegment


# ============================================================
# Configuration
# ============================================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ============================================================
# YouTube Cookies from Streamlit Secrets
# ============================================================

def get_youtube_cookie_file():
    """
    Read YouTube cookies from Streamlit Secrets.

    Expected secrets.toml:

    [youtube]
    cookies = '''
    # Netscape HTTP Cookie File
    ...
    '''
    """

    try:
        cookies = st.secrets["youtube"]["cookies"]

    except (KeyError, FileNotFoundError):
        return None

    if not cookies or not cookies.strip():
        return None

    cookie_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    )

    try:
        cookie_file.write(cookies)
        cookie_file.close()

        return cookie_file.name

    except Exception:
        try:
            cookie_file.close()
            os.unlink(cookie_file.name)
        except OSError:
            pass

        raise


# ============================================================
# YouTube Audio Downloader
# ============================================================

def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio and convert it to WAV.

    Requirements:
        yt-dlp[default]
        FFmpeg
        Deno

    Optional:
        YouTube cookies from Streamlit Secrets
    """

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    cookie_file = None

    try:

        # ----------------------------------------------------
        # Get cookies
        # ----------------------------------------------------

        cookie_file = get_youtube_cookie_file()

        # ----------------------------------------------------
        # yt-dlp options
        # ----------------------------------------------------

        ydl_opts = {

            # Best available audio
            "format": "bestaudio/best",

            # Output
            "outtmpl": output_path,

            # Don't download playlist
            "noplaylist": True,

            # Show logs
            "quiet": False,
            "no_warnings": False,

            # ------------------------------------------------
            # JavaScript runtime
            # ------------------------------------------------

            "js_runtimes": {
                "deno": {}
            },

            # ------------------------------------------------
            # EJS remote component
            # ------------------------------------------------

            "remote_components": [
                "ejs:github"
            ],

            # ------------------------------------------------
            # Audio conversion
            # ------------------------------------------------

            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }

        # ----------------------------------------------------
        # Cookies
        # ----------------------------------------------------

        if cookie_file:
            ydl_opts["cookiefile"] = cookie_file

        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        print(
            "Starting YouTube download..."
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            original_path = ydl.prepare_filename(
                info
            )

            # FFmpeg output
            wav_path = (
                os.path.splitext(original_path)[0]
                + ".wav"
            )

            if not os.path.exists(wav_path):

                raise FileNotFoundError(
                    "Audio downloaded but WAV "
                    "conversion failed."
                )

            print(
                f"YouTube audio saved: {wav_path}"
            )

            return wav_path

    except Exception as e:

        print(
            f"YouTube download failed: {e}"
        )

        raise

    finally:

        # Delete temporary cookie file
        if cookie_file:

            try:
                os.unlink(cookie_file)

            except OSError:
                pass


# ============================================================
# Local Audio / Video → WAV
# ============================================================

def convert_to_wav(input_path: str) -> str:

    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(
        input_path
    )

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


# ============================================================
# Audio Chunking
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    audio = AudioSegment.from_wav(
        wav_path
    )

    chunk_ms = (
        chunk_minutes
        * 60
        * 1000
    )

    chunks = []

    for i, start in enumerate(
        range(
            0,
            len(audio),
            chunk_ms
        )
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


# ============================================================
# Main Input Processor
# ============================================================

def process_input(source: str) -> list:

    # --------------------------------------------------------
    # YouTube URL
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Local file
    # --------------------------------------------------------

    else:

        print(
            "Detected local file. "
            "Converting to WAV..."
        )

        wav_path = convert_to_wav(
            source
        )

    # --------------------------------------------------------
    # Chunk audio
    # --------------------------------------------------------

    print(
        "Chunking audio..."
    )

    chunks = chunk_audio(
        wav_path
    )

    print(
        f"Audio ready — "
        f"{len(chunks)} chunk(s) created."
    )

    return chunks