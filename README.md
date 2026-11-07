# Confam

See [CLAUDE.md](CLAUDE.md), [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md).

## Status

Built so far: the verdict contract (`packages/contract`) and a stub engine with the
rule-1 regression test (`services/engine`).

## TODO (not yet in the repo)

- `docs/ARCHITECTURE.md` and `confam-ui/` prototype: not supplied yet. Backend and UI work that needs them is marked `TODO(ARCHITECTURE.md)`.
- `apps/web`, `services/api` (`POST /v1/checks`), `services/worker`, `packages/i18n`, `eval/`, docker-compose.
- Port the real Python engine into `services/engine` (the current code is a stub).
