# src/agents/youtube_scraper.py
from utils.youtube_utils import download_video
import os
import yt_dlp
import json # Importamos la librería json

class YouTubeScraper:
    def __init__(self, output_path="/app/data/youtube_videos", urls_log_file="/app/data/found_urls.json"): # Definimos la ruta del archivo JSON
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
                    downloaded_path = download_video(first_video_url, output_path=self.output_path)
                    if downloaded_path:
                        print(f"Video descargado a: {downloaded_path}")
                        return {"video_path": downloaded_path, "metadata": None, "key_segments": None}
                    else:
                        print("La descarga del video falló.")
                        return None
                else:
                    print(f"No se encontraron videos para la consulta: {query}")
                    return None
        except Exception as e:
            print(f"Error durante la búsqueda en el agente: {e}")
            return None

if __name__ == "__main__":
    scraper = YouTubeScraper()
    test_query = "How to build an agent with LamaIndex?"
    result = scraper.process_video(test_query)
    if result:
        print("\nResultado del procesamiento:")
        print(f"Ruta del video: {result['video_path']}")
        print(f"Metadatos: {result['metadata']}")
        print(f"Segmentos clave: {result['key_segments']}")