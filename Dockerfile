FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg with additional codecs
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install latest youtube-dl binary and make it executable
RUN wget -O /usr/local/bin/youtube-dl https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp && \
    chmod a+rx /usr/local/bin/youtube-dl

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY bot.py .

# Create downloads directory with proper permissions
RUN mkdir -p downloads && chmod 777 downloads

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]
