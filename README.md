# IronClad Unified Inventory CLI

A unified inventory management tool that aggregates assets from multiple sources: NetBox, Qualys, and CrowdStrike.

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- `pip` and `venv` (usually included with Python)

### Quick Start

1. **Clone or navigate to the project directory:**
```bash
cd "IronClad CLI"
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Verify installation:**
```bash
python3 main.py --help
```

You should see the CLI help output with all available subcommands.

### Deactivate Virtual Environment

When finished, deactivate the venv:
```bash
deactivate
```

## Schema Mapping Notes

This section documents how fields from each data source are mapped to the internal `Asset` model.

### NetBox Mapping

NetBox provides IT infrastructure inventory data. The following fields are mapped:

| NetBox Field | Asset Property | Notes |
|---|---|---|
| `id` | `asset_id` | Device unique identifier |
| `device_name` | `hostname` | Device hostname |
| `primary_ip` | `ip_address` | Primary IP address |
| `platform` | `os` | Operating system/platform type |
| `environment` | `environment` | Deployment environment (dev, staging, prod) |
| `tenant` | `owner_context` | Organizational tenant/owner |
| (entire record) | `raw` | Raw API response stored for reference |

**Example:** `web-752` (NetBox) → `[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR`

### Qualys Mapping

Qualys provides vulnerability and asset scanning data. The following fields are mapped:

| Qualys Field | Asset Property | Notes |
|---|---|---|
| `asset_id` | `asset_id` | Asset UUID from Qualys |
| `hostname` | `hostname` | Asset hostname/FQDN |
| `ip_address` | `ip_address` | IP address scanned |
| `operating_system` | `os` | Detected operating system |
| `asset_group` | `environment` | Qualys asset group (mapped to environment) |
| (unmapped) | `owner_context` | Not provided by Qualys API |
| (entire record) | `raw` | Raw API response stored for reference |

**Example:** `photobucket.com` (Qualys) → `[qualys] photobucket.com ip=230.30.154.87 os=Windows Server 2019 env=Production owner=n/a`

### CrowdStrike Mapping

CrowdStrike provides endpoint detection and response (EDR) data. The following fields are mapped:

| CrowdStrike Field | Asset Property | Notes |
|---|---|---|
| `sensor_id` | `asset_id` | Sensor/endpoint unique identifier |
| `hostname` | `hostname` | Endpoint hostname |
| `local_ip` | `ip_address` | Local/primary IP address of endpoint |
| `os_version` | `os` | Operating system version |
| (unmapped) | `environment` | Not provided by CrowdStrike API |
| `logged_in_user` | `owner_context` | Currently logged-in user context |
| (entire record) | `raw` | Raw API response stored for reference |

**Example:** `yahoo.co.jp` (CrowdStrike) → `[crowdstrike] yahoo.co.jp ip=224.215.182.42 os=macOS Ventura env=n/a owner=otown0`

## Usage

### List all assets from a source

```bash
python3 main.py list --source netbox
python3 main.py list --source qualys
python3 main.py list --source crowdstrike
python3 main.py list --source all
```

### Challenge B — Filters on list

Filter results by operating system, environment, or owner:

```bash
# Filter by OS (substring match, case-insensitive)
python3 main.py list --source netbox --os Linux
python3 main.py list --source all --os "Windows"

# Filter by environment
python3 main.py list --source netbox --environment prod
python3 main.py list --source all --environment staging

# Filter by owner
python3 main.py list --source netbox --owner Engineering
python3 main.py list --source all --owner HR

# Combine multiple filters
python3 main.py list --source all --os Linux --environment prod --owner Engineering
```

### Challenge C — Output formats

Display results in table (default) or JSON format:

```bash
# Default table format
python3 main.py list --source netbox --format table
python3 main.py search --query "photobucket" --format table

# JSON format (useful for scripting/parsing)
python3 main.py list --source netbox --format json
python3 main.py search --query "Linux" --format json > assets.json
python3 main.py find-ip --ip "10.0" --format json | jq '.[] | select(.environment == "prod")'
```

### Challenge D — Find by IP

Search for assets by IP address (substring match):

```bash
python3 main.py find-ip --ip "147.149"
python3 main.py find-ip --ip "10.0.0" --source netbox
python3 main.py find-ip --ip "192.168" --format json
```

### Search assets by keyword

Search across all asset properties (hostname, IP, OS, environment, owner, source):

```bash
python3 main.py search --query "photobucket" --source all
python3 main.py search --query "Linux" --source netbox
python3 main.py search --query "Windows" --limit 10
```

### Pull inventory and show statistics

```bash
python3 main.py pull --source all
python3 main.py stats --source qualys
```

## Output Format

All assets display using a consistent summary format:

```
[source] hostname ip=<ip_or_n/a> os=<os_or_n/a> env=<environment_or_n/a> owner=<owner_or_n/a>
```

Examples:
- `[netbox] web-752 ip=147.149.196.21 os=Windows env=dev owner=HR`
- `[qualys] photobucket.com ip=230.30.154.87 os=Windows Server 2019 env=Production owner=n/a`
- `[crowdstrike] yahoo.co.jp ip=224.215.182.42 os=macOS Ventura env=n/a owner=otown0`

## Implementation Notes

- **Source field:** All assets include the `source` identifier (`netbox`, `qualys`, or `crowdstrike`)
- **Default values:** Missing fields display as `n/a` in the summary
- **Search:** The search function matches case-insensitively across all asset properties
- **API Key:** Uses `IRONCLAD_API_KEY` environment variable or built-in default key
