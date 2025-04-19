
import yt_dlp

def download_best_match(query: str, **kwargs) -> str:
    ydl_opts = {
        "format": "best[height<=720]",
        "outtmpl": "videos/%(id)s.%(ext)s",
        **kwargs
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        return f"videos/{info['entries'][0]['id']}.mp4"