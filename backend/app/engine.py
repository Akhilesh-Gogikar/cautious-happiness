import os
import json
from duckduckgo_search import DDGS
from google import genai
import httpx
from dotenv import load_dotenv
from typing import List, Optional, Tuple
from app.models import Source, ForecastResult, ChatRequest, ChatResponse, OrderBook, AlternativeSignal
from app.execution import SlippageAwareKelly
from app.execution import SlippageAwareKelly
from app.market_client import MockMarketClient
from app.vector_db import VectorDBClient
from app.news_ingestor import NewsIngestor
from app.sentiment import SentimentDetector
from app.connectors.aggregator import DataAggregator
from app.connectors.news import ReutersConnector, APNewsConnector, BloombergConnector
from app.connectors.social import TwitterConnector, RedditConnector, DiscordConnector
from app.connectors.vertical import NOAAConnector, CSPANConnector
from app.alt_data_client import AlternativeDataClient
from app.risk_engine import RiskEngine

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
        self.enable_execution = True 
        
        # RAG Components
        self.vector_db = VectorDBClient()
        self.news_ingestor = NewsIngestor(self.vector_db)
        
        # Execution Modules
        self.execution_algo = SlippageAwareKelly(bankroll=1000.0) 
        self.market_client = MockMarketClient()
        self.alt_data_client = AlternativeDataClient()
        
        # NLP Modules
        self.sentiment_detector = SentimentDetector()
        
        # Data Connectors
        self.social_sources = [
            TwitterConnector(),
            RedditConnector(),
            DiscordConnector()
        ]
        self.social_aggregator = DataAggregator(self.social_sources)

        self.aggregator = DataAggregator([
            ReutersConnector(),
            APNewsConnector(),
            BloombergConnector(),
            NOAAConnector(),
            CSPANConnector()
        ] + self.social_sources)
        
        self.risk_engine = RiskEngine()

    async def search_market_news(self, question: str) -> List[Source]:
        """
        Search for live news, ingest into Vector DB, and retrieve relevant context.
        """
        # 1. Ingest new news
        await self.news_ingestor.fetch_and_store(question, max_results=5)
        
        # 2. Retrieve top related snippets from Vector DB
        sources = await self.vector_db.search(question, limit=7)
        return sources

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

    async def classify_market(self, question: str) -> str:
        """
        Classifies the market question into a domain: Economics, Politics, Science, or Other.
        """
        system_prompt = """You are a Classifier. Categorize the given specific market question into one of these domains:
        - Economics
        - Politics
        - Science
        - Other

        Output ONLY the category name.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}"}
        ]
        
        try:
            category = await self._call_llm(messages, temperature=0.0)
            category = category.strip().replace(".", "")
            if category not in ["Economics", "Politics", "Science"]:
                return "Other"
            return category
        except Exception as e:
            print(f"Classification failed: {e}")
            return "Other"

    async def generate_forecast_with_reasoning(self, question: str, sources: List[Source], alt_signals: List[AlternativeSignal] = None, model: str = None, category: str = "General") -> Tuple[float, str]:
        """
        Generate forecast using Llama.cpp server.
        """
        news_text = "\n".join([f"- {s.title}: {s.snippet}" for s in sources])
        alt_text = ""
        if alt_signals:
            alt_text = "\nAlternative Data Signals:\n" + "\n".join([f"- {s.signal_name} ({s.source_type}): {s.value}. Impact: {s.impact}. {s.description}" for s in alt_signals])
        
        # Domain-Specific Prompts
        domain_prompts = {
            "Economics": "You are a Chief Economist. Focus on macro indicators, central bank policies, and market sentiment.",
            "Politics": "You are a Political Analyst. Focus on polling data, historical election trends, and legislative dynamics.",
            "Science": "You are a Scientific Expert. Focus on peer-reviewed research, technological feasibility, and clinical trial data.",
            "Other": "You are a Superforecaster. Focus on base rates and general implementation details."
        }
        
        persona_prompt = domain_prompts.get(category, domain_prompts["Other"])

        system_prompt = f"""{persona_prompt} Your job is to estimate the probability of a future event.
        Instructions:
        1. Analyze the base rate.
        2. Evaluate context/evidence (including news and alternative non-traditional signals).
        3. Consider counter-arguments.
        4. Provide reasoning.
        5. Conclude with a JSON object: {{"reasoning": "...", "probability": 0.XX}}
        """
        
        user_prompt = f"""
        Event: {question}
        
        Context/News:
        {news_text}
        
        {alt_text}
        
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
        alt_text = ""
        if hasattr(self, 'last_alt_signals') and self.last_alt_signals:
             alt_text = "\nAlt Signals: " + ", ".join([f"{s.signal_name}: {s.value}" for s in self.last_alt_signals])

        prompt = f"""
        Role: Risk Manager. Critique this forecast for "{question}".
        News: {news_text}
        {alt_text}
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

    async def extract_claims(self, text: str) -> List[str]:
        """
        Extract checkable factual claims from the reasoning text using the local LLM.
        """
        system_prompt = """You are a Fact Checker. Extract 3-5 verifiable factual claims from the text.
        Focus on specific numbers, dates, status (e.g., "Inflation is 3.2%").
        Ignore opinions or future speculation.
        Output ONLY a JSON list of strings: ["claim 1", "claim 2"]
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Text: {text}"}
        ]
        
        try:
            response_text = await self._call_llm(messages)
            # Cleaning
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            claims = json.loads(response_text)
            if isinstance(claims, list):
                return claims[:5] # Limit to 5
            return []
        except Exception as e:
            print(f"Claim Extraction Failed: {e}")
            return []

    async def verify_claims(self, claims: List[str]) -> Tuple[str, bool]:
        """
        Verify claims against search results.
        Returns a report string and a boolean (True if passed, False if issues found).
        """
        report_lines = ["**Verification Report:**"]
        all_passed = True
        
        for claim in claims:
            try:
                # Targeted search for the claim
                results = self.ddgs.text(claim, max_results=3)
                if not results:
                    report_lines.append(f"- [?] '{claim}': No data found.")
                    continue
                    
                snippets = "\n".join([r.get('body', '') for r in results])
                
                # Simple LLM Check: Does the evidence support the claim?
                check_prompt = f"""
                Claim: "{claim}"
                Evidence: {snippets}
                
                Is the claim TRUE, FALSE, or UNVERIFIED based on the evidence? 
                Start with TRUE, FALSE, or UNVERIFIED. Then explain briefly.
                """
                
                messages = [
                    {"role": "system", "content": "You are a Truth Arbiter."},
                    {"role": "user", "content": check_prompt}
                ]
                
                verdict = await self._call_llm(messages, temperature=0.0)
                report_lines.append(f"- {verdict}")
                
                if "FALSE" in verdict.upper():
                    all_passed = False
                    
            except Exception as e:
                report_lines.append(f"- [!] Error checking '{claim}': {e}")
        
        return "\n".join(report_lines), all_passed

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
        Run full pipeline with RAG.
        """
        try:
            # 1. Search General News (DDG)
            sources = await self.search_market_news(question)
            # 2. Aggregated Multi-Source Data
            aggregated_sources = await self.aggregator.fetch_all(question)
            all_sources = sources + aggregated_sources

            # 3. Alternative Data
            alt_signals = []
            if self.alt_data_client: # Check if client is enabled/initialized
                alt_signals = self.alt_data_client.get_signals_for_market(question)
            self.last_alt_signals = alt_signals # Cache for critic

            # 4. Classify Market
            category = await self.classify_market(question)
            print(f"Market Classified as: {category}")
            
            init_prob, reasoning = await self.generate_forecast_with_reasoning(question, all_sources, alt_signals, category=category)
            
            # --- Audit Log: AI Decision ---
            try:
                from app.database import SessionLocal
                from app.audit_logger import AuditLogger
                
                db = SessionLocal()
                audit_logger = AuditLogger()
                
                payload = {
                    "question": question,
                    "model": self.model_name,
                    "category": category,
                    "initial_probability": init_prob,
                    "reasoning_snippet": reasoning[:200] if reasoning else "", 
                    "sources_count": len(sources)
                }
                
                audit_logger.log_event(db, "AI_DECISION", payload)
                db.close()
            except Exception as e:
                print(f"Audit Log Failed: {e}")
            # ------------------------------


            # --- Hallucination Guardrails ---
            verification_report = "Verification Skipped"
            if reasoning:
                try:
                    claims = await self.extract_claims(reasoning)
                    if claims:
                        verification_report, is_valid = await self.verify_claims(claims)
                        if not is_valid:
                            # Penalize probability if verification failed significantly
                            if init_prob > 0.5:
                                init_prob = max(0.5, init_prob - 0.2)
                            else:
                                init_prob = min(0.5, init_prob + 0.2)
                            reasoning += f"\n\n[Guardrail Alert]: Probability adjusted due to failed verification."
                except Exception as e:
                    print(f"Guardrail Error: {e}")
                    verification_report = f"Guardrail Error: {e}"
            # --------------------------------

            critique, adj_prob = await self.critique_forecast(question, sources, init_prob, reasoning)
            
            execution_log = "Execution Disabled."
            if self.enable_execution:
                market_id = "test_market_123" 
                order_book = self.market_client.get_order_book(market_id)
                size_usd, shares, vwap = self.execution_algo.optimal_allocation(adj_prob, order_book)
                
                if size_usd > 0:
                    # Risk Check
                    from app.models import TradeSignal, PortfolioPosition
                    
                    # Mock Portfolio for verification
                    mock_portfolio = [
                        PortfolioPosition(
                            asset_id="1", condition_id="c1", question="Will Trump win?", 
                            outcome="Yes", price=0.5, size=200, svalue=400, pnl=0
                        )
                    ]
                    
                    signal = TradeSignal(
                        market_id=market_id,
                        market_question=question,
                        signal_side="BUY_YES",
                        price_estimate=vwap,
                        kelly_size_usd=size_usd,
                        expected_value=0.0, # Not calc here
                        rationale="Engine output",
                        status="PENDING",
                        timestamp=0.0
                    )
                    
                    risk_alerts = self.risk_engine.check_portfolio_risk(signal, mock_portfolio)
                    
                    if any(a.severity == "HIGH" for a in risk_alerts):
                        execution_log = f"BLOCKED BY RISK ENGINE: {[a.message for a in risk_alerts]}"
                    else:
                        warnings = [a.message for a in risk_alerts]
                        warn_text = f" (Warnings: {warnings})" if warnings else ""
                        execution_log = f"OPPORTUNITY: Buy ${size_usd:.2f} ({shares:.1f} shares) @ avg {vwap:.3f}.{warn_text}"
                else:
                    execution_log = "No trade. (Negative EV or Slippage too high)"
            
            # Gather Social Data for Hype/Sentiment Analysis
            social_sources = await self.social_aggregator.fetch_all(question)
            social_snippets = [s.snippet for s in social_sources]
            hype_results = self.sentiment_detector.detect_hype_and_manipulation(social_snippets)
            
            # Determine data sources used
            data_sources = ["RAG"]  # Always use RAG
            if alt_signals:
                data_sources.append("ALT_DATA")
            if social_sources:
                data_sources.append("SOCIAL")
            
            result = ForecastResult(
                search_query=question,
                news_summary=all_sources,
                alternative_signals=alt_signals,
                initial_forecast=init_prob,
                critique=critique,
                adjusted_forecast=adj_prob,
                hype_score=hype_results["hype_score"],
                sentiment_score=hype_results["sentiment_score"],
                discourse_analysis=hype_results["summary"],
                verification_report=verification_report,
                reasoning=reasoning + f"\n\n[Execution Engine]: {execution_log}"
            )
            
            # Store attribution metadata for later use
            result.category = category
            result.data_sources_used = data_sources
            result.model_name = self.model_name
            
            return result
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
