# Vasilisa Admin — clean Worker

This is a standalone Cloudflare Worker-style admin panel. It does not use `env.ASSETS`, React, npm, or a build step.

Required Cloudflare bindings/secrets:
- D1 binding: `DB` -> `vasilisa-db`
- Secret `ADMIN_USER`
- Secret `ADMIN_PASSWORD`
- Secret `SESSION_SECRET`

The worker creates the small required D1 tables automatically if they do not exist.
