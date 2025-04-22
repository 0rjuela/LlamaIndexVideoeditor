import yt_dlp
import os
import subprocess  
import json 

def search_youtube(query: str, max_results: int = 1) -> list[str]: # Reduced max_results for simplicity
    """Searches YouTube for videos based on the given query.

    Args:
        query: The search term.
        max_results: The maximum number of video URLs to return.

    Returns:
        A list of YouTube video URLs.
    """
    ydl_opts = {
        'quiet': False, # Set to False to see more output
        'extract_flat': 'in_playlist', # Let's keep this for now
        'entries': f'ytsearch{max_results}:{query}',
        'skip_download': True,
        'ignoreerrors': False, # Keep this as False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
            print(json.dumps(info_dict, indent=4)) # Print the raw info dictionary
            video_urls = [entry.get('webpage_url') for entry in info_dict.get('entries', []) if entry and entry.get('webpage_url')]
            return video_urls
        except Exception as e:
            print(f"An error occurred during search: {e}")
            return []

def download_video(url: str, output_path: str = "/app/data/youtube_videos", **kwargs) -> tuple[str | None, str | None]:
    """Downloads a YouTube video and its subtitles using subprocess."""
    os.makedirs(output_path, exist_ok=True)
    base_filename = url.split('/')[-1]  # Extract video ID from URL
    video_output_path = os.path.join(output_path, f'{base_filename}.mp4')
    subtitle_output_path = os.path.join(output_path, f'{base_filename}.en.vtt')

    video_success = False
    subtitle_success = False

    try:
        print(f"Attempting to download video for '{url}' using subprocess...")
        video_command = [
            'yt-dlp',
            '-o', video_output_path,
            '-f', 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            url
        ]
        subprocess.run(video_command, check=True, capture_output=True)
        video_success = True
        print(f"Video downloaded to: {video_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e.stderr.decode()}")
    except FileNotFoundError:
        print("Error: yt-dlp command not found. Is it installed in the container?")

    try:
        print(f"Attempting to download subtitles for '{url}' using subprocess...")
        subtitle_command = [
            'yt-dlp',
            '--write-sub',
            '--write-auto-sub',
            '--sub-lang', 'en',
            '--sub-format', 'vtt',
            '-o', subtitle_output_path,
            '--skip-download',  # Don't download the video again
            url
        ]
        subprocess.run(subtitle_command, check=True, capture_output=True)
        subtitle_success = True
        print(f"Subtitles downloaded to: {subtitle_output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading subtitles: {e.stderr.decode()}")
    except FileNotFoundError:
        print("Error: yt-dlp command not found. Is it installed in the container?")

    return video_output_path if video_success else None, subtitle_output_path if subtitle_success else None

if __name__ == '__main__':
    test_url = "https://www.youtube.com/watch?v=jnWaUtS2Fr8"  # Use the same test URL
    output_directory = "/app/data/youtube_videos"
    print(f"Attempting to directly download: {test_url} to {output_directory} using subprocess")
    downloaded_paths = download_video(test_url, output_path=output_directory)
    print(f"Download attempt result: {downloaded_paths}")
    if downloaded_paths and downloaded_paths[0]:
        print(f"Video downloaded to: {downloaded_paths[0]}")
        if downloaded_paths[1]:
            print(f"Subtitles downloaded to: {downloaded_paths[1]}")
        else:
            print("No English subtitles were downloaded.")
    else:
        print("Video download failed.")