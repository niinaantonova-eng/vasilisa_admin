# Vasilisa Admin — photo upload + visible error fix

Photo upload accepts image files from a phone gallery or computer. Navigation renders immediately; if loading data fails, the admin shows the actual API error instead of a blank page.

Replace only `_worker.js` in the existing `vasilisa_admin` GitHub repository. Keep the existing D1 binding `DB` and secrets unchanged.
