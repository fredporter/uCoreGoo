# uCore-Google

Google Workspace cloud bridge and DreamBeans daily briefing extension for the uDos ecosystem.

## Purpose & Scope

This extension connects the sovereign uCore runtime with personal Google services and daily autonomous planning:

- **DreamBeans Daily Briefing:** Synthesizes calendar schedules, unread inbox priorities, and personal goals into actionable morning task beans linked directly into `app.flow`.
- **Truth in Reporting:** Clearly distinguishes local staging from remote upload status (`locally_recorded` vs `remote_upload: pending/synced`).
- **Drive & Vault Sync:** Bidirectional document mirror contracts between local `~/Vault` and Google Drive.
- **Gemini & Gems Integration:** Thin-slice route contracts for Gemini multimodal models and Google Gems.
- **OAuth Scope Governance:** Explicit local token storage and scope boundaries fail closed when unauthenticated.

## Repository Structure

```text
/
├── udos_google/
│   └── src/
│       ├── contracts.py
│       ├── routes.py
│       └── service.py
├── tests/
│   └── test_google_bridge.py
├── pyproject.toml
├── package.json
└── README.md
```

## Run Tests

```bash
python3 -m unittest discover
```
