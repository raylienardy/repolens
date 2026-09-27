import json
import logging
from datetime import datetime, timezone
import httpx

from app.ai.schemas import AIExplanation, AIResult
from app.analysis.schemas import AnalysisResult

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://9router.com/v1"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TIMEOUT_SECONDS = 60
MAX_ERROR_BODY_CHARS = 300


class NineRouterProvider:
    """OpenAI-compatible chat completions client for 9Router.

    Never performs I/O in __init__. Errors are returned as AIResult with
    status="error" instead of raising, so callers can degrade gracefully.
    """

    name = "9router"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout
        self._transport = transport
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.timeout,
                transport=self._transport,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _sanitize(self, message: str) -> str:
        """Strip secret material and cap length before surfacing to caller."""
        text = message
        if self.api_key and self.api_key in text:
            text = text.replace(self.api_key, "***redacted***")
        if len(text) > MAX_ERROR_BODY_CHARS:
            text = text[:MAX_ERROR_BODY_CHARS] + "...[truncated]"
        return text

    def _error(self, message: str, detail: str | None = None) -> AIResult:
        full = f"{message}: {detail}" if detail else message
        return AIResult(
            status="error",
            provider=self.name,
            model=self.model,
            explanation=None,
            error_message=self._sanitize(full),
            generated_at=datetime.now(timezone.utc),
        )

    def _parse_explanation(self, content: str) -> AIExplanation:
        text = content.strip()
        if text.startswith("```"):
            # strip markdown fences
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        return AIExplanation.model_validate(json.loads(text))

    async def generate_explanation(
        self, analysis: AnalysisResult, prompt: str
    ) -> AIResult:
        if not self.api_key:
            return self._error("AI_API_KEY is not configured for provider '9router'")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Kamu membantu menjelaskan repository GitHub berdasarkan fakta. "
                        "Jawab hanya dengan JSON valid sesuai skema yang diminta."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        client = self._get_client()
        try:
            resp = await client.post("/chat/completions", json=payload)
        except httpx.HTTPError as exc:
            logger.warning("9router request failed: %s", type(exc).__name__)
            return self._error("Request to 9router failed", type(exc).__name__)

        if resp.status_code >= 400:
            return self._error(
                f"9router returned HTTP {resp.status_code}", resp.text
            )

        try:
            data = resp.json()
        except ValueError:
            return self._error("9router returned a non-JSON response body")

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return self._error("9router response missing 'choices[0].message.content'")

        if not content or not content.strip():
            return self._error("9router returned empty completion content")

        try:
            explanation = self._parse_explanation(content)
        except (ValueError, TypeError) as exc:
            return self._error("9router completion did not match AIExplanation schema", str(exc))

        usage = data.get("usage") or {}
        return AIResult(
            status="ok",
            provider=self.name,
            model=data.get("model") or self.model,
            explanation=explanation,
            generated_at=datetime.now(timezone.utc),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )
