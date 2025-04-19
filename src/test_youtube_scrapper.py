
import os
from agents.youtube_scraper import YouTubeScraper

if __name__ == "__main__":
    try:
        # Create an instance of the YouTubeScraper
        scraper = YouTubeScraper()

        # Define a test query
        test_query = "What is LlamaIndex?"

        # Process the video
        result = scraper.process_video(test_query)

        # Print the results
        print("Processing complete from within Docker!")
        print(f"Video Path: {result['video_path']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Key Segments: {result['key_segments']}")

        # Clean up the downloaded video file
        if os.path.exists(result['video_path']):
            os.remove(result['video_path'])
            print(f"\nCleaned up: Removed {result['video_path']}")

    except Exception as e:
        print(f"An error occurred within Docker: {e}")