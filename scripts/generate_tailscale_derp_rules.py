import ipaddress
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DERP_MAP_URL = "https://login.tailscale.com/derpmap/default"
OUTPUT_PATH = Path("rules/tailscale-derp.yaml")


def quote_yaml(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def append_unique(rules: list[str], seen: set[str], rule: str) -> None:
    if rule in seen:
        return
    seen.add(rule)
    rules.append(rule)


def load_derp_map() -> dict:
    with urllib.request.urlopen(DERP_MAP_URL, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def build_rules(derp_map: dict) -> list[str]:
    rules: list[str] = []
    seen: set[str] = set()

    for region in derp_map.get("Regions", {}).values():
        for node in region.get("Nodes", []):
            host = node.get("HostName")
            ipv4 = node.get("IPv4")
            ipv6 = node.get("IPv6")

            if host:
                append_unique(rules, seen, f"DOMAIN,{host},DIRECT")

            if ipv4:
                ipaddress.IPv4Address(ipv4)
                append_unique(rules, seen, f"IP-CIDR,{ipv4}/32,DIRECT,no-resolve")

            if ipv6:
                ipaddress.IPv6Address(ipv6)
                append_unique(rules, seen, f"IP-CIDR6,{ipv6}/128,DIRECT,no-resolve")

    return rules


def write_rule_provider(rules: list[str]) -> None:
    if not rules:
        raise RuntimeError("empty Tailscale DERP rule list")

    updated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Tailscale DERP DIRECT rules for Clash/Mihomo rule-provider",
        f"# Source: {DERP_MAP_URL}",
        f"# Updated: {updated_at}",
        f"# Count: {len(rules)}",
        "payload:",
    ]
    lines.extend(f"  - {quote_yaml(rule)}" for rule in rules)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_rule_provider(build_rules(load_derp_map()))


if __name__ == "__main__":
    main()
