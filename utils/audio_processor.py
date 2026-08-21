import os
import shutil
import subprocess
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
# Check JavaScript Runtime
# ============================================================

def check_node():
    """
    Check whether Node.js is available on the machine.
    """

    node_path = shutil.which("node")

    if not node_path:
        print("WARNING: Node.js was not found.")
        return False

    try:
        result = subprocess.run(
            [node_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(
            f"Node.js detected: {result.stdout.strip()}"
        )

        return True

    except Exception as e:
        print(
            f"Node.js check failed: {e}"
        )
        return False


# ============================================================
# Get YouTube Cookies from Streamlit Secrets
# ============================================================

def get_youtube_cookie_file():
    """
    Read YouTube cookies from Streamlit Secrets
    and create a temporary Netscape cookie file.

    Streamlit secrets format:

    [youtube]

    cookies = '''
    # Netscape HTTP Cookie File
    ...
    '''
    """

    try:
        cookies = st.secrets["youtube"]["cookies"]

    except (KeyError, FileNotFoundError):
        print(
            "No YouTube cookies found in Streamlit Secrets."
        )
        return None

    if not cookies or not cookies.strip():
        print(
            "YouTube cookies are empty."
        )
        return None

    cookie_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    )

    try:

        cookie_file.write(
            cookies
        )

        cookie_file.close()

        print(
            "YouTube cookie file created."
        )

        return cookie_file.name

    except Exception:

        try:
            cookie_file.close()
            os.unlink(cookie_file.name)

        except OSError:
            pass

        raise


# ============================================================
# Download YouTube Audio
# ============================================================

def download_youtube_audio(url: str) -> str:
    """
    Download YouTube audio and convert it to WAV.

    Requires:

        yt-dlp
        FFmpeg
        Node.js

    Optional:

        YouTube cookies from Streamlit Secrets
    """

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s",
    )

    cookie_file = None

    try:

        # ----------------------------------------------------
        # Check Node.js
        # ----------------------------------------------------

        node_available = check_node()

        if not node_available:

            raise RuntimeError(
                "Node.js is not available on this "
                "Streamlit Cloud machine. "
                "Make sure packages.txt contains: nodejs"
            )

        # ----------------------------------------------------
        # Get cookies
        # ----------------------------------------------------

        cookie_file = (
            get_youtube_cookie_file()
        )

        # ----------------------------------------------------
        # yt-dlp configuration
        # ----------------------------------------------------

        ydl_opts = {

            # Best available audio
            "format": "bestaudio/best",

            # Output filename
            "outtmpl": output_path,

            # Don't download playlists
            "noplaylist": True,

            # Logging
            "quiet": False,
            "no_warnings": False,

            # ------------------------------------------------
            # JavaScript runtime
            # ------------------------------------------------
            #
            # Node.js comes from packages.txt
            #
            "js_runtimes": {
                "node": {}
            },

            # ------------------------------------------------
            # EJS remote component
            # ------------------------------------------------
            #
            # IMPORTANT:
            # This must be a LIST.
            #
            "remote_components": [
                "ejs:github"
            ],

            # ------------------------------------------------
            # Convert audio to WAV
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
        # Add cookies
        # ----------------------------------------------------

        if cookie_file:

            ydl_opts["cookiefile"] = (
                cookie_file
            )

        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        print(
            "Starting YouTube download..."
        )

        print(
            f"URL: {url}"
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True,
            )

            # ------------------------------------------------
            # Get original filename
            # ------------------------------------------------

            original_path = (
                ydl.prepare_filename(info)
            )

            # ------------------------------------------------
            # FFmpeg creates WAV
            # ------------------------------------------------

            wav_path = (
                os.path.splitext(
                    original_path
                )[0]
                + ".wav"
            )

            # ------------------------------------------------
            # Check WAV
            # ------------------------------------------------

            if not os.path.exists(
                wav_path
            ):

                raise FileNotFoundError(
                    "YouTube download completed, "
                    "but WAV file was not created.\n"
                    f"Expected: {wav_path}"
                )

            print(
                f"YouTube audio saved: "
                f"{wav_path}"
            )

            return wav_path

    except Exception as e:

        print(
            f"YouTube download failed: {e}"
        )

        raise

    finally:

        # ----------------------------------------------------
        # Delete temporary cookie file
        # ----------------------------------------------------

        if cookie_file:

            try:
                os.unlink(
                    cookie_file
                )

            except OSError:
                pass


# ============================================================
# Convert Local Audio / Video to WAV
# ============================================================

def convert_to_wav(
    input_path: str
) -> str:

    """
    Convert any audio/video file to
    mono 16 kHz WAV.
    """

    output_path = (
        os.path.splitext(
            input_path
        )[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(
        input_path
    )

    # Whisper-friendly format
    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
    )

    audio.export(
        output_path,
        format="wav",
    )

    return output_path


# ============================================================
# Split Audio into Chunks
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10,
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
            chunk_ms,
        )
    ):

        chunk = audio[
            start:start + chunk_ms
        ]

        chunk_path = (
            f"{wav_path}"
            f"_chunk_{i}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav",
        )

        chunks.append(
            chunk_path
        )

    return chunks


# ============================================================
# Main Input Processor
# ============================================================

def process_input(
    source: str
) -> list:

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

        wav_path = (
            download_youtube_audio(
                source
            )
        )

    # --------------------------------------------------------
    # Local file
    # --------------------------------------------------------

    else:

        print(
            "Detected local file. "
            "Converting to WAV..."
        )

        wav_path = (
            convert_to_wav(
                source
            )
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