# CLAUDE.md

Public Claude plugins, served as one plugin marketplace, `aleos`. How it is installed is in `README.md`; these are the operating rules.

This file is `CLAUDE.md`, not `AGENTS.md`, on purpose: contributors' setups are unknown, and every Claude Code version and setup reads `CLAUDE.md`.

## Rules

- Everything here is public. Never add personal material, or anything copied from a private repository that isn't a plugin cleaned for publishing.
- No top-level `bin/` in a plugin: claude.ai refuses to install one. A skill's scripts live in its own `scripts/`.
- Renaming or removing a plugin means adding `"old": "new"`, or `"old": null`, to `renames` in `.claude-plugin/marketplace.json`. The map is append-only history.
- Run `claude plugin validate .` before committing.
