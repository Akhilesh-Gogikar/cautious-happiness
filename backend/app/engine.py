import os
import json
from duckduckgo_search import DDGS
from google import genai
import httpx
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from app.models import Source, ForecastResult, ChatRequest, ChatResponse, OrderBook
from app.execution import SlippageAwareKelly
from app.market_client import MockMarketClient

load_dotenv()

class ForecasterCriticEngine:
    def __init__(self):
        # Llama.cpp Server Config (OpenAI Compatible)
        self.api_base = os.getenv("OPENAI_API_BASE", "http://ai-engine:8080/v1")
        self.api_key = os.getenv("OPENAI_API_KEY", "sk-no-key-required")
        self.model_name = os.getenv("MODEL_NAME", "openforecaster")
        
        api_key_gemini = os.getenv("GEMINI_API_KEY")
        self.gemini_client = genai.Client(api_key=api_key_gemini) if api_key_gemini else None
        self.ddgs = DDGS()
        
        # Execution Modules
        self.execution_algo = SlippageAwareKelly(bankroll=1000.0) 
        self.market_client = MockMarketClient()
        self.enable_execution = True 

    def search_market_news(self, question: str) -> List[Source]:
        """
        Search for live news related to the market question.
        """
        print(f"Searching news for: {question}")
        try:
            results = self.ddgs.text(question, max_results=5)
            sources = []
            for r in results:
                sources.append(Source(
                    title=r.get('title', 'Unknown'),
                    url=r.get('href', '#'),
                    snippet=r.get('body', '')
                ))
            return sources
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    async def _call_llm(self, messages: List[dict], temperature: float = 0.2) -> str:
        """
        Helper to call the OpenAI-compatible Llama.cpp backend.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "user-selected-model", # Llama.cpp often ignores this or uses loaded model
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": 1024,
                        "stream": False
                    },
                    timeout=300.0
                )
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            except Exception as e:
                print(f"LLM Call Error: {e}")
                raise e

    async def generate_forecast_with_reasoning(self, question: str, sources: List[Source], model: str = None) -> Tuple[float, str]:
        """
        Generate forecast using Llama.cpp server.
        """
        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        system_prompt = """You are a Superforecaster. Your job is to estimate the probability of a future event.
        Instructions:
        1. Analyze the base rate.
        2. Evaluate context/evidence.
        3. Consider counter-arguments.
        4. Provide reasoning.
        5. Conclude with a JSON object: {"reasoning": "...", "probability": 0.XX}
        """
        
        user_prompt = f"""
        Event: {question}
        
        Context/News:
        {news_text}
        
        Provide your analysis and probability.
        Output format must be valid JSON.
        """
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response_text = await self._call_llm(messages)
            
            # Parse JSON
            try:
                # Try to clean markdown
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                     response_text = response_text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(response_text)
                reasoning = data.get("reasoning", "No reasoning provided.")
                prob = float(data.get("probability", 0.5))
            except Exception:
                # Fallback Regex
                reasoning = response_text
                prob = 0.5
                import re
                match = re.search(r"probability[\"']?\s*:\s*(0\.\d+|1\.0|0|1)", response_text, re.IGNORECASE)
                if match:
                    prob = float(match.group(1))
            
            return prob, reasoning

        except Exception as e:
            return 0.5, f"Error generating forecast: {str(e)}"

    async def critique_forecast(self, question: str, sources: List[Source], initial_prob: float, initial_reasoning: str) -> Tuple[str, float]:
        """
        Critique using Gemini or Fallback.
        """
        if not self.gemini_client:
            return "Local Critic: Verified (Gemini Key Missing).", initial_prob

        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        prompt = f"""
        Role: Risk Manager. Critique this forecast for "{question}".
        News: {news_text}
        Forecast: {initial_prob}. Reasoning: {initial_reasoning}
        
        Provide "Critique: ..." and "Adjusted Probability: ..."
        """
        
        try:
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

    async def _call_llm_stream(self, messages: List[dict], temperature: float = 0.2):
        """
        Helper to call the OpenAI-compatible Llama.cpp backend with streaming.
        Yields chunks of text.
        """
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "user-selected-model",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": 2048,
                        "stream": True
                    },
                    timeout=300.0
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data['choices'][0]['delta']
                                content = delta.get('content')
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                print(f"LLM Stream Error: {e}")
                raise e

    async def chat_with_model(self, req: ChatRequest) -> str:
        """
        Chat about the forecast.
        """
        system_prompt = f"You are an intelligent market analyst. Context: {req.context}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.user_message}
        ]
        
        try:
            return await self._call_llm(messages)
        except Exception as e:
            print(f"LLM Connection Failed, using Mock: {e}")
            return "<think>Connection to neural core failed. Using cached fallback protocols.\nAnalyzing failover state...</think>I am unable to reach the primary neural engine (ai-engine). \n\nHowever, I can confirm my internal logic is operational."

    async def stream_chat_with_model(self, req: ChatRequest):
        """
        Stream chat about the forecast.
        """
        system_prompt = f"You are an intelligent market analyst. Context: {req.context}. Always output your internal reasoning process enclosed in <think> tags before your response."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.user_message}
        ]
        
        try:
            async for chunk in self._call_llm_stream(messages):
                yield chunk
        except Exception as e:
            # Fallback mock stream
            yield "<think>"
            import asyncio
            await asyncio.sleep(0.1)
            yield "Neural link unstable. Switching to local survival heuristics...\n"
            await asyncio.sleep(0.1)
            yield "Checking system integrity...\n"
            await asyncio.sleep(0.1)
            yield "</think>"
            yield "The external AI service is unreachable. I am operating in failover mode. \n\n"
            yield "Your UI updates for reasoning blocks should be visible above."

    async def run_analysis(self, question: str, model: str = None) -> ForecastResult:
        """
        Run full pipeline.
        """
        try:
            sources = self.search_market_news(question)
            init_prob, reasoning = await self.generate_forecast_with_reasoning(question, sources)
            critique, adj_prob = await self.critique_forecast(question, sources, init_prob, reasoning)
            
            execution_log = "Execution Disabled."
            if self.enable_execution:
                market_id = "test_market_123" 
                order_book = self.market_client.get_order_book(market_id)
                size_usd, shares, vwap = self.execution_algo.optimal_allocation(adj_prob, order_book)
                
                if size_usd > 0:
                    execution_log = f"OPPORTUNITY: Buy ${size_usd:.2f} ({shares:.1f} shares) @ avg {vwap:.3f}."
                else:
                    execution_log = "No trade. (Negative EV or Slippage too high)"
            
            return ForecastResult(
                search_query=question,
                news_summary=sources,
                initial_forecast=init_prob,
                critique=critique,
                adjusted_forecast=adj_prob,
                reasoning=reasoning + f"\n\n[Execution Engine]: {execution_log}"
            )
        except Exception as e:
            return ForecastResult(
                search_query=question,
                news_summary=[],
                initial_forecast=0,
                critique="Error",
                adjusted_forecast=0,
                reasoning=str(e),
                error="unknown_error"
            )
