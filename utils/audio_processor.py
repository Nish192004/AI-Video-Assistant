import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile

import streamlit as st
import yt_dlp
from pydub import AudioSegment


# ============================================================
# Configuration
# ============================================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ============================================================
# Deno Installation
# ============================================================

def ensure_deno():
    """
    Find Deno or install it locally.

    Streamlit Cloud may not provide Deno through apt,
    so this installs Deno into ~/.deno/bin when necessary.
    """

    # --------------------------------------------------------
    # Check whether Deno already exists
    # --------------------------------------------------------

    deno_path = shutil.which("deno")

    if deno_path:
        print(f"Deno found: {deno_path}")

        try:
            result = subprocess.run(
                [deno_path, "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            print(result.stdout.strip())

        except Exception as e:
            print(f"Deno version check failed: {e}")

        return deno_path

    # --------------------------------------------------------
    # Installation directory
    # --------------------------------------------------------

    home = os.path.expanduser("~")

    deno_home = os.path.join(
        home,
        ".deno"
    )

    deno_bin = os.path.join(
        deno_home,
        "bin"
    )

    deno_path = os.path.join(
        deno_bin,
        "deno"
    )

    os.makedirs(
        deno_bin,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Add Deno to PATH
    # --------------------------------------------------------

    current_path = os.environ.get(
        "PATH",
        ""
    )

    if deno_bin not in current_path.split(
        os.pathsep
    ):
        os.environ["PATH"] = (
            deno_bin
            + os.pathsep
            + current_path
        )

    # --------------------------------------------------------
    # Check again
    # --------------------------------------------------------

    deno_path_from_path = shutil.which(
        "deno"
    )

    if deno_path_from_path:
        print(
            f"Deno found after PATH update: "
            f"{deno_path_from_path}"
        )

        return deno_path_from_path

    # --------------------------------------------------------
    # Download Deno
    # --------------------------------------------------------

    print(
        "Deno not found."
    )

    print(
        "Installing Deno..."
    )

    deno_zip_url = (
        "https://github.com/denoland/deno/"
        "releases/latest/download/"
        "deno-x86_64-unknown-linux-gnu.zip"
    )

    zip_path = os.path.join(
        home,
        "deno.zip"
    )

    try:

        print(
            f"Downloading Deno from:\n"
            f"{deno_zip_url}"
        )

        urllib.request.urlretrieve(
            deno_zip_url,
            zip_path
        )

        print(
            "Deno archive downloaded."
        )

        # ----------------------------------------------------
        # Extract
        # ----------------------------------------------------

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_file:

            zip_file.extractall(
                deno_bin
            )

        # ----------------------------------------------------
        # Remove ZIP
        # ----------------------------------------------------

        try:
            os.remove(zip_path)
        except OSError:
            pass

        # ----------------------------------------------------
        # Make executable
        # ----------------------------------------------------

        if not os.path.exists(
            deno_path
        ):
            raise RuntimeError(
                "Deno executable was not found "
                "after extraction."
            )

        os.chmod(
            deno_path,
            0o755
        )

        # ----------------------------------------------------
        # Update PATH
        # ----------------------------------------------------

        os.environ["PATH"] = (
            deno_bin
            + os.pathsep
            + os.environ.get(
                "PATH",
                ""
            )
        )

        # ----------------------------------------------------
        # Verify
        # ----------------------------------------------------

        result = subprocess.run(
            [
                deno_path,
                "--version"
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Deno was installed but "
                "could not be executed.\n"
                f"{result.stderr}"
            )

        print(
            "Deno installed successfully."
        )

        print(
            result.stdout.strip()
        )

        return deno_path

    except Exception as e:

        print(
            f"Deno installation failed: {e}"
        )

        # Clean up failed download

        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except OSError:
            pass

        raise RuntimeError(
            "Could not install Deno. "
            f"Reason: {e}"
        ) from e


# ============================================================
# Initialize Deno
# ============================================================

DENO_PATH = ensure_deno()


# ============================================================
# FFmpeg Check
# ============================================================

def check_ffmpeg():
    """
    Check FFmpeg availability.
    """

    ffmpeg_path = shutil.which(
        "ffmpeg"
    )

    if not ffmpeg_path:
        raise RuntimeError(
            "FFmpeg is not installed "
            "or not available in PATH."
        )

    print(
        f"FFmpeg found: {ffmpeg_path}"
    )

    return ffmpeg_path


# ============================================================
# yt-dlp Check
# ============================================================

def check_ytdlp():
    """
    Print yt-dlp version.
    """

    try:

        version = (
            yt_dlp.version.__version__
        )

        print(
            f"yt-dlp version: {version}"
        )

        return version

    except Exception as e:

        print(
            f"Could not determine "
            f"yt-dlp version: {e}"
        )

        return None


# ============================================================
# YouTube Cookies
# ============================================================

def get_youtube_cookie_file():
    """
    Read YouTube cookies from Streamlit Secrets.

    Expected:

    [youtube]

    cookies = '''
    # Netscape HTTP Cookie File
    ...
    '''
    """

    try:

        cookies = (
            st.secrets[
                "youtube"
            ][
                "cookies"
            ]
        )

    except (
        KeyError,
        FileNotFoundError
    ):

        print(
            "YouTube cookies were not "
            "found in Streamlit Secrets."
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

            os.unlink(
                cookie_file.name
            )

        except OSError:
            pass

        raise


# ============================================================
# Download YouTube Audio
# ============================================================

def download_youtube_audio(
    url: str
) -> str:

    """
    Download YouTube audio and convert
    it to WAV.
    """

    print(
        "================================"
    )

    print(
        "Starting YouTube download..."
    )

    print(
        f"URL: {url}"
    )

    print(
        "================================"
    )

    # --------------------------------------------------------
    # Check dependencies
    # --------------------------------------------------------

    check_ytdlp()

    check_ffmpeg()

    print(
        f"Deno executable: {DENO_PATH}"
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(id)s.%(ext)s"
    )

    cookie_file = None

    try:

        # ----------------------------------------------------
        # Cookies
        # ----------------------------------------------------

        cookie_file = (
            get_youtube_cookie_file()
        )

        # ----------------------------------------------------
        # yt-dlp configuration
        # ----------------------------------------------------

        ydl_opts = {

            # Best audio
            "format": "bestaudio/best",

            # Output
            "outtmpl": output_path,

            # No playlists
            "noplaylist": True,

            # Logs
            "quiet": False,
            "no_warnings": False,

            # ------------------------------------------------
            # Deno
            # ------------------------------------------------

            "js_runtimes": {
                "deno": {
                    "path": DENO_PATH
                }
            },

            # ------------------------------------------------
            # EJS
            # ------------------------------------------------

            "remote_components": [
                "ejs:github"
            ],

            # ------------------------------------------------
            # Convert to WAV
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

            ydl_opts[
                "cookiefile"
            ] = cookie_file

        # ----------------------------------------------------
        # Download
        # ----------------------------------------------------

        with yt_dlp.YoutubeDL(
            ydl_opts
        ) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            original_path = (
                ydl.prepare_filename(
                    info
                )
            )

        # ----------------------------------------------------
        # Expected WAV
        # ----------------------------------------------------

        wav_path = (
            os.path.splitext(
                original_path
            )[0]
            + ".wav"
        )

        # ----------------------------------------------------
        # Verify
        # ----------------------------------------------------

        if not os.path.exists(
            wav_path
        ):

            # Sometimes yt-dlp may produce
            # a slightly different extension.
            # Search the downloads directory.

            video_id = info.get(
                "id"
            )

            possible_files = []

            if video_id:

                for filename in os.listdir(
                    DOWNLOAD_DIR
                ):

                    if video_id in filename:

                        possible_files.append(
                            os.path.join(
                                DOWNLOAD_DIR,
                                filename
                            )
                        )

            wav_files = [
                f
                for f in possible_files
                if f.lower().endswith(
                    ".wav"
                )
            ]

            if wav_files:

                wav_path = wav_files[0]

            else:

                raise FileNotFoundError(
                    "YouTube download completed "
                    "but WAV file was not found.\n"
                    f"Expected: {wav_path}"
                )

        print(
            "================================"
        )

        print(
            "YouTube download successful!"
        )

        print(
            f"WAV file: {wav_path}"
        )

        print(
            "================================"
        )

        return wav_path

    except Exception as e:

        print(
            "================================"
        )

        print(
            "YouTube download failed:"
        )

        print(
            str(e)
        )

        print(
            "================================"
        )

        raise

    finally:

        # ----------------------------------------------------
        # Delete temporary cookies
        # ----------------------------------------------------

        if cookie_file:

            try:

                os.unlink(
                    cookie_file
                )

                print(
                    "Temporary cookie file deleted."
                )

            except OSError:
                pass


# ============================================================
# Convert Local Audio / Video
# ============================================================

def convert_to_wav(
    input_path: str
) -> str:

    """
    Convert local audio/video to
    mono 16 kHz WAV.
    """

    output_path = (
        os.path.splitext(
            input_path
        )[0]
        + "_converted.wav"
    )

    print(
        "Converting local file to WAV..."
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

    print(
        f"Converted file: {output_path}"
    )

    return output_path


# ============================================================
# Audio Chunking
# ============================================================

def chunk_audio(
    wav_path: str,
    chunk_minutes: int = 10
) -> list:

    """
    Split WAV into chunks.
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
            chunk_ms
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
            format="wav"
        )

        chunks.append(
            chunk_path
        )

    print(
        f"Created {len(chunks)} chunk(s)."
    )

    return chunks


# ============================================================
# Main Input Processor
# ============================================================

def process_input(
    source: str
) -> list:

    """
    Process YouTube URL or local file,
    convert to WAV and split into chunks.
    """

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    if (
        source.startswith("http://")
        or source.startswith("https://")
    ):

        print(
            "Detected YouTube URL."
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
            "Detected local file."
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
        f"Audio ready - "
        f"{len(chunks)} chunk(s) created."
    )

    return chunks