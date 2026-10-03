# Vasilisa Admin — upload photos

The Gallery / Before & After section accepts image files directly from a phone photo library or computer. No URL is needed. The browser resizes photos before upload. Existing D1 database and bindings are preserved.

## Deploy
Replace the existing `_worker.js` in the `vasilisa_admin` GitHub repository with this one and commit to `main`. Keep the existing D1 binding `DB` and secrets `ADMIN_USER`, `ADMIN_PASSWORD`, `SESSION_SECRET`. Wait for the Cloudflare Pages deployment to finish, then open `/login`.

Note: photos are stored as compressed image data in the existing gallery table. For very large galleries, Cloudflare R2 object storage is preferable, but it requires a separate R2 binding.
