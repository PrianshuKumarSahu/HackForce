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
- [ ] **Kochi Metro AI Fleet Operations & Chart Optimization Platform** (`vibe/vivian-kochi-metro` by @Vivian with Antigravity)
  - Dual-ML Failure Prediction & Station Crowding Engine.
  - CP-SAT Resilience Schedule Optimizer & ML Chart Evaluator (Efficiency %).
  - Real-Time Chart Efficiency Degradation Monitor & "What-If" Simulator.
  - Closed-Loop Feedback & Explainable AI Supervisor Console.

### 📋 Backlog (Pick up & claim a task below!)
- [ ] **Frontend Foundation / UI Shell**: Set up Next.js / Vite / Tailwind UI layout.
- [ ] **Backend Server / API Routes**: Set up server framework (Express / FastAPI / Hono).
- [ ] **Database & Authentication**: Schema design, ORM setup (Prisma / Drizzle / Supabase), and Auth routes.
- [ ] **DevOps & CI/CD**: GitHub Actions build & test workflow.

---

## 3. Shared API Endpoint & Type Contracts

> **AI Tool Note**: Add any shared TypeScript interfaces, Zod schemas, or REST/GraphQL routes here so other team members' AI tools do not invent conflicting signatures.

```typescript
// Kochi Metro Data Interfaces:
export interface TrainHealthMetrics {
  trainId: string; // e.g. "KM-101"
  brakeWearPct: number;
  hvacPressurePsi: number;
  doorCycles: number;
  mileageKm: number;
  pastDelayCount: number;
  subsystemFailureRisk: {
    brakes: number;
    doors: number;
    hvac: number;
    traction: number;
  };
  overallHealthScore: number; // 0 - 100
  failureProbabilityNextDay: number; // 0.0 - 1.0
  consequenceScore: number;
}

export interface ChartEvaluationResult {
  chartId: string;
  expectedEfficiencyPct: number; // e.g. 94.2
  failureProbabilityPct: number; // e.g. 5.8
  expectedDelayMinutes: number;
  reserveAdequacy: 'High' | 'Medium' | 'Low';
  confidenceScorePct: number;
  recommendedTrains: string[];
  standbyTrains: string[];
  maintenanceTrains: string[];
}

// Active Kochi Metro Endpoints:
// GET  /api/kochi/trains/health     -> TrainHealthMetrics[]
// GET  /api/kochi/chart/evaluate    -> ChartEvaluationResult
// POST /api/kochi/chart/optimize    -> Optimized Schedule Proposal
// POST /api/kochi/simulate/whatif   -> Disruption Simulation Result
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
