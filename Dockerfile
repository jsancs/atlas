FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --frozen

# Create a test file to verify file listing
RUN touch /app/DOCKER_CONTAINER_ACTIVE.txt

# Default command to run the agent
CMD ["uv", "run", "atlas", "serve", "--name", "container-agent", "--redis-url", "redis://redis:6379/0"]
