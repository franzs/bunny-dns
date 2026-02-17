# bunnydns

[![PyPI version](https://badge.fury.io/py/bunnydns.svg)](https://pypi.org/project/bunnydns/)
[![Tests](https://github.com/franzs/bunnydns/actions/workflows/tests.yaml/badge.svg)](https://github.com/franzs/bunnydns/actions/workflows/tests.yaml)
[![Documentation](https://readthedocs.org/projects/bunnydns/badge/?version=latest)](https://bunnydns.readthedocs.io)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://github.com/franzs/bunnydns?tab=GPL-3.0-1-ov-file)

A Python SDK for the [Bunny.net  DNS API](https://docs.bunny.net/api-reference/core/dns-zone/).

## Installation

```bash
pip install bunnydns
```

## Quick Start

```Python
#!/usr/bin/env python3

from bunnydns import BunnyDNS, DnsRecordInput, RecordType

client = BunnyDNS(access_key="your-api-key")

# List all zones
zones = client.list_dns_zones()
for zone in zones.items:
    print(zone.domain)

# Create a zone
zone = client.add_dns_zone(domain="example.com")

# Add a record
record = client.add_dns_record(
    zone_id=zone.id,
    record=DnsRecordInput(
        type=RecordType.A,
        name="www",
        value="1.2.3.4",
        ttl=300,
    ),
)

# Export zone file
zone_file = client.export_dns_zone(zone_id=zone.id)

# Enable DNSSEC
ds = client.enable_dnssec(zone_id=zone.id)
print(ds.ds_record)
```

## Documentation

Full documentation is available at https://franzs.github.io/bunnydns/.

## License

GPL License. See [LICENSE](https://github.com/franzs/bunnydns?tab=GPL-3.0-1-ov-file) for details.
