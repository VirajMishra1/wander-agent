FROM python:3.11-slim

WORKDIR /app

# Install uv for fast installs
RUN pip install --no-cache-dir uv

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock* ./

# Install package and dependencies (no dev extras)
RUN uv pip install --system -e . --no-cache

# Copy source
COPY src/ ./src/

# Default to streamable-http for Claude.ai compatibility
ENV WANDER_TRANSPORT=streamable-http
ENV PORT=8000

EXPOSE 8000

CMD ["python", "-m", "wander_agent.server"]
