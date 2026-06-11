FROM python:3.11-slim

WORKDIR /app

# Copy everything the build needs (hatchling reads pyproject + README)
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# stdio by default (MCP introspection / local clients).
# Hosted deployments (Railway etc.) override via WANDER_TRANSPORT=streamable-http + PORT.
ENV WANDER_TRANSPORT=stdio

EXPOSE 8000

CMD ["python", "-m", "wander_agent.server"]
