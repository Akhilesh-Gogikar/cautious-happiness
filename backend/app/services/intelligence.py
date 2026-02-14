import os
import httpx
import asyncio
from duckduckgo_search import DDGS
from typing import List, Tuple
from app.models import Source

class IntelligenceService:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.llama_cpp_host = os.getenv("LLAMA_CPP_HOST", "http://llama-cpp:8080")
        self.ddgs = DDGS()

    async def search_market_news(self, question: str) -> List[Source]:
        """
        Search for live news related to the market question using DuckDuckGo.
        Runs in a thread to verify blocking I/O doesn't freeze the event loop.
        """
        print(f"Searching news for: {question}")
        try:
            # Run blocking DDGS in a thread
            results = await asyncio.to_thread(self.ddgs.text, question, max_results=5)
            
            sources = []
            if results:
                for r in results:
                    sources.append(Source(
                        title=r.get('title', 'Unknown'),
                        url=r.get('href', '#'),
                        snippet=r.get('body', '')
                    ))
            return sources
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    async def generate_forecast_with_reasoning(self, question: str, sources: List[Source], model: str = "lfm-thinking") -> Tuple[float, str]:
        """
        Send news + question to LLM for a probability forecast + reasoning.
        Defaults to LFM2.5-Thinking via llama.cpp.
        """
        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        if not news_text:
            news_text = "No recent news found. Rely on general knowledge."

        prompt = f"""
        [INST] Role: Senior Commodity Intelligence Analyst
        Task: Perform an "Intelligence Mirroring" analysis for {question}.
        
        Context/Market News:
        {news_text}
        
        Instructions:
        1. "The Mirror": Analyze what AI-driven media and data tools are currently feeding to quantitative algorithms.
        2. "The Noise": Identify the dominant sentiment-driven narratives that might be inducing algo-driven volatility.
        3. "The Divergence": Contrast this with the physical market dynamics (supply/demand, logistics, production).
        4. "Algo Interpretation": Predict how a sentiment-following algorithm would likely act on this data.
        5. Provide a "Mirror Confidence Score" (0.00 to 1.00) representing how much of the current market move is likely driven by sentiment/noise vs. physical reality.
        
        Output Format:
        Reasoning: [Your step-by-step analysis of media narratives vs physical reality]
        Mirror Confidence: [0.00-1.00]
        [/INST]
        """
        
        async with httpx.AsyncClient() as client:
            try:
                # Route to llama.cpp if lfm-thinking, else Ollama
                if model == "lfm-thinking":
                    url = f"{self.llama_cpp_host}/completion"
                    payload = {
                        "prompt": prompt,
                        "n_predict": 1024,
                        "temperature": 0.2,
                        "stream": False
                    }
                else:
                    url = f"{self.ollama_host}/api/generate"
                    payload = {
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "num_predict": 1024
                        }
                    }

                response = await client.post(url, json=payload, timeout=300.0)
                response.raise_for_status()
                result = response.json()
                
                if model == "lfm-thinking":
                    response_text = result['content'].strip()
                else:
                    response_text = result['response'].strip()
                
                # Parse
                reasoning = response_text
                prob = 0.5
                
                # Heuristic parsing
                import re
                # Look for "Mirror Confidence: 0.XX" (case insensitive, handle asterisks/bolding)
                # Matches: Mirror Confidence: 0.75, **Mirror Confidence**: 0.75, Mirror Confidence: 75%
                match = re.search(r"Mirror Confidence.*?(\d+(?:\.\d+)?)", response_text, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        val = float(match.group(1))
                        # Normalize percentage if needed (e.g., 75 -> 0.75)
                        if val > 1.0:
                            val = val / 100.0
                        prob = min(max(val, 0.0), 1.0)
                    except ValueError:
                        pass
                else:
                    # Fallback search for just the number near end if explicit label missing
                    # We are careful not to pick up other numbers.
                    # Looking for 0.XX pattern in last 100 chars
                    last_bit = response_text[-100:]
                    match_loose = re.findall(r"(?:^|\s)(0\.\d+)(?:$|\s)", last_bit)
                    if match_loose:
                        prob = float(match_loose[-1])
                
                return prob, reasoning

            except Exception as e:
                print(f"Forecaster Error: {e}")
                err_msg = str(e)
                return 0.5, f"Error generating forecast: {err_msg}"

    async def chat_with_model(self, req) -> str:
        """
        Chat with the model about a specific forecast context.
        Using generic 'req' to avoid circular import issues if possible, or expect req to have .context, .user_message, .model
        """
        prompt = f"""
        [INST] You are an intelligent market analyst.
        
        Context of the conversation (previous forecast):
        {req.context}
        
        User Question: {req.user_message}
        
        Answer the user's question based on the context provided. Be concise and professional.
        [/INST]
        """
        
        async with httpx.AsyncClient() as client:
            try:
                if req.model == "lfm-thinking":
                    url = f"{self.llama_cpp_host}/completion"
                    payload = {
                        "prompt": prompt,
                        "n_predict": 1024,
                        "temperature": 0.2,
                        "stream": False
                    }
                else:
                    url = f"{self.ollama_host}/api/generate"
                    payload = {
                        "model": req.model,
                        "prompt": prompt,
                        "stream": False
                    }

                response = await client.post(url, json=payload, timeout=300.0)
                if response.status_code == 200:
                    result = response.json()
                    if req.model == "lfm-thinking":
                        return result['content'].strip()
                    else:
                        return result['response'].strip()
                
                error_detail = response.text
                print(f"Chat Error ({response.status_code}): {error_detail}")
                return f"I apologize, I am unable to answer right now. (System Error: {response.status_code} - {error_detail[:50]}...)"
            except Exception as e:
                return f"Error: {str(e)}"
