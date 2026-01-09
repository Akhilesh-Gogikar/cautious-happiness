import os
import json
from duckduckgo_search import DDGS
from google import genai
import httpx
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from app.models import Source, ForecastResult, ChatRequest, ChatResponse

load_dotenv()

# Configure Gemini
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) # Will be initialized in init

class ForecasterCriticEngine:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = genai.Client(api_key=api_key) if api_key else None
        self.ddgs = DDGS()

    def search_market_news(self, question: str) -> List[Source]:
        """
        Search for live news related to the market question using DuckDuckGo.
        """
        print(f"Searching news for: {question}")
        results = self.ddgs.text(question, max_results=5)
        # DDGS result format: {'title': ..., 'href': ..., 'body': ...}
        sources = []
        for r in results:
            sources.append(Source(
                title=r.get('title', 'Unknown'),
                url=r.get('href', '#'),
                snippet=r.get('body', '')
            ))
        return sources

    async def generate_forecast_with_reasoning(self, question: str, sources: List[Source], model: str = "openforecaster") -> Tuple[float, str]:
        """
        Send news + question to Ollama (openforecaster) for a probability forecast + reasoning.
        Returns: (probability, reasoning_text)
        """
        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        prompt = f"""
        [INST] You are a Superforecaster. Your job is to estimate the probability of a future event.
        
        Event: {question}
        
        Context/News:
        {news_text}
        
        Instructions:
        1. Analyze the base rate for this type of event.
        2. Evaluate the evidence from the context (strength, credibility).
        3. Consider counter-arguments and risks.
        4. Provide a detailed step-by-step reasoning.
        5. Conclude with a final probability score between 0.00 and 1.00.
        
        Output Format:
        Reasoning: [Your step-by-step analysis]
        Probability: [0.00-1.00]
        [/INST]
        """
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2, # Low temp for precision
                            "num_predict": 1024
                        }
                    },
                    timeout=300.0 # Extended timeout for local inference
                )
                response.raise_for_status()
                result = response.json()
                response_text = result['response'].strip()
                
                # Parse
                reasoning = response_text
                prob = 0.5
                
                # Heuristic parsing
                import re
                # Look for "Probability: 0.XX" at the end
                match = re.search(r"Probability:\s*(0\.\d+|1\.0|0|1)", response_text, re.IGNORECASE)
                if match:
                    prob = float(match.group(1))
                else:
                    # Fallback search for just the number near end
                    match_loose = re.findall(r"0\.\d+", response_text)
                    if match_loose:
                        prob = float(match_loose[-1])
                
                return prob, reasoning

            except Exception as e:
                print(f"Forecaster Error: {e}")
                err_msg = str(e)
                if "model 'openforecaster' not found" in err_msg.lower():
                    print("HINT: Run ./setup_model.sh to install the model.")
                return 0.5, f"Error generating forecast: {err_msg}"

    async def critique_forecast(self, question: str, sources: List[Source], initial_prob: float, initial_reasoning: str) -> Tuple[str, float]:
        """
        Send the forecast to Gemini (or local) to check for hallucinations and bias.
        """
        # Fast fail to local if no key
        if not os.getenv("GEMINI_API_KEY"):
            # Minimal local fallback for now
            return "Local Critic: Verified.", initial_prob

        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        prompt = f"""
        Role: Risk Manager
        Task: Critique a forecast for "{question}".
        
        News Context:
        {news_text}
        
        Analyst Forecast: {initial_prob}
        Analyst Reasoning: {initial_reasoning}
        
        Instructions:
        1. Check if the reasoning aligns with the news.
        2. Identify if the analyst was overconfident or ignored risks.
        3. Provide a short critique.
        4. Provide an Adjusted Probability.
        
        Format:
        Critique: [Text]
        Adjusted Probability: [Number]
        """
        
        try:
            # Using new google-genai SDK
            response = await self.gemini_client.aio.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            text = response.text
            
            critique = "Critique failed"
            adj_prob = initial_prob
            
            lines = text.split('\n')
            for line in lines:
                if line.startswith("Critique:"):
                    critique = line.replace("Critique:", "").strip()
                if line.startswith("Adjusted Probability:"):
                    try:
                        prob_str = line.replace("Adjusted Probability:", "").strip()
                        adj_prob = float(prob_str)
                    except: pass
            return critique, adj_prob

        except Exception as e:
            print(f"Gemini Critic Failed: {e}")
            return "Critic unavailable", initial_prob

    async def chat_with_model(self, req: ChatRequest) -> str:
        """
        Chat with the model about a specific forecast context.
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
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": req.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=300.0
                )
                if response.status_code == 200:
                    return response.json()['response'].strip()
                
                error_detail = response.text
                print(f"Chat Error ({response.status_code}): {error_detail}")
                return f"I apologize, I am unable to answer right now. (System Error: {response.status_code} - {error_detail[:50]}...)"
            except Exception as e:
                return f"Error: {str(e)}"

    async def run_analysis(self, question: str, model: str = "openforecaster") -> ForecastResult:
        """
        Run the full pipeline: Search -> Forecast (w/ Reasoning) -> Critique.
        """
        try:
            sources = self.search_market_news(question)
            init_prob, reasoning = await self.generate_forecast_with_reasoning(question, sources, model=model)
            
            # If forecast failed specifically due to model missing
            if "model 'openforecaster' not found" in reasoning:
                 return ForecastResult(
                    search_query=question,
                    news_summary=sources,
                    initial_forecast=0.0,
                    critique="N/A",
                    adjusted_forecast=0.0,
                    reasoning=None,
                    error="model_missing"
                )

            critique, adj_prob = await self.critique_forecast(question, sources, init_prob, reasoning)
            
            return ForecastResult(
                search_query=question,
                news_summary=sources,
                initial_forecast=init_prob,
                critique=critique,
                adjusted_forecast=adj_prob,
                reasoning=reasoning
            )
        except Exception as e:
            print(f"Engine Error: {e}")
            return ForecastResult(
                search_query=question,
                news_summary=[],
                initial_forecast=0,
                critique="Error",
                adjusted_forecast=0,
                reasoning=str(e),
                error="unknown_error"
            )
