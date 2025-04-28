from agents.youtube_analizer import VideoAnalyzer

if __name__ == '__main__':
    # Path to your video file
    video_path = '/app/data/youtube_videos/jnWaUtS2Fr8.webm'
    
    # Create an instance of VideoAnalyzer
    analyzer = VideoAnalyzer(video_path)
    
    # Run the analysis
    segments = analyzer.analyze()
    
    # Print the results
    print(f'Found {len(segments)} important segments')
    for i, segment in enumerate(segments):
        print(f'Segment {i+1}: {segment}')
