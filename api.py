import redis
from chat import *
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_DB = os.environ.get("REDIS_DB", 0)
redis_store = redis.StrictRedis(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_DB))  # type: ignore

@app.route("/sunbird-assistant/answer", methods=["GET"])
@cross_origin()
def ask_assistant():
    """
    Ask Sunbird Assistant a question.

    Args:
        q: question
        session_id: session id

    Returns:
        str: answer
    """
    question = request.args.get("q")
    session_id = request.args.get("session_id", "default")
    system_message = format_system_message()
    messages = read_messages_from_redis(session_id, redis_store)
    search_results = search_documents(question)  # Implement your search function in chat.py
    user_message = format_user_message(
        question, search_results, max_tokens=1024
    )  # Token management
    message_payload = create_message_payload(
        user_message, system_message, messages, max_tokens=2048
    )
    answer = get_answer(messages=message_payload, model="gpt-3.5", max_tokens=1024, temperature=0.7)
    redis_store = redis.StrictRedis(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_DB))
    assistant_message = format_assistant_message(answer)
    messages = read_messages_from_redis(session_id, redis_store)
    messages.extend([user_message, assistant_message])
    store_messages_in_redis(session_id, messages, redis_store)
    return Response(answer, mimetype="text/plain")

if __name__ == "__main__":
    app.run(port=8088, debug=True)
