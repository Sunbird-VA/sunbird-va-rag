### Libraries ###
import os
import zlib
import openai
import pickle

openai.api_key = os.environ.get("OPENAI_API_KEY")

### Cache Management ###
def read_json_from_redis(redis_key, redis_conn):
    """Read a JSON object from Redis, given a key."""
    compressed_json = redis_conn.get(redis_key)
    if compressed_json is None:
        return []
    else:
        pickled_json = zlib.decompress(compressed_json)
        return pickle.loads(pickled_json)

def read_messages_from_redis(session_id, redis_conn):
    """Read messages from Redis, given a session ID."""
    redis_key = f"messages:{session_id}"
    return read_json_from_redis(redis_key, redis_conn)

def store_json_in_redis(json_obj, redis_key, redis_conn, ttl=60 * 60 * 12):
    """Store a JSON object in Redis, with a default TTL of 12 hours."""
    pickled_json = pickle.dumps(json_obj)
    compressed_json = zlib.compress(pickled_json)
    redis_conn.setex(redis_key, ttl, compressed_json)

def store_messages_in_redis(session_id, messages, redis_conn):
    """Store messages in Redis, given a session ID."""
    redis_key = f"messages:{session_id}"
    store_json_in_redis(messages, redis_key, redis_conn)

### Token Counting ###
def count_tokens_str(doc, model="gpt-3.5"):
    """Count tokens in a string.
    Args:
        doc (str): String to count tokens for.
    Returns:
        int: number of tokens in the string
    """
    encoder = tiktoken.encoding_for_model(model)  # type: ignore
    return len(encoder.encode(doc, disallowed_special=()))

def count_tokens(messages):
    """
    Counts tokens in a list of messages.
    Args:
        messages (list): list of messages to count tokens for
    Returns:
        int: number of tokens in the list of messages
    """
    num_tokens = 0
    for message in messages:
        num_tokens += 4
        for key, value in message.items():
            num_tokens += count_tokens_str(value)
            if key == "name":
                num_tokens += -1
    num_tokens += 2
    return num_tokens

### Formatting ###
def get_prompt(prompt_file, prompt_dir="prompts"):
    """Load a prompt from a file.

    Args:
        prompt_file (str): Name of the prompt file.
        prompt_dir (str, optional): Path to the prompt directory. Defaults to 'assets/prompts'.

    Returns:
        str: prompt
    """
    prompt_path = os.path.join(prompt_dir, prompt_file)
    return open(prompt_path, "r", encoding="utf-8").read()

def format_system_message() -> dict:
    """Formats the system message

    Returns:
        dict: formatted system message
    """
    return {"role": "system", "content": get_prompt("system.md")}

def format_assistant_message(a: str) -> dict:
    """Formats the assistant message
    Args:
        a (str, optional): assistant's reply.
    Returns:
        dict: formatted assistant message
    """
    return {"role": "assistant", "content": a}

def format_user_message(question, document_list=[], max_tokens=1280):
    """Formats the user message upto a maximum number of tokens.

    Args:
        question (str): question to search
        documents (list): list of documents to format
    Returns:
        dict: formatted system message
    """
    if len(document_list) == 0:
        doc_string = "No documents found"
    else:
        total_tokens = 0
        selected_docs = []
        for docs in document_list:
            for doc in docs:
                total_tokens += count_tokens_str(doc)
                if total_tokens > max_tokens:
                    break
                else:
                    selected_docs.append(doc)
            selected_docs.append("\n\n")
        doc_string = "".join(selected_docs)
    user_prompt = f"Question: {question}\n\nDocuments:\n\n{doc_string}"
    return {"role": "user", "content": user_prompt}

def search_documents(question: str, limit: int = 5) -> list:
    """Implement your own vector search here.
    Args:
        question (str): question to search
        limit (int, optional): number of documents to return. Defaults to 5.
    Returns:
        list: list of documents

    NOTE: This is a placeholder function. You should implement your own vector search here.
    Some choices:
        - https://www.pinecone.io/
        - https://weaviate.io/
        - https://www.langchain.com/
        - https://www.llamaindex.ai/
        - https://marqo.pages.dev/
    """
    return list(str)

def create_message_payload(user_message, system_message, messages=[], max_tokens=3000):
    """Get the message history for the conversation.
    Args:
        user_message (dict): user message
        system_message (dict): system message
        messages (list, optional): list of messages to include in the message history. Defaults to [].
        max_tokens (int, optional): Maximum number of tokens to limit the message history to. Defaults to 3000.
    Returns:
        list: message payload
    """
    message_history = []
    total_tokens = 0
    system_token_count = count_tokens([system_message])
    max_tokens -= system_token_count  # subtract the system prompt tokens
    if len(user_message) > 0:
        messages = messages + [user_message]
    else:
        messages = messages
    for message in reversed(messages):
        message_tokens = count_tokens([message])
        if total_tokens + message_tokens <= max_tokens:
            total_tokens += message_tokens
            message_history.insert(0, message)
        else:
            break
    message_history.insert(0, system_message)
    return message_history

def get_answer(**kwargs):
    """Completes the chat given a list of messages.

    Args:
        messages (list): list of messages to complete the chat with
        **kwargs: additional arguments to pass to the OpenAI API, such as
            temperature, max_tokens, etc.
    Returns:
        str: the chat completion
    """
    response = openai.ChatCompletion.create(**kwargs)
    return response.choices[0]["message"]["content"]
