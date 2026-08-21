import os
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """Download audio from a YouTube URL and convert it to WAV."""
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        # Use Android / iOS internal API clients instead of just the
        # web client. These generally don't require a PO token, which
        # is what causes "HTTP Error 403: Forbidden" on the web client
        # when no PO-token provider is configured.
        # YouTube has been rolling out a "SABR-only" streaming
        # experiment that strips download URLs from android/ios/web
        # clients unless a PO token is supplied. The "tv" client is
        # currently the most reliable fallback that still works
        # without one (falls back to itag 18 — 360p combined
        # audio+video — which is fine since we only need the audio).
        # See: https://github.com/yt-dlp/yt-dlp/issues/12482
        "extractor_args": {
            "youtube": {
                "player_client": ["tv", "web_safari", "android", "ios"],
                "player_skip": ["webpage", "configs"],
            },
        },

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    # Cookies are required once YouTube serves a bot-check ("Sign in to
    # confirm you're not a bot"), which happens often on cloud/datacenter
    # IPs like Streamlit Community Cloud, even when it doesn't happen
    # locally. app.py writes this file from st.secrets on startup.
    cookie_path = os.path.join(os.path.dirname(__file__), "..", "youtube_cookies.txt")
    if os.path.exists(cookie_path) and os.path.getsize(cookie_path) > 0:
        ydl_opts["cookiefile"] = cookie_path
        print(f"Using cookies from: {cookie_path}")
    else:
        print(
            "WARNING: No youtube_cookies.txt found. If you see a "
            "'Sign in to confirm you are not a bot' error, this is why — "
            "add fresh YouTube cookies to Streamlit Secrets."
        )

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # After the FFmpegExtractAudio postprocessor runs, the final
        # file is always <original_name_without_ext>.wav — computing
        # it this way is more reliable than string-replacing known
        # source extensions (which breaks on formats you didn't list).
        base, _ext = os.path.splitext(ydl.prepare_filename(info))
        filename = base + ".wav"

    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Expected WAV file not found after download: {filename}"
        )

    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """Split a WAV file into fixed-length chunks."""
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    """Process a YouTube URL or local file into audio chunks."""
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks