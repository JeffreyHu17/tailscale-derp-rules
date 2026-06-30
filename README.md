# Tailscale DERP Rules

Daily generated Clash/Mihomo rule-provider for Tailscale public DERP servers.

Source DERP map:

```text
https://login.tailscale.com/derpmap/default
```

Use the generated rule-provider at the top of your Clash/Mihomo rules:

```yaml
rule-providers:
  tailscale-derp:
    type: http
    behavior: classical
    url: "https://raw.githubusercontent.com/JeffreyHu17/tailscale-derp-rules/main/rules/tailscale-derp.yaml"
    path: ./ruleset/tailscale-derp.yaml
    interval: 86400

rules:
  - RULE-SET,tailscale-derp,DIRECT
```

The workflow runs every day at `04:10` Asia/Shanghai time and can also be run
manually from GitHub Actions.
