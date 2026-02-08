from typing import Any
from asset import Asset
import requests
import os

from config import CROWDSTRIKE_API_URL, NETBOX_API_URL, QUALYS_API_URL, DEFAULT_API_KEY


class InventorySource:
    name: str = "base"

    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch_raw(self):
        headers = {
            "X-API-Key": os.environ.get("IRONCLAD_API_KEY") or DEFAULT_API_KEY
        }
        r = requests.get(self.api_url, headers=headers, timeout=10)
        if r.status_code != 200:
            raise RuntimeError(f"{self.name} fetch failed ({r.status_code}): {r.text[:200]}")
        data = r.json()
        if not isinstance(data, list):
            raise RuntimeError(f"{self.name} returned unexpected JSON (expected list).")
        return data

    def normalize(self, record: dict[str, Any]) -> Asset:
        raise NotImplementedError
    
    def fetch_assets(self) -> list[Asset]:
        raw = self.fetch_raw()
        results = []
        for each_record in raw:
            results.append(self.normalize(each_record))

        return results
    
# NetBox adapter - maps NetBox API records to our internal Asset model.
class NetboxInventorySource(InventorySource):
    name = "netbox"

    def normalize(self, record: dict[str, Any]) -> Asset:
        # TODO: Map NetBox schema fields based on your preview output.
        # Suggested schema fields (from your Mockaroo design):
        # id, device_name, primary_ip, platform, environment, tenant, ...
        return Asset(
            asset_id=str(record.get("id")),                 # TODO confirm key
            hostname=str(record.get("device_name")),        # TODO confirm key
            ip_address=record.get("primary_ip"),            # TODO confirm key
            os=record.get("platform"),                      # TODO confirm key
            environment=record.get("environment"),          # TODO confirm key
            owner_context=record.get("tenant"),             # TODO confirm key
            source=self.name,
            raw=record,
        )
    
#Qualys adapter - maps Qualys API records to our internal Asset model.
class QualysInventorySource(InventorySource):
    name = "qualys"

    def normalize(self, record: dict[str, Any]) -> Asset:
        # TODO: Map Qualys schema fields based on your preview output.
        # Suggested schema fields:
        # asset_id (UUID), hostname, ip_address, operating_system, asset_group, criticality, ...
        return Asset(
            asset_id=str(record.get("asset_id")),           # TODO confirm key
            hostname=str(record.get("hostname")),           # TODO confirm key
            ip_address=record.get("ip_address"),            # TODO confirm key
            os=record.get("operating_system"),              # TODO confirm key
            environment=record.get("asset_group"),          # TODO map group -> environment
            owner_context=None,                             # TODO if your schema has owner/team, map it
            source=self.name,
            raw=record,
        )
    

# CrowdStrike adapter - maps CrowdStrike API records to our internal Asset model.
class CrowdstrikeInventorySource(InventorySource):
    name = "crowdstrike"

    def normalize(self, record: dict[str, Any]) -> Asset:
        # TODO: Map crowdstrike schema fields based on your preview output.
        # Suggested schema fields:
        # sensor_id, hostname, local_ip, os_version, logged_in_user, policy_applied, ...
        return Asset(
            asset_id=str(record.get("sensor_id")),          # TODO confirm key
            hostname=str(record.get("hostname")),           # TODO confirm key
            ip_address=record.get("local_ip"),              # TODO choose local_ip as primary
            os=record.get("os_version"),                    # TODO confirm key
            environment=None,                               # TODO if you have env-like field, map it
            owner_context=record.get("logged_in_user"),     # TODO confirm key
            source=self.name,
            raw=record,
        )
    
def quick_test():
    sources = {
        "netbox": NetboxInventorySource(NETBOX_API_URL),
        "qualys": QualysInventorySource(QUALYS_API_URL),
        "crowdstrike": CrowdstrikeInventorySource(CROWDSTRIKE_API_URL),
    }

    for name, src in sources.items():
        assets = src.fetch_assets()
        print(f"\n{name}: pulled {len(assets)} assets")
        # This will grab the first 3 elements out of `assets`. Feel free to change to `[:1]` or `[:2]` or any other number you want to get different quantities of assets
        for a in assets[:3]:
            print(" ", a.summary())


if __name__ == "__main__":
    quick_test()