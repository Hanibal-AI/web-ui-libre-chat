# Version Pins

Decided as part of `Docs/roadmap.md` Phase 0.2. This bundle pins every image explicitly, for reproducible deployments — see the rationale below for each one. Revisit this file whenever bumping a version.

## LibreChat

**Pinned:** `ghcr.io/danny-avila/librechat:v0.8.7`

**Not** `registry.librechat.ai/danny-avila/librechat-dev:latest`, even though that's what LibreChat's own official `docker-compose.yml` uses (verified against the `v0.8.7` git tag on 2026-09-24). That image has **no version-pinned tags at all** — only `:latest` resolves; `:v0.8.7` returns `manifest unknown` on that registry. Since reproducibility is the whole point of pinning, we use the `ghcr.io/danny-avila/librechat` image instead, where `:v0.8.7` and `:latest` currently resolve to the same digest (confirmed via `docker manifest inspect`), i.e. `v0.8.7` genuinely is the tagged release.

`v0.8.7` was the latest non-release-candidate tag at the time of this decision (`v0.8.8-rc1..rc4` existed but were pre-releases).

## MongoDB (required by LibreChat)

**Pinned:** `mongo:8.0.20`

Matches the version pinned in LibreChat's own official `docker-compose.yml` at the `v0.8.7` tag — no reason to diverge here since it's already reproducibly pinned upstream.

## Meilisearch, pgvector, RAG API

**Not included** in this bundle (see `Docs/roadmap.md` Phase 1.2: "Meilisearch/RAG API only if kept"). This bundle's only goal is demonstrating Locker's PII masking through a chat UI — conversation search and retrieval-augmented generation aren't needed for that, and dropping them keeps the compose stack smaller and faster to start. If a future phase needs them, upstream's pins at the time of writing were `getmeili/meilisearch:v1.35.1` and `pgvector/pgvector:0.8.0-pg15-trixie`.

## Admin panel

**Not included.** LibreChat's official compose also bundles `registry.librechat.ai/clickhouse/librechat-admin-panel:latest` (itself unpinned, same issue as the main app image). Out of scope — this bundle is a demo/test harness for Locker, not a LibreChat administration deployment.

## Locker

**Not yet pinned — tracking `main`.** `locker` (`../locker`) has not cut a tagged release yet (`git tag -l` is empty as of this writing; its Phase 7 goreleaser pipeline is built and validated but has never run against a real `git tag` push, so no image has been published to `ghcr.io/hanibal-ai/locker`). Until a first tag exists, this bundle must build Locker from source (`../locker`'s own `Dockerfile`) rather than pull a versioned image.

**Action when `locker` cuts its first tag** (e.g. `v0.1.0`): switch this bundle to `ghcr.io/hanibal-ai/locker:v0.1.0` and update this file plus `docker-compose.yml` (once it exists) together, in the same change.
