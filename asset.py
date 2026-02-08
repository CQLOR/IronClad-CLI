from typing import Optional, Any

class Asset:
    def __init__(self, *args, **kwargs):
        self.asset_id: str = kwargs.get("asset_id")
        self.hostname: str = kwargs.get("hostname", "")
        self.ip_address: Optional[str] = kwargs.get("ip_address")
        self.os: Optional[str] = kwargs.get("os")
        self.environment: Optional[str] = kwargs.get("environment")
        self.owner_context: Optional[str] = kwargs.get("owner_context")
        self.source: str = kwargs.get("source", "")
        self.raw: dict[str, Any] = kwargs.get("raw", {})

    def matches(self, query: str) -> bool:
        q = query.lower()
        values = [
            self.asset_id,
            self.hostname,
            self.ip_address or "",
            self.os or "",
            self.environment or "",
            self.owner_context or "",
            self.source,
        ]
        
        return any(q in str(v).lower() for v in values)
    
    def summary(self) -> str:
        return (
            f"[{self.source}] {self.hostname} "
            f"ip={self.ip_address or 'n/a'} os={self.os or 'n/a'} "
            f"env={self.environment or 'n/a'} owner={self.owner_context or 'n/a'}"
        )
    
    def __str__(self):
        return self.summary()