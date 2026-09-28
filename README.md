# Vasilisa Admin — D1 compatible
Upload `_worker.js` as the only runtime file in the Cloudflare Pages/Worker project.
Required bindings:
- D1 binding: `DB` -> `vasilisa-db`
- `ADMIN_USER`
- `ADMIN_PASSWORD`
- `SESSION_SECRET` may remain configured; this version does not require it for basic sessions.

Important: this version never assumes a `booking_date` column. It reads the existing bookings table dynamically and supports common date/time column names. Do not recreate the existing D1 database.
