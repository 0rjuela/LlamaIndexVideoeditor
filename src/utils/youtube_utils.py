import yt_dlp
import os
import subprocess  

def search_youtube(query: str, max_results: int = 5) -> list[str]:
    """Searches YouTube for videos based on the given query.

    Args:
        query: The search term.
        max_results: The maximum number of video URLs to return.

    Returns:
        A list of YouTube video URLs.
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'entries': f'ytsearch{max_results}:{query}',
        'skip_download': True,
        'ignoreerrors': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
        video_urls = [entry['webpage_url'] for entry in info_dict['entries'] if entry and 'webpage_url' in entry]
    return video_urls

def download_video(url: str, output_path: str = "/app/data/youtube_videos", **kwargs) -> str:
    """Downloads a YouTube video to the specified output path inside the container."""
    os.makedirs(output_path, exist_ok=True)  # Create the directory if it doesn't exist inside the container
    output_template = os.path.join(output_path, '%(id)s.%(ext)s')
    ydl_opts = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "outtmpl": output_template,
        "quiet": False,  # Keep quiet False for download progress
        **kwargs
    }
    try:
        print(f"Attempting download of '{url}' to '{output_path}' inside container...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"yt-dlp info: {info}")
            if info and 'id' in info and 'ext' in info:
                downloaded_file_path = os.path.abspath(os.path.join(output_path, f"{info['id']}.{info['ext']}"))
                print(f"Download successful, file path inside container: {downloaded_file_path}")
                return downloaded_file_path
            else:
                print("Download might have failed: no 'id' or 'ext' in info.")
                return None
    except Exception as e:
        print(f"Error during download inside container: {e}")
        return None

if __name__ == '__main__':
    test_url = "https://www.youtube.com/watch?v=cCyYGYyCka4"  # A known LlamaIndex tutorial URL
    output_directory = "/app/data/youtube_videos"
    print(f"Attempting to directly download: {test_url} to {output_directory}")
    downloaded_path = download_video(test_url, output_path=output_directory)
    print(f"Download attempt result: {downloaded_path}")
    if downloaded_path:
        print(f"Video downloaded to: {downloaded_path}")
    else:
        print("Direct video download failed.")