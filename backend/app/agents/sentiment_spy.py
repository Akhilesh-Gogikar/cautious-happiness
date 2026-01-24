from typing import Any, Dict
from app.agents.base import BaseAgent
from app.connectors.news import ReutersConnector, BloombergConnector
from app.connectors.social import TwitterConnector, RedditConnector
from app.connectors.aggregator import DataAggregator
from app.sentiment import SentimentDetector

class SentimentSpyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Sentiment-Spy", role="Market Psychologist")
        self.sentiment_detector = SentimentDetector()
        self.news_sources = [ReutersConnector(), BloombergConnector()]
        self.social_sources = [TwitterConnector(), RedditConnector()]
        
        self.news_aggregator = DataAggregator(self.news_sources)
        self.social_aggregator = DataAggregator(self.social_sources)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "BUSY"
        query = input_data.get("query", "")
        self.current_task = f"Gauging market sentiment for {query}"
        self.log(f"Starting sentiment analysis for: {query}")

        try:
            # Fetch and analyze
            news_feeds = await self.news_aggregator.fetch_all(query)
            social_feeds = await self.social_aggregator.fetch_all(query)
            
            all_text = [s.snippet for s in (news_feeds + social_feeds)]
            sentiment_results = self.sentiment_detector.detect_hype_and_manipulation(all_text)
            
            self.log(f"Sentiment analysis complete. Hype: {sentiment_results['hype_score']}, Sentiment: {sentiment_results['sentiment_score']}", level="SUCCESS")
            
            self.status = "COMPLETED"
            return {
                "agent": self.name,
                "sentiment_score": sentiment_results["sentiment_score"],
                "hype_score": sentiment_results["hype_score"],
                "mood_summary": sentiment_results["summary"],
                "timestamp": self.logs[-1]["timestamp"]
            }
        except Exception as e:
            self.status = "ERROR"
            self.log(f"Sentiment analysis failed: {str(e)}", level="ERROR")
            return {"error": str(e)}
