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
# YouTube Cookies
# ============================================================

def get_youtube_cookie_file():
    """
    Read Netscape-format YouTube cookies from Streamlit Secrets
    and create a temporary cookie file.
    """

    try:
        cookies = st.secrets["youtube"]["cookies"]

    except (KeyError, FileNotFoundError):
        print("WARNING: YouTube cookies not found in Streamlit Secrets.")
        return None

    if not cookies or not cookies.strip():
        print("WARNING: YouTube cookies are empty.")
        return None

    # Detect placeholder cookies
    if (
        "YOUR_VALUE" in cookies
        or "YOUR_HSID_VALUE" in cookies
        or "\tEXPIRY\t" in cookies
    ):
        raise RuntimeError(
            "Invalid YouTube cookies detected. "
            "Export a fresh Netscape cookies.txt file "
            "and replace the Streamlit secret."
        )

    # Basic Netscape-format check
    if "# Netscape HTTP Cookie File" not in cookies:
        print(
            "WARNING: Cookie file does not contain the "
            "usual Netscape header."
        )

    cookie_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        encoding="utf-8",
    )

    try:
        cookie_file.write(
            cookies.strip() + "\n"
        )

        cookie_file.close()

        print("YouTube cookie file created.")

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
    """

    url = url.strip()

    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    valid_prefixes = (
        "https://www.youtube.com/",
        "https://youtube.com/",
        "https://youtu.be/",
    )

    if not url.startswith(valid_prefixes):
        raise ValueError(
            f"Invalid YouTube URL: {url}"
        )

    print("================================")
    print("Starting YouTube download...")
    print(f"URL: {url}")
    print("================================")

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s",
    )

    cookie_file = None

    try:

        # ----------------------------------------------------
        # Get cookies
        # ----------------------------------------------------

        cookie_file = get_youtube_cookie_file()

        # ----------------------------------------------------
        # yt-dlp configuration
        # ----------------------------------------------------
        #
        # IMPORTANT:
        #
        # Do NOT force:
        # tv
        # web_safari
        # android
        # ios
        #
        # Let the installed yt-dlp + bgutil provider
        # select the appropriate client.
        # ----------------------------------------------------

        ydl_opts = {

            # Best available audio
            "format": "bestaudio/best",

            # Output
            "outtmpl": output_path,

            # Never download playlists
            "noplaylist": True,

            # Logs
            "quiet": False,
            "no_warnings": False,

            # ------------------------------------------------
            # JavaScript runtime
            # ------------------------------------------------
            #
            # Deno is available in your deployment.
            #
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
            # Retry configuration
            # ------------------------------------------------

            "retries": 3,
            "fragment_retries": 3,

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

            ydl_opts["cookiefile"] = cookie_file

            print(
                "Using YouTube cookies."
            )

        else:

            print(
                "WARNING: No YouTube cookies found."
            )

        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        print(
            "Running yt-dlp..."
        )

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True,
            )

            original_path = (
                ydl.prepare_filename(
                    info
                )
            )

        # ----------------------------------------------------
        # Determine WAV path
        # ----------------------------------------------------

        base_path = os.path.splitext(
            original_path
        )[0]

        wav_path = (
            base_path + ".wav"
        )

        # ----------------------------------------------------
        # Check WAV
        # ----------------------------------------------------

        if not os.path.exists(
            wav_path
        ):

            raise FileNotFoundError(
                "YouTube audio downloaded, "
                "but WAV conversion failed.\n"
                f"Expected: {wav_path}"
            )

        print("================================")
        print("YouTube download successful!")
        print(f"WAV file: {wav_path}")
        print("================================")

        return wav_path

    except Exception as e:

        print("================================")
        print("YouTube download failed:")
        print(str(e))
        print("================================")

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
# Local Audio / Video → WAV
# ============================================================

def convert_to_wav(
    input_path: str,
) -> str:
    """
    Convert any local audio/video file to
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
# Audio Chunking
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10,
) -> list:
    """
    Split WAV audio into fixed-length chunks.
    """

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
            f"{wav_path}_chunk_{i}.wav"
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
    source: str,
) -> list:
    """
    Process either a YouTube URL or local file
    and return audio chunks.
    """

    source = source.strip()

    # --------------------------------------------------------
    # YouTube
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
    # Chunk
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