# VIBE_LOG.md - Real-Time Team Task & AI Contract Registry

> **Instructions for Humans & AI Agents**: 
> Update this document whenever you begin a new feature branch, define a new API endpoint/type, or finish a task. Every AI tool reading this repo uses this file to coordinate cross-feature logic.

---

## 1. Team Ownership Matrix (6 Collaborators)

| # | Developer | Role / Module | AI Tool Used | Active Branch | Status |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Vivian | Lead / Infrastructure & Setup | Antigravity | `vibe/vivian-setup` | 🟢 Active |
| 2 | Teammate 2 | *Unassigned* | *Cursor / Claude / etc.* | `vibe/member2-feature` | 🟡 Waiting |
| 3 | Teammate 3 | *Unassigned* | *Tool* | `vibe/member3-feature` | 🟡 Waiting |
| 4 | Teammate 4 | *Unassigned* | *Tool* | `vibe/member4-feature` | 🟡 Waiting |
| 5 | Teammate 5 | *Unassigned* | *Tool* | `vibe/member5-feature` | 🟡 Waiting |
| 6 | Teammate 6 | *Unassigned* | *Tool* | `vibe/member6-feature` | 🟡 Waiting |

---

## 2. Active Feature Roadmap & Task Board

### 🚀 In Progress
- [x] **Repository & Multi-AI Infrastructure** (`vibe/vivian-setup` by @Vivian with Antigravity)
  - Created `AGENTS.md`, `VIBE_LOG.md`, `.cursorrules`, `CLAUDE.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`.

### 📋 Backlog (Pick up & claim a task below!)
- [ ] **Frontend Foundation / UI Shell**: Set up Next.js / Vite / Tailwind UI layout.
- [ ] **Backend Server / API Routes**: Set up server framework (Express / FastAPI / Hono).
- [ ] **Database & Authentication**: Schema design, ORM setup (Prisma / Drizzle / Supabase), and Auth routes.
- [ ] **Core Feature Module A**: Primary business logic / app feature.
- [ ] **Core Feature Module B**: Secondary feature / integration module.
- [ ] **DevOps & CI/CD**: GitHub Actions build & test workflow.

---

## 3. Shared API Endpoint & Type Contracts

> **AI Tool Note**: Add any shared TypeScript interfaces, Zod schemas, or REST/GraphQL routes here so other team members' AI tools do not invent conflicting signatures.

```typescript
// Shared Type Registry Example:
export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: string;
}

// Active API Endpoints:
// GET /api/v1/health -> { status: "ok", timestamp: string }
```

---

## 4. Environment Variables Registry

> List all required `.env` variables (without secret values) here so teammates know what keys are needed:

```env
# Required Environment Keys:
# PORT=3000
# DATABASE_URL=
# NEXT_PUBLIC_API_URL=
```
