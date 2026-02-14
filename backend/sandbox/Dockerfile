FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir backtrader pandas matplotlib

COPY executor.py .

# Entry point expecting strategy code to be mounted or passed
CMD ["python", "executor.py"]
