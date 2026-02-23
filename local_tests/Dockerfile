FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy test files
COPY . .

# Default command
CMD ["pytest", "-v", "--html=report.html", "--self-contained-html"]
