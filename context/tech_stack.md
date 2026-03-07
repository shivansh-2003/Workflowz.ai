# workflowz.ai — Tech Stack

---

## Overview

Full-stack monorepo. Next.js 15 frontend (marketing site + app), FastAPI backend (existing), PostgreSQL database. AI pipeline runs on LangGraph + Ollama. All new UI is TypeScript-first, dark-mode default.

```
workflowz_ai/
├── app/                  # Existing FastAPI backend (Python)
├── workflowz-ui/         # Existing Streamlit UI (to be replaced)
├── workflowz-web/        # NEW — Next.js 15 marketing site + app
├── context/              # Design & planning docs
└── CLAUDE.md
```

---

## Frontend — Marketing Site + App UI

### Core Framework

| Package | Version | Role |
|---------|---------|------|
| `next` | 15.x | App Router, RSC, SSR, image optimization |
| `react` | 19.x | UI rendering |
| `react-dom` | 19.x | DOM renderer |
| `typescript` | 5.x | Type safety throughout |

**Why Next.js 15:** App Router enables per-route layouts (marketing vs app shell), RSC for zero-JS static sections, built-in `next/font` for Clash Display/Geist, `next/image` for WebP/AVIF.

---

### Styling

| Package | Version | Role |
|---------|---------|------|
| `tailwindcss` | 4.x | Utility classes, design tokens |
| `@tailwindcss/typography` | latest | Prose styling for docs/blog |
| `clsx` | latest | Conditional class merging |
| `tailwind-merge` | latest | Merge without conflicts |

**CSS Variables:** All design tokens (`--bg-void`, `--accent-cyan`, etc.) defined in `globals.css`, consumed via Tailwind's `theme()` and raw CSS.

---

### Component Library

| Package | Version | Role |
|---------|---------|------|
| `shadcn/ui` | latest | Headless, fully customizable base components |
| `@radix-ui/react-*` | latest | Unstyled primitives under shadcn (dialog, dropdown, tabs…) |
| `lucide-react` | latest | Consistent stroke-1.5 icon set |
| `class-variance-authority` | latest | Variant-based component APIs (used by shadcn) |

**Theme:** `new-york` style, `zinc` base, CSS variables on. Override with workflowz dark palette in `globals.css`.

**Key components in use:**

```
Button      Card        Badge       Dialog
Sheet       Table       Tabs        Toggle
Input       Textarea    Form        NavigationMenu
DropdownMenu  Tooltip   Avatar      Separator
Progress    ScrollArea  Skeleton    Switch
```

---

### 3D & WebGL

| Package | Version | Role |
|---------|---------|------|
| `three` | 0.170.x | 3D renderer — hero shader, 3D kanban |
| `@types/three` | matching | TypeScript types |
| `@react-three/fiber` | 8.x | React bindings for Three.js |
| `@react-three/drei` | 9.x | Helpers: OrbitControls, Text, shaders |

**Scenes:**
- `HeroShader.tsx` — Neural graph GLSL fragment shader, mouse parallax, void→violet→cyan palette
- `KanbanScene.tsx` — Floating 3D board, animated card transitions, particle connectors

**Performance:** Both scenes are `dynamic(() => import(...), { ssr: false })` — load only when hero/feature section enters viewport.

---

### Smooth Scroll

| Package | Version | Role |
|---------|---------|------|
| `lenis` | 1.x | Buttery smooth scroll — the luxury feel |
| `@studio-freight/lenis` | (alias) | Scroll velocity, scroll-linked animations |

```ts
// LenisProvider.tsx — wraps entire app
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  wheelMultiplier: 0.8,
});
```

Initialized only after first user interaction. `requestAnimationFrame` loop synced with GSAP ticker if GSAP is used.

---

### Animation

| Package | Version | Role |
|---------|---------|------|
| `framer-motion` | 11.x | Page reveals, scroll-triggered, drawers, modals |
| `gsap` | 3.x | Timeline orchestration, ScrollTrigger (optional, for complex scenes) |
| `@gsap/react` | 2.x | GSAP React hooks |

**Framer Motion usage:**
- `variants` for staggered entrance animations (opacity, y, blur)
- `AnimatePresence` for modals, drawers, sheet transitions
- `useInView` hook for scroll-triggered section reveals

**GSAP usage** (optional, only if Framer Motion isn't enough):
- `ScrollTrigger` for pinned sticky sections (Problem/Solution)
- Timeline sequencing for complex hero entrance

---

### Text Effects

| Package | Source | Role |
|---------|--------|------|
| 21st.dev text components | copy-paste | `SplitText` — word-by-word staggered reveal |
| 21st.dev text components | copy-paste | `ScrambleText` — rotating hero taglines |
| Custom `GradientText` | in-house | `--gradient-cta` animated shift on brand name |
| Custom `CountUp` | in-house | Stat numbers animate 0 → value on scroll |

---

### Navigation & Background Effects

| Source | Component | Used In |
|--------|-----------|---------|
| 21st.dev | Glassmorphic Navbar | Global sticky nav |
| 21st.dev | Aurora Background | Final CTA section |
| 21st.dev | Animated Grid | Alternative hero bg fallback |
| 21st.dev | Particle Background | Optional section accent |

All 21st.dev components are copy-pasted into `components/effects/` and customized to match the workflowz token system — no runtime npm dependency.

---

### State Management

| Package | Version | Role |
|---------|---------|------|
| `zustand` | 5.x | Client UI state (sidebar open, active sprint, board filters) |
| `@tanstack/react-query` | 5.x | Server state, caching, background refetch |
| `@tanstack/react-query-devtools` | 5.x | Dev-only query inspector |

**Pattern:** TanStack Query for all API calls. Zustand for ephemeral UI state only (never server data).

---

### Forms & Validation

| Package | Version | Role |
|---------|---------|------|
| `react-hook-form` | 7.x | Performant, uncontrolled forms |
| `zod` | 3.x | Schema validation, shared with backend types |
| `@hookform/resolvers` | 3.x | Zod ↔ react-hook-form bridge |

---

### Drag & Drop (Kanban Board)

| Package | Version | Role |
|---------|---------|------|
| `@dnd-kit/core` | 6.x | Drag and drop engine |
| `@dnd-kit/sortable` | 7.x | Sortable lists (backlog, board columns) |
| `@dnd-kit/utilities` | 3.x | CSS transform helpers |

**Why dnd-kit:** Accessible, touch-friendly, no jQuery, works with `@react-three/fiber` canvas — unlike react-beautiful-dnd.

---

### Rich Text Editor (Issue Descriptions)

| Package | Version | Role |
|---------|---------|------|
| `@tiptap/react` | 2.x | Headless rich text editor |
| `@tiptap/starter-kit` | 2.x | Bold, italic, lists, code, headings |
| `@tiptap/extension-placeholder` | 2.x | Placeholder text |
| `@tiptap/extension-mention` | 2.x | `@mention` team members |

---

### Charts & Data Visualization

| Package | Version | Role |
|---------|---------|------|
| `recharts` | 2.x | Burndown chart, velocity bars, distribution |

Custom chart theme: `--bg-surface` background, `--accent-cyan` primary line, `--accent-violet` secondary, muted grid lines, no harsh borders.

---

### Date & Time

| Package | Version | Role |
|---------|---------|------|
| `date-fns` | 3.x | Date formatting, relative time, sprint date math |

---

### HTTP Client

| Package | Version | Role |
|---------|---------|------|
| `axios` | 1.x | API calls to FastAPI backend |
| `ky` | (alternative) | Lightweight fetch wrapper if axios is too heavy |

TanStack Query wraps all axios calls — no raw fetching in components.

---

### Fonts

Loaded via `next/font/local` or `next/font/google`. No layout shift.

| Font | Source | Used For |
|------|--------|---------|
| Clash Display | Local (fontsource) | Hero headlines, brand wordmark |
| Syne | Google Fonts | Section headers |
| Geist | Vercel (npm) | Body text, UI |
| Geist Mono | Vercel (npm) | Issue keys, code blocks |
| Space Mono | Google Fonts | Labels, ticker, small caps |

```ts
// app/layout.tsx
import { GeistSans, GeistMono } from 'geist/font';
import localFont from 'next/font/local';

const clashDisplay = localFont({
  src: '../public/fonts/ClashDisplay-Variable.woff2',
  variable: '--font-clash',
});
```

---

### Dev Tooling

| Package | Version | Role |
|---------|---------|------|
| `eslint` | 9.x | Linting |
| `eslint-config-next` | 15.x | Next.js rules |
| `prettier` | 3.x | Code formatting |
| `prettier-plugin-tailwindcss` | latest | Auto-sort Tailwind classes |
| `husky` | 9.x | Pre-commit hooks |
| `lint-staged` | latest | Run linters only on staged files |

---

### Analytics & Monitoring

| Tool | Role |
|------|------|
| PostHog | Product analytics, feature flags, A/B tests (self-hostable) |
| Plausible | Privacy-first page analytics (alternative / complement) |
| Sentry | Error tracking, performance monitoring |
| Vercel Analytics | Core Web Vitals, real-user monitoring (if deploying on Vercel) |

---

## Backend — FastAPI (Existing, Python)

| Package | Version | Role |
|---------|---------|------|
| `fastapi` | 0.115.x | Async web framework |
| `uvicorn` | 0.32.x | ASGI server |
| `sqlalchemy` | 2.x | Async ORM |
| `asyncpg` | 0.30.x | Async PostgreSQL driver |
| `alembic` | 1.x | Database migrations |
| `pydantic` | 2.x | Request/response validation |
| `pydantic-settings` | 2.x | Env var config |
| `python-jose` | 3.x | JWT encoding/decoding |
| `passlib[bcrypt]` | 1.x | Password hashing |
| `langchain` | 0.3.x | LLM orchestration |
| `langgraph` | 0.2.x | Agentic state machine |
| `langchain-ollama` | 0.2.x | Ollama LLM provider |
| `langfuse` | 2.x | LLM observability (optional) |
| `httpx` | 0.28.x | Async HTTP client |
| `python-dotenv` | 1.x | .env loading |
| `email-validator` | 2.x | Email format validation |

---

## Database

| Technology | Role |
|-----------|------|
| PostgreSQL 16 | Primary database |
| asyncpg | Async connection pool |
| SQLAlchemy 2.x | ORM (async session) |
| Alembic | Schema versioning & migrations |
| JSONB columns | AI workflow state persistence |

---

## AI / LLM Runtime

| Technology | Role |
|-----------|------|
| Ollama | Local LLM inference server |
| `gpt-oss:20b` (or configured model) | Default model |
| LangGraph | 7-stage agentic state machine |
| LangChain | Agent tooling, prompt templates |
| Langfuse | Prompt tracing, cost tracking (optional) |

---

## Infrastructure & Deployment

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend hosting | Vercel | Next.js-native, edge functions, preview deploys |
| Backend hosting | Railway / Render / Fly.io | FastAPI + Uvicorn container |
| Database | Supabase / Neon / Railway Postgres | Managed PostgreSQL |
| LLM runtime | Self-hosted Ollama | VM with GPU (optional), or swap to OpenAI-compatible API |
| File storage | Cloudflare R2 / S3 | Attachments, OG images |
| CDN | Vercel Edge / Cloudflare | Static assets, fonts |
| CI/CD | GitHub Actions | Lint → test → deploy on push to main |

---

## Environment Variables

### Frontend (`workflowz-web/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000      # FastAPI backend
NEXT_PUBLIC_APP_URL=http://localhost:3000      # Frontend base URL
NEXT_PUBLIC_POSTHOG_KEY=phc_...               # PostHog analytics
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_SENTRY_DSN=https://...@sentry.io/...
```

### Backend (`workflowz_ai/.env`)

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/workflowz
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Package.json (workflowz-web)

```json
{
  "name": "workflowz-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev --turbo",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "format": "prettier --write .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "lucide-react": "^0.400.0",
    "three": "^0.170.0",
    "@react-three/fiber": "^8.0.0",
    "@react-three/drei": "^9.0.0",
    "lenis": "^1.0.0",
    "framer-motion": "^11.0.0",
    "gsap": "^3.12.0",
    "@gsap/react": "^2.0.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.0.0",
    "@hookform/resolvers": "^3.0.0",
    "@dnd-kit/core": "^6.0.0",
    "@dnd-kit/sortable": "^7.0.0",
    "@dnd-kit/utilities": "^3.0.0",
    "@tiptap/react": "^2.0.0",
    "@tiptap/starter-kit": "^2.0.0",
    "@tiptap/extension-placeholder": "^2.0.0",
    "@tiptap/extension-mention": "^2.0.0",
    "recharts": "^2.0.0",
    "date-fns": "^3.0.0",
    "axios": "^1.0.0",
    "geist": "^1.0.0"
  },
  "devDependencies": {
    "@types/three": "^0.170.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@types/node": "^20.0.0",
    "@tanstack/react-query-devtools": "^5.0.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.6.0",
    "husky": "^9.0.0",
    "lint-staged": "^15.0.0"
  }
}
```

---

## Performance Budget

| Metric | Target | Strategy |
|--------|--------|---------|
| Initial JS (gzipped) | < 150 KB | Code splitting, dynamic imports |
| Three.js bundle | < 80 KB | Tree-shake, load on demand |
| Total page weight | < 2 MB | WebP/AVIF images, font subsetting |
| LCP | < 2.5s | RSC, static hero fallback |
| CLS | < 0.1 | `next/font`, aspect-ratio on media |
| INP | < 200ms | No layout thrash, passive listeners |
| Lighthouse | > 90 all | Audit in CI on every PR |

---

## Dependency Decision Log

| Decision | Chosen | Rejected | Reason |
|----------|--------|---------|--------|
| Smooth scroll | Lenis | react-scroll, native | Buttery feel = product differentiator |
| Drag & drop | dnd-kit | react-beautiful-dnd | Accessible, maintained, Three.js compatible |
| 3D | Three.js + R3F | Babylon.js, Spline | Tree-shakable, React-native, huge ecosystem |
| Animation | Framer Motion | react-spring | Better scroll-trigger API, simpler syntax |
| Components | shadcn/ui | MUI, Chakra | Copy-paste ownership, full dark customization |
| Editor | Tiptap | Quill, Slate | Headless, extensible, active development |
| Charts | Recharts | Chart.js, Victory | React-native, composable, customizable |
| State | Zustand + TQ | Redux, Jotai | Zustand: minimal; TQ: server state separation |
| Forms | RHF + Zod | Formik | Performance (uncontrolled), schema sharing |
| CSS | Tailwind v4 | CSS Modules, styled | Colocated, consistent, fast iteration |
