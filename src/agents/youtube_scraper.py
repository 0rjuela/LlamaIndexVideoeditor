# src/agents/youtube_scraper.py
from utils.youtube_utils import download_video
import os
import yt_dlp
import json
import subprocess

class YouTubeScraper:
    def __init__(self, output_path="/app/data/youtube_videos", urls_log_file="/app/data/found_urls.json"):
        self.output_path = output_path
        self.urls_log_file = urls_log_file
    
    def process_video(self, query: str, max_results: int = 1):
        ydl_opts_search = {
            'quiet': False,
            'extract_flat': True,
            'max_entries': max_results,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
                info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                video_urls = [entry['url'] for entry in info.get('entries', []) if entry and 'url' in entry]
                
                # Escribimos las URLs encontradas en un archivo JSON
                with open(self.urls_log_file, 'w') as f:
                    json.dump({"query": query, "urls": video_urls}, f, indent=4)
                print(f"URLs encontradas para la consulta '{query}' guardadas en: {self.urls_log_file}")
                
                if video_urls:
                    first_video_url = video_urls[0]
                    print(f"Descargando video con URL: {first_video_url}")
                    
                    # Handle the return value from download_video based on what it actually returns
                    try:
                        result = download_video(first_video_url, output_path=self.output_path)
                        
                        # Check if the function returns a single path or a tuple
                        if isinstance(result, tuple):
                            # If it returns a tuple, unpack it
                            video_path = result[0]
                            subtitle_path = result[1] if len(result) > 1 else None
                        else:
                            # If it returns a single value, assume it's the video path
                            video_path = result
                            subtitle_path = None
                    except Exception as e:
                        print(f"Error downloading video: {e}")
                        video_path = None
                        subtitle_path = None
                    
                    # If no subtitles, try to download them separately
                    if video_path and not subtitle_path:
                        try:
                            subtitle_path = self.download_subtitles(first_video_url)
                        except Exception as e:
                            print(f"Error downloading subtitles: {e}")
                            subtitle_path = None
                    
                    if video_path:
                        print(f"Video descargado a: {video_path}")
                        if subtitle_path:
                            print(f"Subtítulos descargados a: {subtitle_path}")
                        else:
                            print("No se pudieron descargar los subtítulos.")
                        
                        return {
                            "video_path": video_path,
                            "subtitle_path": subtitle_path,
                            "metadata": None,
                            "key_segments": None
                        }
                    else:
                        print("La descarga del video falló.")
                        return None
                else:
                    print(f"No se encontraron videos para la consulta: {query}")
                    return None
        except Exception as e:
            print(f"Error durante la búsqueda en el agente: {e}")
            import traceback
            traceback.print_exc()
            return None

    def download_subtitles(self, video_url, output_path=None):
        """Download subtitles for a video URL."""
        if output_path is None:
            output_path = self.output_path
            
        os.makedirs(output_path, exist_ok=True)
        base_filename = video_url.split('/')[-1].split('?')[0]  # Extract video ID from URL
        subtitle_output = os.path.join(output_path, f'{base_filename}.en.vtt')
        
        try:
            print(f"Attempting to download subtitles for '{video_url}'...")
            subtitle_command = [
                'yt-dlp',
                '--write-sub',
                '--write-auto-sub',
                '--sub-lang', 'en',
                '--sub-format', 'vtt',
                '-o', os.path.join(output_path, base_filename),  # Base filename without the extension
                '--skip-download',  # Don't download the video again
                video_url
            ]
            subprocess.run(subtitle_command, check=True)
            
            # Check for possible subtitle file names
            possible_names = [
                subtitle_output,
                os.path.join(output_path, f'{base_filename}.en.vtt'),
                os.path.join(output_path, f'{base_filename}.en-US.vtt'),
                os.path.join(output_path, f'{base_filename}.vtt')
            ]
            
            for name in possible_names:
                if os.path.exists(name):
                    print(f"Subtitles found at: {name}")
                    return name
                    
            print("No subtitle file found.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error downloading subtitles: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error downloading subtitles: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    try:
        print("Starting YouTube scraper...")
        scraper = YouTubeScraper()
        test_query = "What is the Einstein relativity about?"  # You can modify this line to search for any topic
        print(f"Searching for: {test_query}")
        result = scraper.process_video(test_query)
        if result:
            print("\nResultado del procesamiento:")
            print(f"Ruta del video: {result['video_path']}")
            print(f"Subtitle path: {result.get('subtitle_path')}")
            print(f"Metadatos: {result['metadata']}")
            print(f"Segmentos clave: {result['key_segments']}")
        else:
            print("No se obtuvo resultado del procesamiento.")
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()