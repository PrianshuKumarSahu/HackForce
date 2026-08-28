# CONTRIBUTING.md - Multi-AI Vibe Coding Git Workflow

This guide details the git rules for the **HackForce** group project where 6 contributors are vibe coding across multiple AI assistants.

---

## 🌿 1. Branch Strategy

Never commit directly to `main`! Always work on a feature branch.

### Branch Naming Pattern:
`vibe/<your-name>-<short-feature-description>`

Examples:
- `vibe/vivian-project-setup`
- `vibe/alex-user-auth`
- `vibe/sam-dashboard-ui`

---

## 📝 2. Commit Message Standard

Include the AI tool tag in commit messages so the team knows which AI was used:

### Commit Format:
`<type>(<scope>): [vibe:<ai-tool>] <description>`

Examples:
- `feat(setup): [vibe:antigravity] add multi-ai workflow infrastructure`
- `feat(auth): [vibe:cursor] add login component and JWT handling`
- `fix(api): [vibe:claude] resolve database connection timeout`

---

## 🔄 3. Daily Vibe Coding Loop

1. **Pull Latest Main**:
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Create / Switch to Feature Branch**:
   ```bash
   git checkout -b vibe/<your-name>-<feature>
   ```
3. **Prompt Your AI Assistant**:
   - Ask your AI assistant to read `AGENTS.md` and `VIBE_LOG.md`.
4. **Update `VIBE_LOG.md`**:
   - Register your active branch and any new shared types/routes.
5. **Push & Open Pull Request**:
   ```bash
   git push origin vibe/<your-name>-<feature>
   ```
   - Open a PR on GitHub using the provided PR template.
