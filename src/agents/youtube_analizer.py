# src/agents/youtube_analizer.py
print("Starting youtube_analizer.py")
import os
print("os imported")
import subprocess
print("subprocess imported")
from dotenv import load_dotenv
print("dotenv imported")
from llama_index.core import VectorStoreIndex, Document
print("llama_index.core imported")
from llama_index.embeddings.openai import OpenAIEmbedding
print("llama_index.embeddings.openai imported")
from llama_index.core.node_parser import SimpleNodeParser
print("llama_index.core.node parser imported")
from llama_index.llms.openai import OpenAI
print("llama_index.llms imported")
import re
print("re imported")
import pysubs2  # For handling .srt subtitles
print("pysubs2 imported")

class VideoAnalyzer:
    def __init__(self, video_path: str, output_path: str = "/app/data/video_analysis"):
        self.video_path = video_path
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.openai_api_key:
            print("Warning: OPENAI_API_KEY not found in .env file.")

    def analyze(self):
        print(f"Starting analysis of video: {self.video_path}")
        important_segments = self._identify_important_segments()
        print(f"Analysis complete. Important segments identified: {len(important_segments)}")
        return important_segments

    def _load_subtitles_with_time(self, subtitle_path):
        try:
            if subtitle_path.endswith('.vtt'):
                print(f"Loading VTT subtitle from {subtitle_path}")
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                subtitle_data = []
                i = 0
                while i < len(lines):
                    if '-->' in lines[i]:
                        try:
                            time_segment = lines[i].strip().split(' --> ')
                            start_time_str = time_segment[0]
                            end_time_str = time_segment[1].split()[0]
                            
                            def time_to_seconds(t):
                                parts = t.replace(',', '.').split(':')
                                if len(parts) == 3:
                                    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                                elif len(parts) == 2:
                                    return float(parts[0]) * 60 + float(parts[1])
                                return 0
                                
                            start_time = time_to_seconds(start_time_str)
                            end_time = time_to_seconds(end_time_str)
                            
                            i += 1
                            text = ''
                            while i < len(lines) and lines[i].strip() and not '-->' in lines[i]:
                                text += lines[i].strip() + ' '
                                i += 1
                                
                            if text.strip():  # Only add if there's actual text content
                                subtitle_data.append({'start': start_time, 'end': end_time, 'text': text.strip()})
                        except Exception as e:
                            print(f"Error parsing subtitle line: {lines[i]}, error: {e}")
                            i += 1
                    else:
                        i += 1
                        
                print(f"Loaded {len(subtitle_data)} subtitle entries")
                return subtitle_data
            elif subtitle_path.endswith('.srt'):
                try:
                    subs = pysubs2.load(subtitle_path, encoding='utf-8')
                    subtitle_data = []
                    for sub in subs:
                        start_time = sub.start / 1000.0
                        end_time = sub.end / 1000.0
                        text = sub.text.replace('\\N', ' ').replace('\\n', ' ')  # Clean up line breaks
                        subtitle_data.append({'start': start_time, 'end': end_time, 'text': text})
                    print(f"Loaded {len(subtitle_data)} SRT subtitle entries")
                    return subtitle_data
                except Exception as e:
                    print(f"Error loading SRT subtitles: {e}")
                    import traceback
                    traceback.print_exc()
                    return []
            else:
                print(f"Unsupported subtitle format: {subtitle_path}")
                return []
        except Exception as e:
            print(f"Error loading subtitles with time: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _find_subtitle_file(self):
        # First try the default approach - looking for subtitle with same base name
        base_filename = os.path.basename(self.video_path).split('.')[0]
        possible_extensions = ['.en.vtt', '.vtt', '.en.srt', '.srt']
        subtitle_dir = os.path.dirname(self.video_path)
        
        # Debug info
        print(f"Video path: {self.video_path}")
        print(f"Base filename: {base_filename}")
        print(f"Subtitle directory: {subtitle_dir}")
        
        # First try with the original video filename
        for ext in possible_extensions:
            subtitle_path = os.path.join(subtitle_dir, f'{base_filename}{ext}')
            print(f"Checking for: {subtitle_path}")
            if os.path.exists(subtitle_path):
                print(f"Found subtitle file: {subtitle_path}")
                return subtitle_path
        
        # If not found, try looking for 'watch.en.vtt' which is common for YouTube files
        fallback_file = os.path.join(subtitle_dir, 'watch.en.vtt')
        print(f"Checking fallback: {fallback_file}")
        if os.path.exists(fallback_file):
            print(f"Found fallback subtitle file: {fallback_file}")
            return fallback_file
            
        # List all files in the directory for debugging
        print("All files in directory:")
        try:
            for file in os.listdir(subtitle_dir):
                print(f"  {file}")
                # Check if any file in the directory has one of our extensions
                for ext in possible_extensions:
                    if file.endswith(ext):
                        subtitle_path = os.path.join(subtitle_dir, file)
                        print(f"Found potential subtitle file: {subtitle_path}")
                        return subtitle_path
        except Exception as e:
            print(f"Error listing directory: {e}")
            
        print("No subtitle file found.")
        return None

    def _identify_important_segments(self):
        try:
            subtitle_path = self._find_subtitle_file()
            if not subtitle_path:
                print("No subtitle file found for analysis.")
                return []

            subtitle_data = self._load_subtitles_with_time(subtitle_path)
            if not subtitle_data:
                print("No subtitle data loaded.")
                return []
                
            print(f"Processing {len(subtitle_data)} subtitle entries")

            # Combine nearby subtitles into chunks to get more context
            chunked_subtitles = self._chunk_subtitles(subtitle_data)
            print(f"Created {len(chunked_subtitles)} subtitle chunks")

            documents = [Document(text=chunk['text'], metadata={'start': chunk['start'], 'end': chunk['end']}) for chunk in chunked_subtitles]
            
            embed_model = OpenAIEmbedding(api_key=self.openai_api_key)
            llm = OpenAI(model="gpt-3.5-turbo", api_key=self.openai_api_key)

            index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
            query_engine = index.as_query_engine(similarity_top_k=5)

            important_segments = []
            queries = [
                "Identify the main topics or concepts explained in the video and the time they are discussed.",
                "What are the key steps or processes demonstrated, along with their start and end times?",
                "Point out any summaries or key takeaways explicitly mentioned by the speaker and their timestamps.",
                "Find segments where important examples or demonstrations are provided, noting the time.",
            ]

            for query in queries:
                try:
                    response = query_engine.query(query)
                    print(f"Query: {query}\nResponse: {response.response}")
                    extracted_times = self._parse_response_for_time(response.response)
                    important_segments.extend(extracted_times)
                except Exception as e:
                    print(f"Error processing query '{query}': {e}")
                    continue

            # Deduplicate segments based on start and end times
            unique_segments = self._deduplicate_segments(important_segments)
            return unique_segments

        except Exception as e:
            print(f"Error during important segment identification: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _chunk_subtitles(self, subtitle_data, max_gap_seconds=5, max_chunk_seconds=60):
        """Combine nearby subtitles into chunks for better context"""
        if not subtitle_data:
            return []
            
        chunks = []
        current_chunk = {
            'start': subtitle_data[0]['start'],
            'end': subtitle_data[0]['end'],
            'text': subtitle_data[0]['text']
        }
        
        for i in range(1, len(subtitle_data)):
            current_sub = subtitle_data[i]
            time_gap = current_sub['start'] - current_chunk['end']
            
            # If the gap is small and chunk isn't too long, extend current chunk
            if time_gap <= max_gap_seconds and (current_sub['end'] - current_chunk['start']) <= max_chunk_seconds:
                current_chunk['end'] = current_sub['end']
                current_chunk['text'] += " " + current_sub['text']
            else:
                # Save current chunk and start a new one
                chunks.append(current_chunk)
                current_chunk = {
                    'start': current_sub['start'],
                    'end': current_sub['end'],
                    'text': current_sub['text']
                }
        
        # Add the last chunk
        chunks.append(current_chunk)
        return chunks

    def _deduplicate_segments(self, segments):
        """Remove duplicate segments based on similar start/end times"""
        if not segments:
            return []
            
        # Sort by start time
        sorted_segments = sorted(segments, key=lambda x: x['start'])
        unique_segments = [sorted_segments[0]]
        
        for segment in sorted_segments[1:]:
            last_segment = unique_segments[-1]
            # Check if this segment overlaps significantly with the last one
            if abs(segment['start'] - last_segment['start']) <= 10 and abs(segment['end'] - last_segment['end']) <= 10:
                # Segments are similar, keep the one with the longer text description
                if len(segment['text']) > len(last_segment['text']):
                    unique_segments[-1] = segment
            else:
                unique_segments.append(segment)
                
        return unique_segments

    def _parse_response_for_time(self, llm_response: str):
        segments = []
        lines = llm_response.split('\n')
        
        # Pattern for start-end time ranges (e.g., "from 5:20 to 8:45")
        time_range_pattern = re.compile(r'(?:at|around|from)\s*((\d+):(\d+)(?::(\d+))?)\s*(?:to|-|and|–|—)\s*((\d+):(\d+)(?::(\d+))?)')
        
        # Pattern for single timestamps (e.g., "at 5:20")
        single_time_pattern = re.compile(r'(?:at|around)\s*((\d+):(\d+)(?::(\d+))?)')
        
        # Pattern for minutes and seconds format (e.g., "at 5 minutes 20 seconds")
        minute_second_pattern = re.compile(r'(?:at|around)\s*(?:the\s*)?((\d+)\s*minute(?:s)?(?:\s*and)?\s*(\d+)\s*second(?:s)?)')
        
        # Pattern for minutes only (e.g., "at minute 5")
        minute_only_pattern = re.compile(r'(?:at|around)\s*(?:the\s*)?(?:minute|mark|time(?:stamp)?)\s*(\d+)')
        
        def time_to_seconds(hours, minutes, seconds=0):
            try:
                return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            except (ValueError, TypeError) as e:
                print(f"Error converting time to seconds: {e}, hours={hours}, minutes={minutes}, seconds={seconds}")
                return 0

        for line in lines:
            # Try the time range pattern first
            range_match = time_range_pattern.search(line)
            if range_match:
                try:
                    # Extract start time
                    start_hours = int(range_match.group(2)) if range_match.group(2) else 0
                    start_minutes = int(range_match.group(3)) if range_match.group(3) else 0
                    start_seconds = int(range_match.group(4)) if range_match.group(4) else 0
                    
                    # Extract end time
                    end_hours = int(range_match.group(6)) if range_match.group(6) else 0
                    end_minutes = int(range_match.group(7)) if range_match.group(7) else 0
                    end_seconds = int(range_match.group(8)) if range_match.group(8) else 0
                    
                    # Convert to seconds
                    start_total = time_to_seconds(start_hours, start_minutes, start_seconds)
                    end_total = time_to_seconds(end_hours, end_minutes, end_seconds)
                    
                    segments.append({'start': start_total, 'end': end_total, 'text': line.strip()})
                    continue  # Skip to next line
                except Exception as e:
                    print(f"Error parsing time range: {e} in line: '{line}'")
            
            # Try single time pattern
            single_match = single_time_pattern.search(line)
            if single_match:
                try:
                    hours = int(single_match.group(2)) if single_match.group(2) else 0
                    minutes = int(single_match.group(3)) if single_match.group(3) else 0
                    seconds = int(single_match.group(4)) if single_match.group(4) else 0
                    
                    start_time = time_to_seconds(hours, minutes, seconds)
                    end_time = start_time + 30  # Assume 30 second segment
                    
                    segments.append({'start': start_time, 'end': end_time, 'text': line.strip()})
                    continue
                except Exception as e:
                    print(f"Error parsing single time: {e} in line: '{line}'")
            
            # Try minute-second pattern
            ms_match = minute_second_pattern.search(line)
            if ms_match:
                try:
                    minutes = int(ms_match.group(2)) if ms_match.group(2) else 0
                    seconds = int(ms_match.group(3)) if ms_match.group(3) else 0
                    
                    start_time = time_to_seconds(0, minutes, seconds)
                    end_time = start_time + 30  # Assume 30 second segment
                    
                    segments.append({'start': start_time, 'end': end_time, 'text': line.strip()})
                    continue
                except Exception as e:
                    print(f"Error parsing minute-second: {e} in line: '{line}'")
                    
            # Try minute-only pattern
            min_match = minute_only_pattern.search(line)
            if min_match:
                try:
                    minutes = int(min_match.group(1)) if min_match.group(1) else 0
                    
                    start_time = time_to_seconds(0, minutes, 0)
                    end_time = start_time + 60  # Assume 60 second segment
                    
                    segments.append({'start': start_time, 'end': end_time, 'text': line.strip()})
                except Exception as e:
                    print(f"Error parsing minute-only: {e} in line: '{line}'")
                    
        return segments

# Add test code at the end of the file
if __name__ == '__main__':
    print('Starting test of VideoAnalyzer')
    # Path to your video file
    video_path = '/app/data/youtube_videos/jnWaUtS2Fr8.webm'
    
    # Create an instance of VideoAnalyzer
    analyzer = VideoAnalyzer(video_path)
    
    # Run the analysis
    print('Running analyzer...')
    segments = analyzer.analyze()
    
    # Print the results
    print(f'Found {len(segments)} important segments')
    for i, segment in enumerate(segments):
        # Convert seconds to MM:SS format for readability
        start_min = int(segment['start'] // 60)
        start_sec = int(segment['start'] % 60)
        end_min = int(segment['end'] // 60)
        end_sec = int(segment['end'] % 60)
        
        print(f'Segment {i+1}: {start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}')
        print(f'  Description: {segment["text"]}')
        print('-' * 40)
         