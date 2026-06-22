import json
import redis
from app.config import settings


class RedisSessionMemory:
    def __init__(self):
        self.redis_url = settings.redis_url
        self._client = None
        self._fallback_memory = {}

    @property
    def client(self):
        """Lazy load redis client to avoid early connection exceptions."""
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def get_history(self, session_id: str) -> list[dict]:
        """Fetch chat history list from Redis, fallback to in-memory dict if fails."""
        try:
            data = self.client.get(f"arogya:session:{session_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            # Fallback to local memory if Redis is down or unreachable
            print(f"[Memory] Redis lookup failed, using local fallback. Error: {e}")
            return self._fallback_memory.get(session_id, [])
        return []

    def add_message(self, session_id: str, role: str, content: str):
        """Append a message to the session's history and save it to Redis (expiry 24h)."""
        history = self.get_history(session_id)
        history.append({"role": role, "content": content})
        # Keep history under a reasonable limit to stay within model token constraints
        if len(history) > 20:
            history = history[-20:]

        try:
            self.client.set(
                f"arogya:session:{session_id}", json.dumps(history), ex=86400
            )
        except Exception as e:
            print(f"[Memory] Redis save failed, using local fallback. Error: {e}")
            self._fallback_memory[session_id] = history

    def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        try:
            self.client.delete(f"arogya:session:{session_id}")
        except Exception as e:
            print(f"[Memory] Redis delete failed. Error: {e}")
        if session_id in self._fallback_memory:
            del self._fallback_memory[session_id]


session_memory = RedisSessionMemory()
