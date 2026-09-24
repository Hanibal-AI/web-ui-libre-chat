# Locker Web UI — LibreChat Bundle

A docker-compose bundle that wires [LibreChat](https://github.com/danny-avila/LibreChat) — an open source, self-hosted chat interface — to [Locker](https://github.com/Hanibal-AI/locker), the open source PII-masking proxy for LLM APIs.

`docker compose up` gets you a real, familiar ChatGPT-style interface where every prompt is automatically screened for PII (emails, phone numbers, IBANs, names, organizations, locations...) before it ever reaches the LLM provider — and transparently restored in the response.

## Why this repo exists

Locker on its own is a proxy: you can `curl` it, but you can't *see* it working. This bundle makes Locker's PII masking demonstrable and testable through a real chat experience, matching the product vision described in [`../synthese-produit.md`](../synthese-produit.md) (§7 "Expérience salarié & démo commerciale", §12 "MVP commercialisable"): *"Bundle type docker-compose : chat-ui + proxy-go."*

## Status

Early planning stage — see [Docs/roadmap.md](Docs/roadmap.md) for what's built and what's next. There is no `docker-compose.yml` yet.

## Relationship to other repos

- [`locker`](../locker) — the core PII-masking proxy this bundle points LibreChat at.
- The Control Plane / SaaS dashboard described in the product vision (`../synthese-produit.md` §5, §12) is a separate, future repository, out of scope here.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
