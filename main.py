import requests
import os
import json
from typing import Any, List
from inventory_source import NetboxInventorySource, QualysInventorySource, CrowdstrikeInventorySource
from inventory_manager import InventoryManager
from config import NETBOX_API_URL, QUALYS_API_URL, CROWDSTRIKE_API_URL
from asset import Asset
import argparse


def filter_assets(assets: List[Asset], os_filter: str = None, env_filter: str = None, owner_filter: str = None) -> List[Asset]:
    """Filter assets by OS, environment, or owner (case-insensitive)."""
    result = assets
    if os_filter:
        os_lower = os_filter.lower()
        result = [a for a in result if a.os and os_lower in a.os.lower()]
    if env_filter:
        env_lower = env_filter.lower()
        result = [a for a in result if a.environment and env_lower in a.environment.lower()]
    if owner_filter:
        owner_lower = owner_filter.lower()
        result = [a for a in result if a.owner_context and owner_lower in a.owner_context.lower()]
    return result


def format_assets(assets: List[Asset], fmt: str = "table") -> None:
    """Format and print assets in the specified format."""
    if fmt == "json":
        data = []
        for a in assets:
            data.append({
                "asset_id": a.asset_id,
                "hostname": a.hostname,
                "ip_address": a.ip_address,
                "os": a.os,
                "environment": a.environment,
                "owner_context": a.owner_context,
                "source": a.source,
            })
        print(json.dumps(data, indent=2))
    else:  # table (default)
        for a in assets:
            print(a.summary())


def build_manager() -> InventoryManager:
    sources = {
        "netbox": NetboxInventorySource(NETBOX_API_URL),
        "qualys": QualysInventorySource(QUALYS_API_URL),
        "crowdstrike": CrowdstrikeInventorySource(CROWDSTRIKE_API_URL),
    }
    return InventoryManager(sources)


def cmd_pull(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    s = mgr.stats()
    print("Pulled inventory.")
    print("Stats:", s)


def cmd_list(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)  # simple: list always pulls fresh
    assets = mgr.list_assets(args.source)
    # Apply filters
    assets = filter_assets(assets, args.os, args.environment, args.owner)
    # Format and display
    format_assets(assets, args.format)


def cmd_search(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    results = mgr.search(args.query, args.source)
    print(f"Results: {len(results)}")
    format_assets(results[:args.limit], args.format)


def cmd_stats(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    print("Stats:", mgr.stats())


def cmd_find_ip(args) -> None:
    mgr = build_manager()
    mgr.pull(args.source)
    assets = mgr.list_assets(args.source)
    results = [a for a in assets if a.ip_address and args.ip in a.ip_address]
    print(f"Results for IP {args.ip}: {len(results)}")
    format_assets(results, args.format)


def main():
    p = argparse.ArgumentParser(prog="ironclad-inventory", description="Ironclad Unified Inventory CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_pull = sub.add_parser("pull", help="Pull inventory from a source")
    p_pull.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_pull.set_defaults(func=cmd_pull)

    p_list = sub.add_parser("list", help="List assets")
    p_list.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_list.add_argument("--os", dest="os", help="Filter by operating system (substring match)")
    p_list.add_argument("--environment", dest="environment", help="Filter by environment (substring match)")
    p_list.add_argument("--owner", dest="owner", help="Filter by owner (substring match)")
    p_list.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Search assets by keyword")
    p_search.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=50)
    p_search.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_search.set_defaults(func=cmd_search)

    p_stats = sub.add_parser("stats", help="Show counts by source")
    p_stats.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_stats.set_defaults(func=cmd_stats)

    p_find_ip = sub.add_parser("find-ip", help="Find assets by IP address")
    p_find_ip.add_argument("--ip", required=True, help="IP address to search for (substring match)")
    p_find_ip.add_argument("--source", choices=["netbox", "qualys", "crowdstrike", "all"], default="all")
    p_find_ip.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    p_find_ip.set_defaults(func=cmd_find_ip)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main() 