# Locker Web UI — LibreChat Bundle

162.19.241.44:3080 # test url 

A docker-compose bundle that wires [LibreChat](https://github.com/danny-avila/LibreChat) — an open source, self-hosted chat interface — to [Locker](https://github.com/Hanibal-AI/locker), the open source PII-masking proxy for LLM APIs.

`docker compose up` gets you a real, familiar ChatGPT-style interface where every prompt is automatically screened for PII (emails, phone numbers, IBANs, names, organizations, locations...) before it ever reaches the LLM provider — and transparently restored in the response.

## Why this repo exists

Locker on its own is a proxy: you can `curl` it, but you can't *see* it working. This bundle makes Locker's PII masking demonstrable and testable through a real chat experience, matching the product vision described in [`../synthese-produit.md`](../synthese-produit.md) (§7 "Expérience salarié & démo commerciale", §12 "MVP commercialisable"): *"Bundle type docker-compose : chat-ui + proxy-go."*

## Status

`docker-compose.yml` is up and wired (LibreChat ↔ Locker, see `Docs/roadmap.md` Phase 1) — see [Docs/roadmap.md](Docs/roadmap.md) for what's built and what's next, and [Docs/versions.md](Docs/versions.md) for the exact image versions this bundle pins (and why).

## Development

```bash
cp .env.example .env   # then fill in OPENAI_API_KEY and the LibreChat secrets (see comments in the file)
make dev-run            # docker compose up -d --build — brings up locker, mongodb, and librechat
```

LibreChat is then at `http://localhost:3080`, Locker at `http://localhost:8080` (override the host port with `LOCKER_HOST_PORT` in `.env` if that's already taken).

Other targets:

```bash
make dev-logs                   # follow logs for every service
make dev-logs SERVICE=locker    # follow logs for just one (locker, mongodb, or librechat)
make dev-shell                  # open a shell inside the librechat container
```

`dev-shell` targets `librechat`, not `locker` — Locker's image is [distroless](https://github.com/GoogleContainerTools/distroless) and has no shell at all, by design (see `../locker/Dockerfile`). To debug Locker, use `make dev-logs SERVICE=locker`; it never logs request/response bodies or API keys (see `../locker/SECURITY.md`), so PII/secrets won't show up there even in verbose output — to see what Locker actually sends upstream you need to inspect it on the provider side, or point it at a local test double.

These `make` targets are thin wrappers around `docker compose` — see `Makefile`; run the equivalent `docker compose` commands directly if you don't have `make`.

## Relationship to other repos

- [`locker`](../locker) — the core PII-masking proxy this bundle points LibreChat at.
- The Control Plane / SaaS dashboard described in the product vision (`../synthese-produit.md` §5, §12) is a separate, future repository, out of scope here.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
