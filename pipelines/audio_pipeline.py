#!/usr/bin/env python3
"""
Audio Pipeline Module - Extracted from audio-md_latest.py
Handles YouTube audio download and OpenAI Whisper transcription.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

from pydub import AudioSegment
from pydub.utils import which
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

@dataclass
class AudioConfig:
    url: str
    cookies: Optional[Path]
    chunk_ms: int
    outdir: Path
    use_cli: bool
    do_ollama: bool
    ollama_model: str = "llama3.2"
    whisper_model: str = "whisper-1"

class AudioPipeline:
    def __init__(self, config: AudioConfig):
        self.config = config
        self.session_dir = None
    
    def process(self) -> Tuple[Path, Path]:
        """Main processing method that returns transcript paths (md, txt)"""
        self.ensure_ffmpeg()
        
        # Create session directory
        self.session_dir = self.now_ts_dir(self.config.outdir)
        print(f"[INFO] Session directory: {self.session_dir}")
        
        # 1) Download audio
        mp3_path = self.download_yt_audio_mp3()
        
        # 2) Transcribe → .md and .txt
        transcript_md, transcript_txt = self.chunk_and_transcribe_whisper(mp3_path)
        
        # 3) Optional structuring with Ollama
        if self.config.do_ollama:
            self.structure_transcript_with_ollama(transcript_md)
        
        return transcript_md, transcript_txt
    
    def ensure_ffmpeg(self) -> None:
        ffmpeg = which("ffmpeg")
        if ffmpeg is None:
            env_ffmpeg = os.getenv("FFMPEG_BINARY")
            if env_ffmpeg and Path(env_ffmpeg).exists():
                AudioSegment.converter = env_ffmpeg
                return
            raise RuntimeError(
                "ffmpeg not found. Install ffmpeg and ensure it's in PATH, or set FFMPEG_BINARY to its path.\n"
                "Windows (choco):  choco install ffmpeg\n"
                "Windows (scoop):  scoop install ffmpeg\n"
                "Ubuntu:           sudo apt-get update && sudo apt-get install -y ffmpeg\n"
                "macOS (brew):     brew install ffmpeg"
            )
    
    @staticmethod
    def have_ssl() -> bool:
        try:
            import ssl  # noqa: F401
            return True
        except Exception:
            return False
    
    def require_openai_key(self) -> str:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not set in environment.")
        return key
    
    @staticmethod
    def ms_to_hms(ms: int) -> str:
        s = ms // 1000
        h = s // 3600
        m = (s % 3600) // 60
        s = s % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    @staticmethod
    def now_ts_dir(base: Path) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = base / ts
        out.mkdir(parents=True, exist_ok=True)
        return out
    
    def resolve_default_cookies(self, cookies_cli: Optional[str]) -> Optional[Path]:
        if cookies_cli:
            p = Path(cookies_cli).expanduser().resolve()
            if p.exists():
                return p
            print(f"[WARN] --cookies provided but not found: {p}")
        
        # Enhanced cookie search: try multiple common names and locations
        cookie_names = [
            "yt_cookies.txt",
            "youtube_cookies.txt", 
            "www.youtube.com_cookies.txt"
        ]
        
        search_locations = [
            Path(__file__).resolve().parent.parent,  # youtube-course-builder directory
            Path(__file__).resolve().parent,         # pipelines directory
            Path.cwd(),                              # current working directory
        ]
        
        for location in search_locations:
            for cookie_name in cookie_names:
                candidate = location / cookie_name
                if candidate.exists():
                    print(f"[INFO] Found cookies file: {candidate}")
                    return candidate
        
        print("[INFO] No cookies file found, will try browser cookies as fallback")
        return None
    
    def find_yt_dlp_binary(self) -> Optional[str]:
        """Look for yt-dlp binary in various locations"""
        local_names = ["yt-dlp", "yt-dlp.exe"]
        here = Path(__file__).resolve().parent
        for name in local_names:
            cand = here / name
            if cand.exists():
                return str(cand)
        for name in local_names:
            cand = Path.cwd() / name
            if cand.exists():
                return str(cand)
        # Then PATH
        for name in local_names:
            p = shutil.which(name)
            if p:
                return p
        return None
    
    def download_yt_audio_mp3(self) -> Path:
        """Download YouTube audio to MP3 in session_dir. Returns the MP3 path."""
        files_before = set(p.name for p in self.session_dir.glob("*"))
        
        if not self.config.use_cli and self.have_ssl():
            # Try Python module path (lazy import)
            try:
                import yt_dlp  # type: ignore
            except Exception as e:
                print(f"[WARN] yt_dlp Python import failed: {e}\n→ Falling back to external yt-dlp binary.")
                return self.download_via_cli(files_before)
            else:
                return self.download_via_module(files_before, yt_dlp)
        else:
            if not self.have_ssl():
                print("[WARN] Python 'ssl' module is unavailable — using external yt-dlp binary.")
            return self.download_via_cli(files_before)
    
    def ytdlp_common_args(self) -> List[str]:
        args = [
            "--format", "bestaudio/best",
            "--no-playlist",
            "--sleep-requests", "6",  # Sleep 6 seconds like the working original
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "--extractor-args", "youtube:player_client=web",
            "--paths", f"home:{self.session_dir}",
            "--output", "%(id)s.%(ext)s",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        ]
        if self.config.cookies and self.config.cookies.exists():
            args += ["--cookies", str(self.config.cookies)]
        else:
            # Try to use browser cookies if module/binary supports it; harmless if unsupported
            args += ["--cookies-from-browser", "chrome"]
        return args
    
    def download_via_cli(self, files_before: set) -> Path:
        binary = self.find_yt_dlp_binary()
        if not binary:
            raise RuntimeError(
                "Could not find external 'yt-dlp' binary.\n"
                "Download it and place it next to this script or add it to PATH:\n"
                "  https://github.com/yt-dlp/yt-dlp/releases (yt-dlp.exe on Windows)"
            )
        
        args = self.ytdlp_common_args()
        cmd = [binary] + args + [self.config.url]
        print(f"[INFO] Running external yt-dlp: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"yt-dlp binary failed with exit code {e.returncode}.") from e
        
        return self._select_mp3_after_download(files_before)
    
    def download_via_module(self, files_before: set, yt_dlp_mod) -> Path:
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "sleep_requests": 6,  # Sleep 6 seconds like the working original
            "extractor_args": {"youtube": {"player_client": ["web"]}},
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
            ],
            "paths": {"home": str(self.session_dir)},
            "outtmpl": {"default": "%(id)s.%(ext)s"},
            "quiet": False,
            "no_warnings": False,
            "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        }
        
        if self.config.cookies and self.config.cookies.exists():
            ydl_opts["cookiefile"] = str(self.config.cookies)
            print(f"[INFO] Using cookies file: {self.config.cookies}")
        else:
            ydl_opts["cookiesfrombrowser"] = ("chrome",)
            print("[WARN] Cookies file not found. Trying cookiesfrombrowser('chrome').")
        
        try:
            with yt_dlp_mod.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.config.url])
        except yt_dlp_mod.utils.DownloadError as e:
            raise RuntimeError(
                f"yt-dlp failed to download the video.\n"
                f"Reason: {e}\n\n"
                "Tips:\n"
                " - Ensure cookies are fresh (file or browser).\n"
                " - Open the URL in your browser, verify it plays, then re-export cookies.\n"
                " - Update yt-dlp:  python -m pip install -U yt-dlp"
            ) from e
        
        return self._select_mp3_after_download(files_before)
    
    def _select_mp3_after_download(self, files_before: set) -> Path:
        files_after = set(p.name for p in self.session_dir.glob("*"))
        new_files = files_after - files_before
        mp3_candidates = [self.session_dir / f for f in new_files if f.lower().endswith(".mp3")]
        
        if not mp3_candidates:
            time.sleep(0.7)
            mp3_candidates = sorted(self.session_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not mp3_candidates:
            raise RuntimeError("Download appears to have succeeded but no MP3 was found in the session directory.")
        
        mp3_path = mp3_candidates[0]
        print(f"[OK] Audio ready: {mp3_path}")
        return mp3_path
    
    def chunk_and_transcribe_whisper(self, mp3_path: Path) -> Tuple[Path, Path]:
        # SSL is required for OpenAI API
        if not self.have_ssl():
            raise RuntimeError(
                "Python 'ssl' module is not available; cannot contact OpenAI API.\n"
                "Please repair your Python installation (install official python.org build, then Repair)."
            )
        
        key = self.require_openai_key()
        try:
            from openai import OpenAI  # lazy import
        except Exception as e:
            raise RuntimeError(f"Cannot import openai package: {e}. Install with: pip install openai") from e
        
        client = OpenAI(api_key=key)
        
        try:
            audio = AudioSegment.from_file(mp3_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Audio file not found: {mp3_path}")
        
        length_ms = len(audio)
        print(f"[INFO] Audio length: {self.ms_to_hms(length_ms)}")
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_md = self.session_dir / f"transcript_{ts}.md"
        transcript_txt = self.session_dir / f"transcript_{ts}.txt"
        
        with open(transcript_md, "w", encoding="utf-8") as f_md, open(transcript_txt, "w", encoding="utf-8") as f_txt:
            f_md.write(f"# Transcript (generated {ts})\n\n")
            
            for i in range(0, length_ms, self.config.chunk_ms):
                start = i
                end = min(i + self.config.chunk_ms, length_ms)
                idx = i // self.config.chunk_ms
                label = f"Chunk {idx+1} [{self.ms_to_hms(start)} → {self.ms_to_hms(end)}]"
                
                print(f"[INFO] Processing {label} …")
                chunk = audio[start:end]
                
                temp_chunk = self.session_dir / f"temp_chunk_{idx}.mp3"
                chunk.export(temp_chunk, format="mp3")
                
                try:
                    with open(temp_chunk, "rb") as af:
                        resp = client.audio.transcriptions.create(model=self.config.whisper_model, file=af)
                    text = resp.text if hasattr(resp, "text") else str(resp)
                finally:
                    try:
                        temp_chunk.unlink(missing_ok=True)
                    except Exception:
                        pass
                
                f_md.write(f"## {label}\n\n{text}\n\n")
                f_txt.write(text + "\n\n")
                print(f"[OK] {label}")
        
        print(f"[OK] Transcript saved: {transcript_md}")
        print(f"[OK] Raw text saved:  {transcript_txt}")
        return transcript_md, transcript_txt
    
    def structure_transcript_with_ollama(self, transcript_md: Path) -> Optional[Path]:
        try:
            from ollama import Client as OllamaClient  # lazy import
        except Exception:
            print("[WARN] Ollama not installed/importable; skipping structuring.")
            return None
        
        try:
            ollama = OllamaClient()
        except Exception as e:
            print(f"[WARN] Could not connect to Ollama: {e}. Skipping structuring.")
            return None
        
        text = transcript_md.read_text(encoding="utf-8")
        
        chunk_size = 3000
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        processed_sections: List[str] = []
        
        for chunk in chunks:
            structure_prompt = (
                "Based on the following transcript slice, produce a concise, SEO-friendly section heading "
                "(single line, no extra commentary). Then stop.\n\n" + chunk
            )
            try:
                resp = ollama.chat(
                    model=self.config.ollama_model,
                    messages=[
                        {"role": "system", "content": "You generate only a crisp section header for clarity and SEO."},
                        {"role": "user", "content": structure_prompt},
                    ],
                )
                header = resp.get("message", {}).get("content", "Section")
            except Exception as e:
                print(f"[WARN] Ollama structuring failed on a chunk: {e}. Using fallback header.")
                header = "Section"
            processed_sections.append(f"## {header}\n\n{chunk}\n\n")
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        structured_md = self.session_dir / f"structured_transcript_{ts}.md"
        structured_md.write_text("# Structured Transcript\n\n" + "".join(processed_sections), encoding="utf-8")
        
        print(f"[OK] Structured transcript saved: {structured_md}")
        return structured_md


def create_audio_pipeline(url: str, **kwargs) -> AudioPipeline:
    """Factory function to create AudioPipeline with sensible defaults"""
    # Create a temporary pipeline instance to use cookie resolution
    temp_pipeline = AudioPipeline.__new__(AudioPipeline)
    cookies_path = temp_pipeline.resolve_default_cookies(kwargs.get('cookies'))
    
    config = AudioConfig(
        url=url,
        cookies=cookies_path,
        chunk_ms=kwargs.get('chunk_min', 10) * 60 * 1000,  # Convert minutes to milliseconds
        outdir=Path(kwargs.get('outdir', 'cache')),
        use_cli=kwargs.get('use_cli', False),
        do_ollama=kwargs.get('do_ollama', False),
        whisper_model=kwargs.get('whisper_model', 'whisper-1')
    )
    return AudioPipeline(config)