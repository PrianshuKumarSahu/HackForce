# AGENTS.md - Master AI Collaboration & Vibe Coding Guidelines

Welcome AI Assistants (Antigravity, Cursor, Claude Code, Windsurf, Copilot, ChatGPT, Bolt, v0, etc.)!
This repository is being built by a team of **6 human contributors vibe coding simultaneously** using different AI tools.

To ensure zero merge conflicts, zero broken imports, and clean concurrent development, **EVERY AI ASSISTANT WORKING ON THIS REPOSITORY MUST FOLLOW THESE RULES**.

---

## 1. Core Operating Principles for AI Agents

1. **READ `VIBE_LOG.md` BEFORE GENERATING CODE**
   - Check `VIBE_LOG.md` to find:
     - Which team member owns which module/folder.
     - Active feature branches currently in progress.
     - Shared API contracts, TypeScript interfaces, and database schemas.
   - Do NOT edit files or modules assigned to another team member without explicit user instruction.

2. **SCOPED MUTATIONS ONLY**
   - Keep all code changes strictly within your user's assigned feature directory.
   - Do not make global edits, refactor shared utilities, or modify root setup files unless authorized.

3. **SHARED TYPE REGISTRY**
   - When creating or modifying data structures, API requests/responses, or database models, log them in `VIBE_LOG.md` under **Shared Type & API Contracts**.
   - Always export clear TypeScript interfaces/types so other AI agents can consume them cleanly without guessing.

4. **ZERO PLACEHOLDERS & REAL LOGIC**
   - Do not leave empty `// TODO: implement this` or dummy mock fallbacks in shared files.
   - Ensure exported functions have full parameter types and valid return signatures.

5. **BRANCH & COMMIT DISCIPLINE**
   - Remind the user to work on a dedicated branch named `vibe/<developer>-<feature>` (e.g. `vibe/vivian-auth`).
   - Format git commits with `[vibe:<ai-tool-name>]` (e.g. `feat(auth): [vibe:antigravity] implement JWT login route`).

---

## 2. Team Folder & Ownership Boundaries

| Module / Directory | Primary Owner | Assigned AI Tool | Status |
| :--- | :--- | :--- | :--- |
| `apps/web` or `src/frontend` | TBD | TBD | Unassigned |
| `apps/api` or `src/backend` | TBD | TBD | Unassigned |
| `packages/db` or `src/db` | TBD | TBD | Unassigned |
| `docs/` | Shared | All | Open |

*(Update this matrix in `VIBE_LOG.md` as team members pick up modules!)*

---

## 3. Pre-Commit Checklist for AI Tools

Before completing a response or pushing changes:
- [ ] Are all new files inside your assigned module folder?
- [ ] Did you update `VIBE_LOG.md` with any new exported types, API routes, or environment variables?
- [ ] Did you run tests or linting checks if available?
- [ ] Are all imports relative or using declared workspace aliases (`@/components/...`)?
