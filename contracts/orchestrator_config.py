from typing import Optional


class Webhook:
    name: str = None
    url: str = None
    api_token: Optional[str] = None


class Outbox:
    concurrency: int = 10
    batch_size: int = 50
    item_delay: float = 0.02
    long_batch_delay: float = 10.0
    batch_delay: float = 2.0
    max_submissions_per_minute: int = 1500


class OrchestratorConfig:
    application_name: str = None
    base_url: str = None
    outbox: Outbox = Outbox()
    default_callback_webhook: Optional[Webhook] = None
    use_simulator: bool = False
    require_https: bool = False