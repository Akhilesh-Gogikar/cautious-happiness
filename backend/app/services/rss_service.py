import feedparser
import logging
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from app.database_users import SessionLocal
from app.models_db import ProposedTrade
from app.engine import ForecasterCriticEngine
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

# List of RSS feeds to monitor
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://cryptopotato.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://decrypt.co/feed"
]

class RssService:
    def __init__(self):
        self.engine = ForecasterCriticEngine()

    async def fetch_and_filter_feeds(self):
        """
        Fetches RSS feeds, filters them using LLM, and stores proposed trades.
        """
        logger.info("Starting RSS fetch and filter cycle...")
        db = SessionLocal()
        try:
            for feed_url in RSS_FEEDS:
                try:
                    logger.info(f"Fetching feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:5]: # Check top 5 from each feed
                        # 1. Deduplication check
                        existing = db.query(ProposedTrade).filter(ProposedTrade.link == entry.link).first()
                        if existing:
                            continue

                        # 2. Extract content
                        title = entry.title
                        summary = getattr(entry, 'summary', '')
                        published_parsed = getattr(entry, 'published_parsed', None)
                        pub_date = datetime.fromtimestamp(time.mktime(published_parsed)) if published_parsed else datetime.utcnow()
                        
                        # Fix for dateutil parser if needed, or just use current time if parsing fails
                        if not published_parsed:
                             try:
                                 if hasattr(entry, 'published'):
                                     pub_date = date_parser.parse(entry.published)
                             except:
                                 pub_date = datetime.utcnow()

                        content_text = f"Title: {title}\nSummary: {summary}"

                        # 3. LLM Filter
                        is_trade, analysis = await self._analyze_with_llm(content_text)

                        if is_trade:
                            logger.info(f"New Proposed Trade found: {title}")
                            new_trade = ProposedTrade(
                                title=title,
                                description=summary[:500], # Trucate if too long
                                link=entry.link,
                                pub_date=pub_date,
                                ai_analysis=analysis,
                                status="NEW"
                            )
                            db.add(new_trade)
                            db.commit()
                        else:
                            logger.debug(f"Skipping: {title}")

                except Exception as e:
                    logger.error(f"Error processing feed {feed_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Global RSS fetch error: {e}")
        finally:
            db.close()

    async def _analyze_with_llm(self, text: str) -> (bool, str):
        """
        Returns (True, reasoning) if the text contains a viable trading opportunity.
        """
        prompt = f"""
        You are a seasoned crypto trader and market analyst.
        Analyze the following news item and determine if it suggests a clear, actionable trading opportunity (high probability trade).
        
        News Item:
        {text}

        Criteria for a "Proposed Trade":
        - News about specific tokens, protocols, or macroeconomic events with direct price impact.
        - Regulatory approvals/bans, major partnerships, hacks, or upgrades.
        - IGNORE general market commentary, "top 5 coins" lists, or vague price predictions without catalysts.

        Output ONLY valid JSON in this format:
        {{
            "is_trade": true/false,
            "reasoning": "Brief explanation of the opportunity and potential impact."
        }}
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            # Reusing the engine's internal call_llm method or similar if accessible, 
            # OR using the public run_analysis interface. 
            # Since engine is complex, let's use its `_call_llm` if we can, or just mock it for now if we can't access it easily.
            # Actually engine._call_llm is available on the instance we created.
            
            # Using low temperature for deterministic output
            response_text = ""
            async for chunk in self.engine._call_llm_stream(messages, temperature=0.1):
                response_text += chunk
            
            # Clean up response (sometimes LLMs add markdown code blocks)
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(response_text)
            return data.get("is_trade", False), data.get("reasoning", "")
            
        except Exception as e:
            logger.error(f"LLM Analysis failed: {e}")
            return False, ""

import time
