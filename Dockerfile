FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Go
RUN wget https://go.dev/dl/go1.22.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz && \
    rm go1.22.5.linux-amd64.tar.gz

# Set Go environment variables
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/root/go
ENV PATH=$PATH:$GOPATH/bin

# Clone XSS-Automation
RUN git clone https://github.com/dirtycoder0124/XSS-Automation.git /opt/XSS-Automation && \
    chmod +x /opt/XSS-Automation/xss_automation.sh

# Install Go tools
RUN go install github.com/tomnomnom/waybackurls@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/hahwul/dalfox/v2@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY README.md .

# Set environment variables
ENV XSS_SCRIPT_PATH=/opt/XSS-Automation/xss_automation.sh
ENV RESULTS_DIR=/opt/XSS-Automation/results

# Create results directory
RUN mkdir -p /opt/XSS-Automation/results

# Expose port (for web services, though bot doesn't need it)
EXPOSE 5000

# Run the bot
CMD ["python", "src/bot_main.py"]

