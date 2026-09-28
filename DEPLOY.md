# Deploy

1. Put `_worker.js` in the root of the Pages/Workers project.
2. Remove old worker files so there is only one active `_worker.js`.
3. Keep D1 binding `DB` -> `vasilisa-db`.
4. Keep secrets `ADMIN_USER`, `ADMIN_PASSWORD`, `SESSION_SECRET`.
5. No build command is required.
6. Open `/login`.

The worker returns its own HTML and does not call `env.ASSETS`, so it is independent of a static-assets configuration.
