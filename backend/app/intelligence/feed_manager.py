import feedparser
import logging
from typing import List
from datetime import datetime
from app.intelligence.models import NewsItem
from app.intelligence.sentiment import sentiment_analyzer

logger = logging.getLogger("polymarket_dashboard")

RSS_FEEDS = [
    "http://feeds.reuters.com/reuters/businessNews",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # CNBC Finance
    "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml"
]

class FeedManager:
    def fetch_news(self, limit: int = 20) -> List[NewsItem]:
        all_news = []
        for url in RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: # Take top 5 from each feed
                    
                    # Parse date
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed'):
                         published = datetime(*entry.published_parsed[:6])
                    
                    summary = entry.summary if hasattr(entry, 'summary') else entry.title

                    # Analyze sentiment
                    sentiment = sentiment_analyzer.analyze(summary)

                    item = NewsItem(
                        id=entry.id if hasattr(entry, 'id') else entry.link,
                        title=entry.title,
                        link=entry.link,
                        published_at=published,
                        source=feed.feed.title if hasattr(feed.feed, 'title') else "Unknown",
                        summary=summary,
                        sentiment=sentiment
                    )
                    all_news.append(item)
            except Exception as e:
                logger.error(f"Error fetching feed {url}: {e}")
        
        # Sort by date
        all_news.sort(key=lambda x: x.published_at, reverse=True)
        return all_news[:limit]

feed_manager = FeedManager()
