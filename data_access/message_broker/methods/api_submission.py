from orchestrator_sdk.contracts.publishing.publish_envelope import PublishEnvelope
from orchestrator_sdk.seedworks.logger import Logger

import json
import httpx
from typing import Any, Optional

logger = Logger.get_instance()


class ApiSubmission:
    def __init__(
        self,
        application_name: Optional[str] = None,
        verify_ssl: bool = False,
        timeout_seconds: float = 60.0,
    ):
        self._application_name = application_name.strip().lower() if application_name else None

        headers = {
            "Content-Type": "application/json"
        }

        # Add once at client level (safe because it's static per instance)
        if self._application_name:
            headers["X-Application-Name"] = self._application_name

        self._client = httpx.AsyncClient(
            verify=verify_ssl,
            timeout=timeout_seconds,
            headers=headers,
            limits=httpx.Limits(
                max_keepalive_connections=100,
                max_connections=200
            ),
        )

        self._disposed = False

    def get_json_data(self, publish_request: Any):
        if isinstance(publish_request, dict):
            return publish_request
        elif isinstance(publish_request, str):
            # if string already JSON, return parsed object when possible
            try:
                return json.loads(publish_request)
            except Exception:
                return publish_request
        else:
            return json.loads(publish_request.model_dump_json())

    async def submit(self, publish_request: PublishEnvelope):
        try:
            json_data = self.get_json_data(publish_request.publish_request)

            http_response = await self._client.post(
                publish_request.endpoint,
                json=json_data
            )

            if not http_response.is_success:
                raise Exception(
                    f"Failed to post on behalf of [{publish_request.handler_name}] "
                    f"to [{publish_request.endpoint}] with ErrorCode "
                    f"[{http_response.status_code}]. Error Details >> {http_response.text}"
                )

            logger.trace(
                f"Successfully posted on behalf of [{publish_request.handler_name}] "
                f"to the orchestrator - reference [{publish_request.reference}]"
            )

        except Exception as ex:
            logger.error(ex)
            raise

    async def dispose(self):
        if not self._disposed:
            await self._client.aclose()
            self._disposed = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.dispose()