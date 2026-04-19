FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the rest of the project files
COPY . .

# Final sync to install the project itself
RUN uv sync --frozen

# Create a test file to verify file listing
RUN touch /app/DOCKER_CONTAINER_ACTIVE.txt

# Default environment variables
ENV AGENT_NAME="container-agent"
ENV REDIS_URL="redis://redis:6379/0"

# Default command to run the agent
CMD ["sh", "-c", "uv run atlas serve --name ${AGENT_NAME} --redis-url ${REDIS_URL}"]
