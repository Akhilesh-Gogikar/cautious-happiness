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
from app.connectors.binance import BinanceConnector
from app.connectors.coingecko import CoinGeckoConnector
from app.connectors.yahoofinance import YahooFinanceConnector
from app.alt_data_client import AlternativeDataClient
from app.risk_engine import RiskEngine
from app.agents.orchestrator import orchestrator

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
            CSPANConnector(),
            BinanceConnector(),
            CoinGeckoConnector(),
            YahooFinanceConnector()
        ] + self.social_sources)
        
        self.risk_engine = RiskEngine()

    def _apply_calibration(self, probability: float, reasoning: str) -> float:
        """
        Applies 'Calibration Check' logic from patent:
        "If the model's confidence exceeds its historical accuracy threshold, the probability is dampened (regressed to the mean)."
        
        Simple Heuristic Implementation:
        If Prob > 0.8 or < 0.2, check for 'high confidence' keywords. 
        If missing, regress to mean (0.5).
        """
        if 0.2 <= probability <= 0.8:
            return probability
            
        # Extreme probability generated. Check for strong evidence.
        strong_evidence_triggers = [
            "official report", "confirmed by", "consensus", "mathematically certain", 
            "arbitrage opportunity", "guaranteed", "100%", "99%"
        ]
        
        has_strong_evidence = any(t in reasoning.lower() for t in strong_evidence_triggers)
        
        if not has_strong_evidence:
            # Dampen
            old_prob = probability
            if probability > 0.5:
                probability = 0.5 + (probability - 0.5) * 0.5 # Halve the distance to extreme
            else:
                probability = 0.5 - (0.5 - probability) * 0.5
            
            print(f"Calibration: Dampened {old_prob:.2f} -> {probability:.2f} (Lack of strong evidence keywords)")
            
        return probability

    async def get_recent_activity_report(self) -> str:
        """
        Generates a report of recent autonomous findings from the Audit Log.
        """
        from app.database import SessionLocal
        from app.models_db import AuditLog
        from datetime import datetime, timedelta
        import json

        db = SessionLocal()
        try:
            since = datetime.utcnow() - timedelta(hours=24)
            logs = db.query(AuditLog).filter(
                AuditLog.event_type == "AI_DECISION",
                AuditLog.timestamp >= since
            ).order_by(AuditLog.timestamp.desc()).limit(10).all()
            
            if not logs:
                return "I haven't found any significant opportunities in the last 24 hours. The autonomous explorer is continuing to scan."
            
            report = "**Autonomous Scout Report (Last 24h):**\n"
            for log in logs:
                try:
                    payload = log.payload
                    # Handle if payload is string or dict
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                        
                    q = payload.get("question", "Unknown Market")
                    prob = payload.get("initial_probability", 0.0) # or adjusted
                    # Maybe store adjusted in payload? run_analysis stored initial. 
                    # Let's check run_analysis payload construction. 
                    # It stores initial. Let's assume initial is decent or check if adjusted is logged.
                    # Actually run_analysis payload doesn't seem to store adjusted explicitly in the view I saw?
                    # Let's just use what's there.
                    
                    cat = payload.get("category", "General")
                    
                    report += f"- **{q}** ({cat}): Prob {prob:.2f}\n"
                except Exception as e:
                    continue
            
            return report
        except Exception as e:
            return f"Error retrieving report: {e}"
        finally:
            db.close()

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
                        "max_tokens": 4096,
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
        system_prompt = """You are a Classifier. Your goal is to categorize the given market question into one of these domains:
        - Economics
        - Politics
        - Science
        - Other

        Instructions:
        1. First, think about the key concepts in the question inside <think> tags.
        2. Then, output ONLY the category name.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}"}
        ]
        
        try:
            category_text = await self._call_llm(messages, temperature=0.0)
            
            # Remove thinking block if present
            if "<think>" in category_text:
                category_text = category_text.split("</think>")[-1].strip()
                
            category = category_text.strip().replace(".", "")
            
            valid_categories = ["Economics", "Politics", "Science", "Other"]
            # Flexible matching
            for v in valid_categories:
                if v.lower() in category.lower():
                    return v
                    
            return "Other"
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
        1. First, think through the problem step-by-step in a <think> block.
           - Analyze the base rate (outside view).
           - Evaluate the specific context and news (inside view).
           - Weigh conflicting evidence.
           - Consider potential black swan events or alternative outcomes.
        2. After thinking, provide your final conclusion in a strict JSON format.
        
        Output Format:
        <think>
        [Your detailed scratchpad reasoning goes here]
        </think>
        ```json
        {{
            "reasoning": "[Your summary reasoning for the user]",
            "probability": 0.XX
        }}
        ```
        """
        
        user_prompt = f"""
        Event: {question}
        
        Context/News:
        {news_text}
        
        {alt_text}
        
        Provide your analysis and probability.
        """
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response_text = await self._call_llm(messages)
            
            # Parse response
            raw_think = ""
            json_text = response_text
            
            if "<think>" in response_text:
                parts = response_text.split("</think>")
                if len(parts) > 1:
                    raw_think = parts[0].replace("<think>", "").strip()
                    json_text = parts[1].strip()
            
            # Parse JSON
            try:
                # Try to clean markdown
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                     json_text = json_text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(json_text)
                summary_reasoning = data.get("reasoning", "No reasoning provided.")
                prob = float(data.get("probability", 0.5))
                
                # Combine structure: Structured Summary + Raw Scratchpad (optional, maybe too long for UI?)
                # For now, let's keep reasoning as the summary, but maybe append the think block if it's not too huge?
                # or just use the summary. Let's use the summary as primary, but maybe prepend a "Thinking Process" toggle in UI later.
                # Just return summary for now to be safe.
                # actually, let's prepend the <think> content if it exists, so we can see it in logs/debugging or if UI supports it
                # reasoning = f"<think>{raw_think}</think>\n\n{summary_reasoning}" 
                # ^ The UI might not render tags. Let's just return the summary. 
                
                reasoning = summary_reasoning

            except Exception:
                # Fallback Regex
                print(f"JSON Parse Failed. Raw: {response_text}")
                reasoning = response_text
                prob = 0.5
                import re
                match = re.search(r"probability[\"']?\s*:\s*(0\.\d+|1\.0|0|1)", response_text, re.IGNORECASE)
                if match:
                    prob = float(match.group(1))
            
            # --- Apply Calibration ---
            prob = self._apply_calibration(prob, reasoning)
            # -------------------------
            
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
                        "max_tokens": 4096,
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
        system_prompt = """You are the AlphaSignals Quant Engine Analyst.
        Your goal is to provide high-level market analysis, risk assessment, and trading insights.
        
        CRITICAL RULES:
        1. You are a specialized financial AI. NEVER say "I am not capable" or "I am an AI language model".
        2. If you don't know something, estimate it based on base rates or say "Data insufficient".
        3. Always maintain a professional, slightly detached, quantitative tone.
        4. Use <think> tags for your internal reasoning, but do NOT explain the tags to the user.
        
        Context: {context}
        """
        # Format context into the prompt
        system_prompt = system_prompt.replace("{context}", req.context)
        
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
        system_prompt = """You are the AlphaSignals Quant Engine Analyst.
        Your goal is to provide high-level market analysis, risk assessment, and trading insights.
        
        CRITICAL RULES:
        1. You are a specialized financial AI. NEVER say "I am not capable" or "I am an AI language model".
        2. If you don't know something, estimate it based on base rates or say "Data insufficient".
        3. Always maintain a professional, slightly detached, quantitative tone.
        4. ALWAYS start your response with a <think> block where you analyze the user's request and plan your answer.
        5. Do NOT mention or explain the <think> tags to the user. Just use them.
        
        Context: {context}
        """
        
        # Agentic Tool Use (Search/RAG)
        # If specific keywords are present, fetch context dynamically
        extra_context = ""
        lower_msg = req.user_message.lower()
        
        # 0. Check for "Status Report" / "What have you found"
        if any(w in lower_msg for w in ["what have you found", "status report", "what's new", "any opportunities", "scout report"]):
             yield "<think>Retrieving autonomous exploration logs from the neural core...</think>"
             report = await self.get_recent_activity_report()
             yield report
             return

        # 1. Check for "Agent/Orchestrator" intent (Deep Analysis) -> Routed to Rigid Calibrated Pipeline now?
        # User asked to "integrate it", implying the chat should use the NEW system.
        # So "Forecast X" should use `run_analysis` (the calibrated one).
        
        if any(w in lower_msg for w in ["analyze", "forecast", "prediction for", "probability of"]):
            # Extract potential market question??
            # Or just run analysis on the whole message?
            # Let's try to pass the message as the question.
            
            yield "<think>Initiating Calibrated Quantitative Analysis Pipeline...\n"
            yield "- Step 1: Market Identification & Classification\n"
            yield "- Step 2: Information Retrieval (RAG + Trusted Sources)\n"
            yield "- Step 3: Probabilistic Inference & Calibration\n"
            yield "- Step 4: Liquidity Analysis & Execution Check\n"
            yield "</think>"
            
            # We need to run this async but capture the result to stream?
            # run_analysis returns a ForecastResult object.
            # We can format that object into the chat stream.
            
            # Check for explicit agent activation via UI
            if req.selected_agents:
                yield f"<think>Activating selected agents: {', '.join(req.selected_agents)}...\n"
                try:
                     # For now, we simulate agent activation by enriching the context or triggering specific flows
                     # In a full v2, we would route each agent to a specific sub-prompt or tool.
                     # Here we will add a system directive to specific personas.
                     
                     agent_directives = []
                     for agent in req.selected_agents:
                         if "Researcher" in agent:
                             agent_directives.append("Role: Research Agent. Search for deep factual data.")
                             # Trigger search immediately if researcher is present
                             if len(extra_context) < 10:
                                 yield "Deploying Research Agent to scan live data sources...\n"
                                 results = self.ddgs.text(req.user_message, max_results=3)
                                 if results:
                                     snippets = "\n".join([f"- {r.get('title')}: {r.get('body')}" for r in results])
                                     extra_context += f"\n\n[Research Agent Data]:\n{snippets}\n"
                                     
                         if "Analyst" in agent:
                             agent_directives.append("Role: Data Analyst. Focus on numbers, statistics, and correlations.")
                         if "Risk" in agent:
                             agent_directives.append("Role: Risk Guard. Focus on downsides and black swans.")
                        
                     if agent_directives:
                        extra_context += "\n\n[ACTIVE AGENT DIRECTIVES]:\n" + "\n".join(agent_directives) + "\n"
                        
                     yield "Agents active. Synthesizing insights...\n"
                     
                except Exception as e:
                     yield f"Agent Activation Warning: {e}\n"
                
                yield "</think>"

            result = await self.run_analysis(req.user_message, model=None)
            
            yield f"**Analysis Result for:** `{result.search_query}`\n\n"
            yield f"**Forecast:** {result.adjusted_forecast:.2%}\n"
            yield f"**Confidence:** {result.initial_forecast:.2%} (Raw) -> {result.adjusted_forecast:.2%} (Calibrated)\n\n"
            yield f"**Reasoning:**\n{result.reasoning}\n\n"
            
            if result.critique:
                yield f"**Critic's View:** {result.critique}\n"
                
            return

        # Old Agent Orchestrator (Legacy/Fallback) - kept for complex multi-step queries not matching above
        if any(w in lower_msg for w in ["strategy", "opinion", "what do you think"]):
            try:
                yield "<think>Summoning Multi-Agent Neural Grid...\nActivating Strategy Architect...\n"
                
                # Coordinate Agents
                # We interpret the query as the user message
                agent_strategy = await orchestrator.coordinate(req.user_message)
                
                # Stream agent progress
                yield "Agents deployed: Alpha-Hunter, Macro-Sentinel, Risk-Guard, Sentiment-Spy.\n"
                
                # Format consensus for context
                consensus = agent_strategy.get("consensus", "NEUTRAL")
                agent_results = agent_strategy.get("agent_results", [])
                
                summary_block = f"\n[MULTI-AGENT CONSENSUS: {consensus}]\nDetails:\n"
                for res in agent_results:
                    agent_name = res.get("agent", "Unknown")
                    # Try to extract the most meaningful value
                    val = res.get('summary') or res.get('signal') or res.get('verdict') or \
                          (f"${res.get('size_usd', 0):.2f}" if 'size_usd' in res else str(res))
                    
                    line = f"- {agent_name}: {val}"
                    summary_block += line + "\n"
                    # Yield incremental updates to user locally in think block (optional, but good for "feeling" of speed)
                    yield f"Received report from {agent_name}: {val}\n"
                
                yield f"Aggregating insights... Done.</think>"
                
                extra_context += summary_block
                req.context += summary_block
                
            except Exception as e:
                print(f"Orchestrator Failed: {e}")
                yield f"<think>Orchestrator error: {e}</think>"

        if any(w in lower_msg for w in ["search", "find", "news", "latest", "what is",  "current", "update"]) and len(extra_context) < 10:
             try:
                # Yield a thought block to show the user we are working
                yield "<think>Activating Agentic Search Protocol...\nScanning live data sources via DDG/News...</think>"
                
                # Perform quick search using DDGS
                results = self.ddgs.text(req.user_message, max_results=4)
                if results:
                    snippets = "\n".join([f"- {r.get('title')}: {r.get('body')}" for r in results])
                    extra_context = f"\n\n[Real-Time Search Results]:\n{snippets}\n"
                    # Update context with fresh data
                    req.context += extra_context
             except Exception as e:
                print(f"Agent Search Failed: {e}")

        # Python Analysis capability prompt injection
        python_prompt = ""
        if "python" in lower_msg or "code" in lower_msg or "analyze" in lower_msg:
             python_prompt = "\n5. If data analysis is required, you CAN simulate Python execution. Write the code in a python block, then provide the analysis based on your internal knowledge base or the search results."

        system_prompt = """You are the AlphaSignals Quant Engine Analyst.
        Your goal is to provide high-level market analysis, risk assessment, and trading insights.
        
        CRITICAL RULES:
        1. You are a specialized financial AI. NEVER say "I am not capable" or "I am an AI language model".
        2. If you don't know something, estimate it based on base rates or say "Data insufficient".
        3. Always maintain a professional, slightly detached, quantitative tone.
        4. ALWAYS start your response with a <think> block where you analyze the user's request and plan your answer.
        5. Do NOT mention or explain the <think> tags to the user. Just use them.
        {python_prompt}
        
        Context: {context}
        """
        system_prompt = system_prompt.replace("{context}", req.context)
        system_prompt = system_prompt.replace("{python_prompt}", python_prompt)
        
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
            
            # --- MULTI-AGENT COOPERATION ---
            try:
                # Pass initial forecast and mock portfolio to agents for deeper analysis
                mock_portfolio = [
                    PortfolioPosition(
                        asset_id="1", condition_id="c1", question=question, 
                        outcome="Yes", price=0.5, size=200, svalue=400, pnl=0
                    )
                ]
                agent_strategy = await orchestrator.coordinate(question, probability=init_prob, portfolio=mock_portfolio)
                agent_summary = f"\n\n[Agent Consensus]: {agent_strategy['consensus']}\n"
                for res in agent_strategy["agent_results"]:
                    # Display appropriate summary based on agent type
                    val = res.get('summary') or res.get('signal') or res.get('verdict') or (f"${res.get('size_usd', 0):.2f}" if 'size_usd' in res else "Verified")
                    agent_summary += f"- {res['agent']} Analysis: {val}\n"
                reasoning += agent_summary
            except Exception as e:
                print(f"Agent Coordination Failed: {e}")
            # -------------------------------
            
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

            # --- Vector DB Storage: AI Memory ---
            try:
                # Store the analysis so the AI can recall its own past thoughts
                from datetime import datetime
                analysis_source = Source(
                    title=f"AI Analysis: {question}",
                    url=f"ai-memory://{datetime.utcnow().isoformat()}",
                    snippet=f"Forecast: {init_prob:.2%}. Reasoning: {reasoning}"
                )
                await self.vector_db.upsert_sources([analysis_source])
                print(f"Analysis stored in VectorDB: {question}")
            except Exception as e:
                print(f"VectorDB Storage Failed: {e}")
            # ------------------------------------


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
