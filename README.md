# Atlas Agent

Atlas is an AI agent framework with built-in Redis orchestration for cross-machine communication.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your environment:
   Copy the `.env.example` file to `.env` and fill in your API keys and configurations.
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings (e.g., your OpenAI API key):
   ```env
   OPENAI_API_KEY=your_key_here
   ATLAS_MODEL=openai:gpt-4o
   REDIS_URL=redis://localhost:6379/0
   ```
   When running `docker compose`, variables defined in your `.env` file (if present in the same directory as the `docker-compose` file) will be automatically picked up for environment variable substitution. This means you do not need to `export` them manually if they are in your `.env` file.

## Usage

### Interactive Chat
Start a local interactive session:
```bash
uv run atlas chat
```

### Redis-Based Orchestration

Atlas agents can communicate asynchronously via Redis Streams.

#### 1. Start a Redis Server
Make sure you have a Redis server running. You can use Docker:
```bash
docker run -d -p 6379:6379 redis
```

#### 2. Start an Agent in Service Mode
Run an agent that listens for tasks on a specific Redis stream:
```bash
uv run atlas serve --name worker-1
```

#### 3. Send a Message to the Agent
From another terminal (or another machine connected to the same Redis), send a request:
```bash
uv run atlas send --to worker-1 --msg "List the files in the current directory"
```

The agent will process the request using its tools and send the response back via its own Redis stream.

### Running Master and Worker Nodes

To run the Redis master services:
```bash
docker compose -f docker-compose.master.yml up -d
```

To run an Atlas agent worker, connecting to the master Redis:
```bash
# Ensure OPENAI_API_KEY is set in your environment
export OPENAI_API_KEY="your_openai_api_key"
docker compose -f docker-compose.worker.yml up -d
```

To stop the services:
```bash
docker compose -f docker-compose.master.yml down
docker compose -f docker-compose.worker.yml down
```

## Architecture

- **Messaging**: Uses Redis Streams for reliable, asynchronous message passing.
- **Agent Framework**: Built on `pydantic-ai`.
- **Schema**:
  - `source`: Originating agent/client ID.
  - `user`: User context ID.
  - `destination`: Target agent ID.
  - `msg`: Content payload.

## Development

### Testing
```bash
uv run pytest
```
