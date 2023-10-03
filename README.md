
# Sunbird Virtual Assistant (Sunbird VA)

Sunbird VA RAG is a Flask-based chat API that utilizes LLMs for generating responses and using Vector Search for document retrieval.
The application also integrates with Redis for message history caching and supports dynamic message formatting.

## Features

1. Flask-based REST API server.
2. OpenAI integration for chat completions.
3. Redis integration for storing and retrieving session-based message histories.
4. Token counting for managing API requests.
5. Custom message formatting to control user and assistant interactions.

## Requirements

- Python 3.x
- Flask
- openai
- tiktoken
- redis
- flask_cors
- zlib
- pickle

## Setup & Configuration

1. Set up a virtual environment and install dependencies.
2. Configure the following environment variables:
   - `REDIS_HOST`: Host for your Redis instance. Default is `localhost`.
   - `REDIS_PORT`: Port for your Redis instance. Default is `6379`.
   - `REDIS_DB`: Database index for your Redis instance. Default is `0`.
   - `OPENAI_API_KEY`: Your OpenAI API key.

To enable search capabilities, implement the vector search function in the `search_documents` function placeholder. You may use any vector search library of your choice.

## Usage

To run the server:

```bash
python api.py
```

Then, you can access the chat API endpoint at:

```
GET /sunbird-assistant/answer?q=[YOUR_QUESTION]&session_id=[OPTIONAL_SESSION_ID]
```

## Endpoints

- **`/sunbird-assistant/answer`** (GET)
  - Params:
    - `q`: The question you want to ask the Sunbird Assistant.
    - `session_id`: (Optional) Session ID for maintaining chat history. Default is "default".
  - Returns: Assistant's answer as plain text.
