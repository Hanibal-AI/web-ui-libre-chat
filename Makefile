# See Docs/roadmap.md Phase 1. Convenience wrappers around docker compose
# for local development of the LibreChat ↔ Locker bundle.

.PHONY: dev-run dev-shell dev-logs

# Brings up the full stack (locker, mongodb, librechat), rebuilding
# locker from source if ../locker changed.
dev-run:
	docker compose up -d --build

# Opens an interactive shell in the librechat container. Not locker: its
# image is distroless/shell-less by design (see ../locker/Dockerfile),
# so there is nothing to exec into there.
dev-shell:
	docker compose exec librechat sh

# Follows logs for every service. Pass SERVICE to follow just one, e.g.
#   make dev-logs SERVICE=locker
dev-logs:
	docker compose logs -f $(SERVICE)
