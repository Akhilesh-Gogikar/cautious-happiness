
import logging
from typing import List, Dict, Any
from app.db.session import AsyncSessionLocal
from app.db.models import MarketInsight
from sqlalchemy.future import select
from app.core.ai_client import ai_client

logger = logging.getLogger(__name__)

class CriticAgent:
    def __init__(self):
        pass

    async def critique_insights(self):
        logger.info("Critiquing market insights...")
        async with AsyncSessionLocal() as session:
            # Fetch insights that haven't been critiqued yet
            stmt = select(MarketInsight).where(MarketInsight.critic_score == None)
            result = await session.execute(stmt)
            insights = result.scalars().all()
            
            for insight in insights:
                prompt = f"""
                Critically analyze the following investment thesis:
                
                 Thesis:
                {insight.content}
                
                Check for:
                1. Logical fallacies in the arguments.
                2. Data misinterpretation (e.g., over-relying on small sample sizes of spread data).
                3. Hidden risks that the thesis ignores.
                
                Provide:
                1. A Reliability Score (0.0 to 1.0).
                2. A detailed critique of the arguments.
                """
                
                critique_raw = await ai_client.generate(prompt)
                
                # Naive parsing of score and critique text
                # In a real app, use structured output.
                score = 0.7 # Default
                if "Score:" in critique_raw:
                    try:
                        score_line = [l for l in critique_raw.split("\n") if "Score:" in l][0]
                        score = float(score_line.split(":")[1].strip())
                    except: pass
                
                insight.critic_score = score
                insight.critic_analysis = critique_raw
            
            await session.commit()
            logger.info("Critique complete.")
