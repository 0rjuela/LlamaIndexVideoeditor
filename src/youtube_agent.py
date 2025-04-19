from utils.youtube_tools import download_best_match

class YoutubeAgent:
    def search(self, math_concept: dict) -> str:
        """Returns path to downloaded video"""
        query = f"{math_concept['concepts']} {math_concept['difficulty']} tutorial"
        return download_best_match(
            query,
            duration_max="20m",
            language="en"
        )