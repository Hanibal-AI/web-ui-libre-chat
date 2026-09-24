# Locker Web UI (LibreChat Bundle) — Roadmap

## Scope

This roadmap covers the docker-compose bundle that wires [LibreChat](https://github.com/danny-avila/LibreChat) — an open source, self-hosted chat interface — to [Locker](https://github.com/Hanibal-AI/locker) (`../locker`), the open source PII-masking proxy. The goal is a `docker compose up` demo where anyone can chat through a real, familiar interface and watch PII masking work live, instead of only being able to `curl` the proxy.

This directly implements steps 1–3 of the MVP order described in `../synthese-produit.md` §12 ("Brancher une Chat UI sur Locker", "Valider masquage + streaming SSE bout en bout", "Paquet Compose + install.sh") and the "Web UI Chat" brick described in §2 and §7 of that document. It does **not** include the Control Plane / SaaS dashboard (§12 step 4, §5 "Enterprise / Control Plane") — that is out of scope for this repository, planned as a separate, future one.

The plan is organized as sequential phases, each with concrete steps as checkboxes and a checkable deliverable. Check items off as work is completed so this file always reflects where the project actually stands.

---

## Phase 0 — Repository Foundations

**Goal:** a clean, documented repository anyone can clone and understand before any compose file exists.

- [x] **0.1 Repository setup**
  - `LICENSE` (Apache 2.0, matching `locker`), this roadmap, `README.md`.
  - `.gitignore` (env files with real secrets, LibreChat's local data volumes, `dist`/`bin`-style build leftovers if any tooling is added later).
- [x] **0.2 Version pins**
  - Decide and document which LibreChat image tag and which Locker image tag (`ghcr.io/hanibal-ai/locker`, published by `locker`'s own Phase 7 release pipeline) this bundle targets, and how that gets bumped over time.
  - Documented in `Docs/versions.md`. LibreChat: `ghcr.io/danny-avila/librechat:v0.8.7` — deliberately *not* the official compose file's `registry.librechat.ai/danny-avila/librechat-dev:latest`, which has no version-pinned tags at all (verified via `docker manifest inspect`: `:v0.8.7` doesn't exist on that registry, only `:latest`). MongoDB: `mongo:8.0.20`, matching LibreChat's own upstream pin. Locker: **not yet pinned** — `locker` has no tagged release yet (`git tag -l` is empty), so this bundle will build it from source until a first tag exists; switching to a pinned `ghcr.io/hanibal-ai/locker` image is a one-line follow-up once one does.
- [x] **0.3 Deliverable** — repository exists, documented, ready for Phase 1.
  - `LICENSE`, `README.md`, `Docs/roadmap.md`, `Docs/versions.md`, `.gitignore` all in place; git repository initialized (`main` branch).

---

## Phase 1 — LibreChat ↔ Locker Wiring

**Goal:** get LibreChat to send every chat request through Locker instead of directly to a provider.

- [ ] **1.1 Research LibreChat's custom endpoint mechanism**
  - Unlike Open WebUI's simple `OPENAI_API_BASE_URL` environment variable, LibreChat routes a non-default OpenAI-compatible backend through its **Custom Endpoints** feature (a `librechat.yaml` config file), not a top-level env var swap. Document this explicitly — it's a real setup difference from the "Open WebUI / LibreChat" framing used interchangeably in `../synthese-produit.md`, and the reason this repo exists separately from a hypothetical Open WebUI bundle.
  - Confirm streaming (SSE) is supported end-to-end through a LibreChat custom endpoint, since Locker's own PII-unmasking-in-streaming work (`locker` Phase 2/5) only matters if the UI actually streams.
- [ ] **1.2 docker-compose skeleton**
  - Services: `librechat` (plus whatever it requires to run — MongoDB at minimum; Meilisearch/RAG API only if kept), `locker` (pulled from `ghcr.io/hanibal-ai/locker`).
  - `librechat.yaml` custom endpoint definition pointing its `baseURL` at `http://locker:8080/v1`.
  - `.env.example` listing every required variable: the LLM provider API key Locker needs, LibreChat's own required secrets (JWT/session signing keys), Mongo connection string.
- [ ] **1.3 First successful message round-trip**
  - `docker compose up`, send one plain (no-PII) message in the LibreChat UI, confirm the response comes back correctly and streams token-by-token.
- [ ] **1.4 Deliverable** — a working chat conversation in LibreChat, proxied through Locker, with zero PII in play yet. This proves the wiring, not yet the masking.

---

## Phase 2 — PII Masking & Streaming Validation (the actual demo)

**Goal:** reproduce the exact demo script from `../synthese-produit.md` §7 through the real UI, not just `curl`.

- [ ] **2.1 Manual test protocol**
  - A documented list of prompts to type into LibreChat (an email, a phone number, an IBAN, a "name + organization + location" sentence for the NER layer) and what to check: Locker's logs show the placeholder (`[EMAIL_1]`, `[PERSON_1]`, ...), never the raw value; the UI shows the original value correctly restored in the assistant's reply.
- [ ] **2.2 Streaming-specific check**
  - A prompt long enough to stream over multiple SSE chunks, confirming a placeholder split across chunks (hardened in `locker` Phase 2/5) still resolves correctly when watched live in the UI, not only in `locker`'s own automated test suite.
- [ ] **2.3 Record the demo**
  - A short recorded walkthrough or step-by-step screenshots for `README.md` / sales use, matching `../synthese-produit.md` §7's "démo type": *prompt avec PII → logs proxy montrant `[EMAIL_1]` côté LLM → (dashboard audit côté SaaS is out of scope here)*.
- [ ] **2.4 Deliverable** — documented, reproducible proof that a real user typing PII into a real chat UI never leaks it to the LLM provider, with the UI still showing a normal, un-degraded conversation.

---

## Phase 3 — Packaging & Quickstart Polish

**Goal:** match the "ready in ~5 minutes" promise repeated across `../synthese-produit.md` and `locker`'s own `Docs/initial.md`.

- [ ] **3.1 `install.sh`**
  - Prompts for the LLM provider API key(s) Locker needs, writes `.env`, runs `docker compose up -d`. No license key here — that's Enterprise/Control Plane territory, out of scope for this repository.
- [ ] **3.2 README quickstart**
  - Copy-pasteable, as few commands as possible, matching `locker`'s own `CONTRIBUTING.md` quickstart style.
- [ ] **3.3 Health/readiness checks**
  - `depends_on` with `condition: service_healthy` for `locker` and MongoDB in `docker-compose.yml`, so `docker compose up` doesn't race LibreChat against a not-yet-ready proxy or database.
- [ ] **3.4 Deliverable** — a first-time user with just Docker installed and an LLM provider API key goes from `git clone` to a working, PII-masking chat UI in under 5 minutes, no manual troubleshooting.

---

## Phase 4 — Beyond MVP (future, not currently scheduled)

- Multi-provider switcher in the LibreChat UI (Anthropic/Mistral), once that's meaningful per-request rather than a single proxy-wide `locker` deployment config.
- Automated end-to-end test (e.g. Playwright) driving the real UI and asserting on Locker's logs, replacing the Phase 2 manual protocol.
- White-labeling / branding (matching `../synthese-produit.md` §7's `https://ia.entreprise.com` vision) — likely Enterprise/Control Plane territory; noted here only as a boundary marker, not planned in this repository.

---

## Summary Timeline (indicative, not committed dates)

| Phase | Focus | Depends on |
|---|---|---|
| 0 | Repository foundations | — |
| 1 | LibreChat ↔ Locker wiring | 0, `locker` Phase 7 (published image) |
| 2 | PII masking & streaming validation | 1 |
| 3 | Packaging & quickstart polish | 1, 2 |
| 4 | Beyond MVP (future) | 3 |
