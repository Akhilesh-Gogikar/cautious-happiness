import logging
import threading
from app.domain.intelligence.models import SentimentScore

logger = logging.getLogger("polymarket_dashboard")

class SentimentAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentAnalyzer, cls).__new__(cls)
            cls._instance.model_name = "ProsusAI/finbert"
            cls._instance.pipeline = None
            cls._instance._load_attempted = False
            cls._instance._load_lock = threading.Lock()
        return cls._instance

    def load_model(self):
        # Loaded on first use rather than at import so API startup does not
        # pull in transformers or download FinBERT (~440 MB). Attempted once;
        # concurrent first callers wait on the lock for the outcome.
        with self._load_lock:
            if self._load_attempted:
                return
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

                logger.info(f"Loading sentiment model: {self.model_name}")
                tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                self.pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
                logger.info("Sentiment model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load sentiment model: {e}")
                self.pipeline = None
            finally:
                self._load_attempted = True

    def analyze(self, text: str) -> SentimentScore:
        if not self._load_attempted:
            self.load_model()

        if not self.pipeline:
            logger.warning("Sentiment model not loaded. Returning neutral.")
            return SentimentScore(label="neutral", score=0.0)

        try:
            # Truncate text to avoid token limit issues (FinBERT max 512 tokens)
            results = self.pipeline(text[:2000], truncation=True, max_length=512)
            result = results[0]
            return SentimentScore(label=result['label'], score=result['score'])
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return SentimentScore(label="error", score=0.0)

# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
