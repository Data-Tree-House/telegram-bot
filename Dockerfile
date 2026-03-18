# Multi-stage build for minimal Telegram bot image
# Stage 1: Builder - install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
# Install uv for faster dependency resolution and installation
RUN pip install --no-cache-dir uv
# Copy only dependency files first (better layer caching)
COPY pyproject.toml ./
# Install dependencies to a virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache .

# Stage 2: Runtime - minimal final image
FROM python:3.12-slim
WORKDIR /app
# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
# Copy application code
COPY bot.py .
# Set PATH to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"
# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser
# BOT_TOKEN can be passed at runtime:
# docker run -e BOT_TOKEN=your_token_here <image>
CMD ["python", "bot.py"]
