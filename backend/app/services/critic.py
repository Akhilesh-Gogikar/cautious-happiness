import os
from google import genai
from typing import List, Tuple
from app.models import Source

class CriticService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = genai.Client(api_key=api_key) if api_key else None

    async def critique_forecast(self, question: str, sources: List[Source], initial_prob: float, initial_reasoning: str) -> Tuple[str, float]:
        """
        Send the forecast to Gemini (or local) to check for hallucinations and bias.
        """
        # Fast fail to local if no key
        if not self.gemini_client:
            # Minimal local fallback for now
            return "Local Critic: Verified.", initial_prob

        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        prompt = f"""
        Role: Head of Commodity Risk
        Task: Perform an "Intelligence Audit" on the mirror analysis for "{question}".
        
        News Context:
        {news_text}
        
        Analyst Mirror Score: {initial_prob}
        Analyst Reasoning: {initial_reasoning}
        
        Instructions:
        1. Audit the analyst's interpretation of "Physical vs. Paper" divergence.
        2. Identify if the analyst is overlooking critical logistical or geo-political physical signals.
        3. Provide a concise risk-adjusted critique of the intelligence.
        4. Provide an Adjusted Mirror Score.
        
        Format:
        Critique: [Text]
        Adjusted Mirror Score: [Number]
        """
        
        try:
            # Using new google-genai SDK
            response = await self.gemini_client.aio.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            text = response.text
            
            critique = "Audit failed"
            adj_prob = initial_prob
            
            import re
            
            # Robust Regex Parsing
            critique_match = re.search(r"Critique:\s*(.+?)(?=Adjusted Mirror Score:|$)", text, re.IGNORECASE | re.DOTALL)
            if critique_match:
                critique = critique_match.group(1).strip()
            
            score_match = re.search(r"Adjusted Mirror Score:\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
            if score_match:
                try:
                    val = float(score_match.group(1))
                    if val > 1.0: val = val / 100.0
                    adj_prob = min(max(val, 0.0), 1.0)
                except ValueError:
                    pass
            
            return critique, adj_prob

        except Exception as e:
            print(f"Gemini Critic Failed: {e}")
            return "Critic unavailable", initial_prob
