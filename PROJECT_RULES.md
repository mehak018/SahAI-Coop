# SahAI-Coop Project Rules

SIH Problem Statement ID: 26088
Project: Multilingual Cooperative Governance & Legal Assistance Chatbot

## Team ownership
- Member 1: `frontend/` — branch `frontend`
- Member 2: `backend/` and `database/` — branch `backend`
- Member 3: `ai-engine/` — branch `ai-engine`

## Collaboration rules
1. Work only in your assigned folders.
2. Do not edit another member's implementation files.
3. Treat `shared/`, root configuration, `.github/`, and integration tests as shared/protected.
4. Get team approval before changing shared files or API contracts.
5. Agree on API request/response contracts before integration.
6. Use mocks while dependent modules are unfinished.
7. Test each module independently before opening a pull request.
8. Push work to the assigned branch; integrate into `main` through reviewed pull requests.
9. Never commit secrets, API keys, passwords, or real `.env` files.
10. Inspect existing files before modifying them; do not restructure without approval.

## Branches
- `main`: integrated project
- `frontend`: Member 1
- `backend`: Member 2
- `ai-engine`: Member 3
