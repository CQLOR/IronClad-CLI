from inventory_source import InventorySource
from asset import Asset

class InventoryManager:
    def __init__(self, sources: dict[str, InventorySource]):
        self.sources = sources
        self.assets: list[Asset] = []

    def pull(self, source: str) -> None:
        self.assets.clear()
        if source == "all":
            for src in self.sources.values():
                self.assets.extend(src.fetch_assets())
        else:
            if source not in self.sources:
                raise ValueError(f"Unknown source: {source}")
            self.assets.extend(self.sources[source].fetch_assets())

    def list_assets(self, source: str = "all") -> list[Asset]:
        if source == "all":
            return list(self.assets)
        return [a for a in self.assets if a.source == source]

    def search(self, query: str, source: str = "all") -> list[Asset]:
        return [a for a in self.list_assets(source) if a.matches(query)]

    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {"total": len(self.assets)}
        for a in self.assets:
            counts[a.source] = counts.get(a.source, 0) + 1
        return counts