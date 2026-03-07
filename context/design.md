# workflowz.ai — Website Design Strategy
## The AI-Native JIRA Alternative

---

## Vision

workflowz.ai isn't just another project management tool — it's a reimagining of how teams think, plan, and ship. The website must feel like the product: fluid, intelligent, frictionless. Every scroll, hover, and interaction should whisper: *"This is what software feels like when AI truly understands you."*

**Core Concept:** "Intelligence that moves at the speed of thought."

---

## Design Philosophy

| Principle | How It Manifests |
|-----------|-----------------|
| **Calm productivity** | Whitespace-heavy layouts, no visual noise |
| **Progressive disclosure** | Details appear on demand, not all at once |
| **AI as collaborator** | AI actions surfaced as suggestions, never commands |
| **Dark-Luxe Neuro-Minimal** | Near-black base, electric accents, glass morphism |
| **Speed IS the product** | Buttery Lenis scroll is itself a product demo |
| **Micro-interactions** | Subtle animations that reward every interaction |

**Aesthetic Direction:** Dark-Luxe Neuro-Minimal
- Near-black backgrounds with deep navy/charcoal surfaces
- Sharp electric accents: `#00F0FF` (electric cyan) + `#A855F7` (AI violet)
- Razor-thin borders, glass morphism layers, luminous glows
- Typography that commands authority — editorial, precise, confident
- Fluid WebGL/GLSL shaders pulsing in the background like a living brain

---

## Color System

```css
:root {
  /* Core Backgrounds */
  --bg-void:        #050508;              /* Deepest background */
  --bg-surface:     #0C0C14;              /* Card / section surfaces */
  --bg-elevated:    #12121E;              /* Elevated elements */
  --bg-glass:       rgba(255,255,255,0.04); /* Glass morphism */

  /* Accent System */
  --accent-cyan:    #00F0FF;              /* Primary CTA, active states */
  --accent-violet:  #A855F7;              /* AI elements, gradients */
  --accent-indigo:  #6366F1;              /* Secondary actions */
  --accent-glow:    rgba(0, 240, 255, 0.15);

  /* Text */
  --text-primary:   #F0F0FF;
  --text-secondary: #8B8BA8;
  --text-muted:     #4A4A6A;

  /* Borders */
  --border-dim:     rgba(255,255,255,0.06);
  --border-bright:  rgba(0,240,255,0.25);

  /* Gradients */
  --gradient-hero:  linear-gradient(135deg, #050508 0%, #0D0D20 50%, #050508 100%);
  --gradient-cta:   linear-gradient(90deg, #00F0FF, #A855F7);
  --gradient-card:  linear-gradient(145deg, rgba(99,102,241,0.08), rgba(168,85,247,0.04));

  /* Semantic */
  --color-success:  #34D399;              /* Done, completed */
  --color-warning:  #FBBF24;              /* In-progress, at-risk */
  --color-danger:   #F87171;              /* Blocked, overdue */
  --color-info:     #60A5FA;              /* Informational */

  /* Priority */
  --priority-urgent: #F87171;
  --priority-high:   #FB923C;
  --priority-medium: #FBBF24;
  --priority-low:    #94A3B8;

  /* Status */
  --status-todo:        #5A5A6A;
  --status-in-progress: #6366F1;
  --status-in-review:   #60A5FA;
  --status-done:        #34D399;
  --status-blocked:     #F87171;
}
```

---

## Typography System

| Role | Font | Weight | Notes |
|------|------|--------|-------|
| Display / Hero | Clash Display or Cal Sans | 600–700 | Bold, editorial authority |
| Section Headers | Syne | 700 | Geometric, futuristic |
| Body Text | Geist | 400–500 | Clean, developer-trusted |
| Code / Mono | Geist Mono | 400 | Feature showcases, issue keys |
| Accent / Labels | Space Mono | 400 | Small caps, +0.05em tracking |

### Type Scale

```
Display: clamp(56px, 8vw, 120px)  — Hero headline
H1:      clamp(40px, 5vw, 72px)
H2:      clamp(28px, 3.5vw, 48px)
H3:      24px
Body:    16–18px, line-height 1.7
Small:   13–14px, tracking +0.05em
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | Next.js 15 (App Router) | Full-stack React foundation |
| Styling | Tailwind CSS v4 + CSS variables | Design tokens, utility classes |
| UI Components | shadcn/ui (new-york style) | Buttons, dialogs, forms, tables |
| Shaders / WebGL | Three.js + GLSL | Hero background, 3D kanban demo |
| Smooth Scroll | Lenis | Buttery luxury scroll feel |
| Navigation | 21st.dev Navbar | Glassmorphic sticky nav |
| Backgrounds | 21st.dev Backgrounds | Aurora, grid, particle effects |
| Text FX | 21st.dev Text | Split reveal, scramble, gradient text |
| Animations | Framer Motion + GSAP | Page reveals, scroll-triggered |
| 3D Kanban | Three.js | Interactive board in features section |
| State | Zustand + TanStack Query v5 | Client state + server data |
| Icons | Lucide React | Consistent stroke-1.5 icons |
| Fonts | next/font | Inter Variable, Geist, Clash Display |
| Analytics | PostHog / Plausible | Privacy-first, A/B testing |

### shadcn/ui Components to Install

```bash
npx shadcn@latest add button card badge dialog
npx shadcn@latest add navigation-menu sheet table tabs
npx shadcn@latest add toggle input textarea form
```

`components.json` theme:
```json
{
  "style": "new-york",
  "baseColor": "zinc",
  "cssVariables": true
}
```

Override `globals.css` with the workflowz dark palette above.

---

## App Layout (Marketing Site)

```
┌─────────────────────────────────────────────────────────────┐
│  STICKY NAV  (glassmorphic, blur on scroll)                 │
│  [workflowz.ai]  Features  Pricing  Docs  Blog  [Sign In]  [Start Free →] │
├─────────────────────────────────────────────────────────────┤
│  01. HERO           (100vh, WebGL shader bg)                │
│  02. SOCIAL PROOF   (infinite ticker)                       │
│  03. PROBLEM/SOL    (sticky left / scroll right)            │
│  04. FEATURES       (3D Kanban + feature cards)             │
│  05. COMPARISON     (vs JIRA / Linear / Asana table)        │
│  06. TESTIMONIALS   (masonry card grid)                     │
│  07. PRICING        (3 tiers, monthly/annual toggle)        │
│  08. FINAL CTA      (aurora background)                     │
│  09. FOOTER                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Section-by-Section Design

---

### 01. Navigation (Sticky)

**Component:** 21st.dev Navbar + shadcn/ui

```
[workflowz.ai logo]    Features  Pricing  Docs  Blog    [Sign In]  [Start Free →]
```

**Specs:**
- Transparent on load → `backdrop-filter: blur(20px)` on scroll
- Logo: geometric hexagon mark with flow lines + Clash Display wordmark
- Nav links: uppercase, tracked, 13px — hover reveals soft cyan underline glow
- CTA: gradient border, fills with `--gradient-cta` on hover
- Mobile: slide-in full-screen panel (Framer Motion)
- Scroll behavior: nav reacts to Lenis scroll velocity

---

### 02. Hero Section

**The most important 6 seconds.**

**Layout:** Full viewport height, centered content over live WebGL shader

**Shader Background (Three.js + GLSL):**
```glsl
// Neural network visualization
// 200 nodes connected by luminous threads
// Pulses at slow 0.5Hz rhythm
// Palette: void black → deep violet → electric cyan
// Reacts to mouse position (±15 deg parallax tilt)
// Fallback: CSS aurora animation (prefers-reduced-motion / low-end)
```

**Content Structure:**
```
[ BADGE: "Now in Beta — Trusted by 2,000+ teams" ]

workflowz.ai
The AI Project Manager That Actually Thinks.

[ SCRAMBLE TEXT rotating between:
  "Automates your sprints."
  "Writes your tickets."
  "Predicts your blockers."
  "Ships with your team." ]

Stop wrangling JIRA. Start shipping faster.
workflowz turns your team's chaos into structured,
AI-driven workflows that adapt in real time.

[ Get Started Free → ]    [ Watch Demo ▶ ]

──────────────────────────────────────────────
↓ Trusted by teams at
[Logo 1]  [Logo 2]  [Logo 3]  [Logo 4]  [Logo 5]
```

**Entrance Animation Sequence:**
```
0ms    Badge          fade in
50ms   H1 words       split reveal, 50ms stagger per word
300ms  Scramble text  cycle every 3s, character scramble
400ms  Body copy      fade up
600ms  CTA buttons    scale 0.9 → 1.0
800ms  Trusted logos  horizontal infinite scroll loop
```

**Parallax:** Lenis controls scroll → hero content parallaxes at 0.4x scroll speed.

---

### 03. Social Proof Ticker

**Full-width continuous scroll strip**

```
"Closed JIRA forever." — @devlead ★★★★★  ·  "2x faster sprint planning." — Sara M., Eng Manager ★★★★★  ·  "AI auto-assigns tickets better than our PM." ★★★★★
```

- Background: `--bg-surface`
- Font: Space Mono, `--text-secondary`
- Cyan star glyphs `★` as separators
- CSS `animation: ticker linear infinite` — pauses on hover

---

### 04. Problem / Solution Section

**The "JIRA Pain → workflowz Relief" narrative**

**Layout:** Two-column — sticky left / scrolling right cards

**Left Column (sticky label):**
```
THE OLD WAY
[Red-crossed screenshots of JIRA complexity]
```

**Right Column (scroll-triggered cards):**
```
❌  47 clicks to create a ticket
    ↓
✅  Describe it in plain English. Done.

❌  Manual sprint planning every 2 weeks
    ↓
✅  AI suggests optimal sprint based on velocity

❌  "Who blocked this?" — daily standup hell
    ↓
✅  Automatic blocker detection + smart reassignment

❌  Context lost between Slack, Docs, and JIRA
    ↓
✅  Unified AI workspace — everything connected
```

**Component:** shadcn/ui Card with `--gradient-card` border, scroll-triggered entrance.
Each card: `opacity: 0 → 1`, `y: 40px → 0`, `blur(8px) → blur(0)` on scroll enter.

---

### 05. Interactive Feature Showcase

**The "Wow" moment — 3D interactive product preview**

**Three.js Scene:**
- Floating 3D Kanban board, tilted 15° on x-axis (perspective)
- Cards animate between columns (Todo → In Progress → Done)
- AI assistant panel slides in, "types" a ticket in real-time
- Glowing particles float between connected cards
- Mouse drag rotates board ±15°

**Feature Cards Grid (below 3D view):**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  🤖 AI Tickets  │  │  ⚡ Auto Sprint  │  │  🧠 Smart Deps  │
│                 │  │                 │  │                 │
│ Describe work   │  │ AI plans your   │  │ Detects blockers│
│ in plain lang.  │  │ 2-week sprints  │  │ before they hit │
│ AI structures   │  │ based on real   │  │ your timeline.  │
│ the rest.       │  │ team velocity.  │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  💬 Slack Sync  │  │  📊 Live Insights│  │  🔌 100+ Integr │
│                 │  │                 │  │                 │
│ Update tickets  │  │ Real-time burn  │  │ GitHub, Figma,  │
│ directly from   │  │ down, velocity, │  │ Linear, Notion, │
│ any conversation│  │ risk forecasts. │  │ and more.       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Interaction:** Hover each card → corresponding 3D scene element highlights + animates.
Cards: `--gradient-card` background, `--border-dim` border, `--border-bright` on hover.

---

### 06. Comparison Table

**workflowz.ai vs JIRA vs Linear vs Asana**

**Component:** shadcn/ui Table with custom styling

| Feature | workflowz.ai | JIRA | Linear | Asana |
|---------|:------------:|:----:|:------:|:-----:|
| AI Ticket Creation | ✅ Native | ❌ | ⚠️ Plugin | ❌ |
| Auto Sprint Planning | ✅ | ❌ | ❌ | ❌ |
| Natural Language Input | ✅ | ❌ | ⚠️ | ❌ |
| Blocker Prediction | ✅ | ❌ | ❌ | ❌ |
| Human-in-Loop AI | ✅ | ❌ | ❌ | ❌ |
| Setup Time | 5 min | 2–3 weeks | 1 day | 1 day |
| Price / seat | $12 | $8.15+ | $8 | $10.99 |

**Design:** workflowz column has `--border-bright` cyan glow + "⚡ Best" floating badge at top.
Checkmarks: `--color-success`. X marks: `--color-danger`. Partial: `--color-warning`.

---

### 07. Testimonials

**Component:** shadcn/ui Card in masonry grid

**Layout:** 2-column masonry, staggered card heights

```
┌──────────────────────────────┐  ┌────────────────────────────┐
│ "We shipped 40% faster in    │  │ "The AI blocker alerts      │
│  our first sprint. I will    │  │  saved our Q3 release."    │
│  never go back to JIRA."     │  │                            │
│                              │  │  — Marcus L., CTO          │
│  — Priya S., VP Engineering  │  │  ⭐⭐⭐⭐⭐               │
│  ⭐⭐⭐⭐⭐                │  └────────────────────────────┘
└──────────────────────────────┘
                                   ┌────────────────────────────┐
┌──────────────────────────────┐   │ "Finally a PM tool that    │
│ "Set up in 8 minutes.        │   │  works the way my team     │
│  Migrated from JIRA in one   │   │  actually thinks."         │
│  afternoon."                 │   │                            │
│                              │   │  — Dev Team, Stripe        │
│  — Tom K., Founder           │   │  ⭐⭐⭐⭐⭐               │
│  ⭐⭐⭐⭐⭐                │   └────────────────────────────┘
└──────────────────────────────┘
```

**Animation:** Cards enter from bottom with staggered 80ms delay on scroll trigger.
Card style: `--bg-surface` bg, `--border-dim` border, `--shadow-md` on hover.

---

### 08. Pricing

**Component:** 21st.dev Pricing + shadcn/ui Card

**Layout:** Monthly / Annual toggle → three-column cards

```
         [Monthly]  [Annual — Save 20%]

┌──────────────┐  ┌──────────────────────┐  ┌──────────────┐
│   STARTER    │  │    PROFESSIONAL      │  │  ENTERPRISE  │
│              │  │  ┌─ MOST POPULAR ──┐ │  │              │
│   $0 / mo    │  │  │   $12 / mo      │ │  │   Custom     │
│              │  │  └─────────────────┘ │  │              │
│  Up to 5     │  │  Unlimited users     │  │  SSO + Audit │
│  members     │  │  All AI features     │  │  Custom AI   │
│  Basic AI    │  │  Integrations        │  │  SLA         │
│              │  │  Priority support    │  │              │
│ [Start Free] │  │ [Start Free Trial →] │  │[Talk to Sales]│
└──────────────┘  └──────────────────────┘  └──────────────┘
```

**Design:**
- Pro card: `--border-bright` cyan glow + floating "Most Popular" badge
- Annual savings shown as green badge on toggle
- All CTAs: "No credit card required" subtext

---

### 09. Final CTA

**Component:** 21st.dev Aurora Background

**Layout:** Full-screen section, aurora mesh animation behind content

```
╔════════════════════════════════════════════╗
║                                            ║
║      Your team deserves better             ║
║           than JIRA.                       ║
║                                            ║
║    Start your free workspace today.        ║
║                                            ║
║     [ Start Free — No CC Required → ]      ║
║                                            ║
║   ✓ Free forever plan                      ║
║   ✓ Import from JIRA in 1 click            ║
║   ✓ Cancel anytime                         ║
║                                            ║
╚════════════════════════════════════════════╝
```

**CTA Button:** `--gradient-cta` fill, `--shadow-lg`, scale 1.04 on hover.

---

### 10. Footer

```
workflowz.ai                Product        Company      Resources
[Logo + tagline]            Features       About        Docs
"Intelligence that          Pricing        Blog         API Reference
 moves at the speed         Integrations   Careers      Status
 of thought."               Changelog      Contact      Community
                                           Security

──────────────────────────────────────────────────────────────────
© 2025 workflowz.ai  |  Privacy  |  Terms  |  SOC2 Compliant
```

---

## Animation System

### Lenis Smooth Scroll

```ts
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  orientation: 'vertical',
  smoothWheel: true,
  wheelMultiplier: 0.8,
});
// Initialize only after first user interaction for performance
```

### Scroll-Triggered Entrance (Framer Motion)

```ts
const variants = {
  hidden: { opacity: 0, y: 40, filter: 'blur(8px)' },
  visible: {
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }
  }
}
// Stagger children: 0.08s delay per item
```

### State Transitions

```
Hover / focus:        150ms ease-out
Layout (expand):      200ms ease-in-out
Drawers / modals:     250ms ease-in-out  (slide + fade)
Drag ghost:           60% opacity, scale(1.02), shadow-lg
Drop zone:            --accent-cyan/20% bg, dashed cyan border
```

### Key Animation Keyframes

```
modal-in:    scale(0.96) + opacity 0  →  scale(1) + opacity 1
drawer-in:   translateX(100%)          →  translateX(0) + opacity 1
fade-up:     y(40px) + opacity 0       →  y(0) + opacity 1
shake:       ±4px horizontal           (validation errors)
ticker:      translateX(0)             →  translateX(-50%) linear infinite
```

### Hero Shader (Three.js + GLSL)

```glsl
// Fragment shader — neural network visualization
// uniforms: time, mouse (vec2), resolution
// 200 nodes: spheres scattered in 3D, connected by luminous line segments
// Glow material: additive blending, cyan/violet palette
// Animation: float + slow rotate at 0.3 rpm
// Mouse: scene tilts ±15° toward cursor (lerped, smooth)
// Camera: PerspectiveCamera + subtle orbit controls
// Performance: 60fps target
// Fallback: CSS @keyframes aurora when prefers-reduced-motion or low-end GPU
```

### Text Animations (21st.dev)

| Effect | Used For |
|--------|----------|
| Scramble | Rotating hero taglines (cycle every 3s) |
| Split Text | H1 word-by-word staggered reveal |
| Gradient Text | "workflowz.ai" brand name (cyan→violet shift) |
| Count Up | Stat numbers animate 0 → value on scroll enter |

---

## Component Library

### Buttons

```
Primary:    --gradient-cta fill, white text, scale(1.04) + glow on hover
Secondary:  transparent bg, --border-dim border, --bg-glass on hover
Ghost:      no bg/border, --bg-glass on hover
Danger:     --color-danger bg (confirm flows only)
Icon-only:  32×32px, ghost, --radius-md
```

### Cards

```
Base:       --bg-surface bg, --border-dim border, --radius-lg
Feature:    --gradient-card bg, --border-dim border, --border-bright on hover
Elevated:   --bg-elevated bg, --shadow-md
Glass:      --bg-glass, backdrop-filter: blur(12px), --border-dim
```

### Status Chips

```
Shape:  pill (border-radius: 999px), 6px horizontal padding, 22px height
Font:   13px, semibold, uppercase, +0.05em tracking
Colors: map to --status-* palette
```

### Avatars

```
Sizes:    20px (inline) / 24px (card) / 32px (field) / 40px (profile)
Shape:    circle
Fallback: initials on --accent-indigo background
Stack:    up to 3, -6px overlap
```

### Input Fields

```
Height:  36px (default) / 32px (compact) / 44px (modal)
Radius:  --radius-md (8px)
Border:  1px --border-dim → --border-bright on focus
BG:      --bg-surface (default) / --bg-elevated (nested)
Focus:   box-shadow: 0 0 0 3px rgba(0,240,255,0.15)
```

### Data Table (Issue List)

```
Row height:  40px
Hover:       --bg-elevated background
Selected:    --accent-cyan/10% tint + 2px left cyan border
Columns:     ☐ | type | key | title | priority | status | assignee | due | pts
Sortable:    click header → chevron indicator
```

---

## Responsive Strategy

### Breakpoints

```css
--mobile:   < 768px
--tablet:   768px – 1024px
--desktop:  1024px – 1440px
--wide:     > 1440px
```

### Mobile Adaptations

| Element | Desktop | Mobile |
|---------|---------|--------|
| Hero shader | Full Three.js neural graph | CSS aurora fallback (50% density) |
| 3D Kanban | Interactive Three.js board | Scrollable 2D card carousel |
| Navigation | Full links + CTA | Hamburger → full-screen slide-in |
| Comparison table | Full table | Horizontally scrollable |
| Pricing | 3-column | Single column, swipeable |
| Typography | `clamp()` fluid scale | Scales smoothly via same clamp |

---

## Performance Budget

| Metric | Target |
|--------|--------|
| Initial JS (gzipped) | < 150 KB |
| Three.js bundle | < 80 KB (tree-shaken) |
| Total page weight | < 2 MB |
| LCP | < 2.5s |
| CLS | < 0.1 |
| INP | < 200ms |
| Lighthouse Score | > 90 |

### Strategies

- **Shader fallback:** CSS `@keyframes aurora` for `prefers-reduced-motion`
- **Images:** WebP + AVIF via Next.js `<Image />`
- **Fonts:** `font-display: swap`, preload critical weights only
- **Lenis:** Initialized only after first user interaction
- **Three.js:** Dynamic import, loads only when hero is in viewport
- **Code splitting:** Each section lazy-loaded below the fold

---

## File Structure

```
workflowz-ai/
├── app/
│   ├── layout.tsx              # Lenis provider, fonts, metadata
│   ├── page.tsx                # Home page — section assembly
│   └── globals.css             # CSS variables, base styles, dark theme
│
├── components/
│   ├── layout/
│   │   ├── Navbar.tsx          # 21st.dev glassmorphic nav
│   │   └── Footer.tsx
│   │
│   ├── sections/
│   │   ├── Hero.tsx            # Shader bg + headline + CTA
│   │   ├── SocialProof.tsx     # Infinite ticker
│   │   ├── ProblemSolution.tsx # Sticky left / scroll right
│   │   ├── Features.tsx        # Three.js Kanban + feature cards
│   │   ├── Comparison.tsx      # vs JIRA table
│   │   ├── Testimonials.tsx    # Masonry testimonial grid
│   │   ├── Pricing.tsx         # 3-tier with toggle
│   │   └── FinalCTA.tsx        # Aurora bg + CTA
│   │
│   ├── ui/                     # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   └── ...
│   │
│   └── effects/
│       ├── HeroShader.tsx      # Three.js neural graph scene
│       ├── KanbanScene.tsx     # Three.js 3D Kanban demo
│       ├── LenisProvider.tsx   # Smooth scroll context
│       ├── SplitText.tsx       # Word-by-word reveal wrapper
│       └── ScrambleText.tsx    # Scramble cycling text
│
└── lib/
    ├── animations.ts           # Shared Framer Motion variants
    └── utils.ts                # shadcn cn() + helpers
```

---

## Pages / Routes (App)

```
/                           → redirect to /projects (authenticated)
/login                      → Auth page
/signup                     → Registration
/projects                   → Project list + global dashboard
/projects/[id]              → Project overview (stats, activity)
/projects/[id]/board        → Kanban board (drag-and-drop)
/projects/[id]/backlog      → Backlog + sprint management
/projects/[id]/timeline     → Roadmap / Gantt view
/projects/[id]/reports      → Burndown, velocity, distribution
/projects/[id]/issues       → Full issue list / table view
/projects/[id]/settings     → Project settings
/issues/[issueKey]          → Single issue full-page view
/team                       → Team members, roles, workload
/settings                   → User + org settings
/settings/ai                → AI pipeline config (model, Langfuse)
```

---

## AI Assistant Panel (Workflowz-Specific)

No JIRA equivalent. Accessible via "✦ AI Plan" on any project.

```
┌───────────────────────────────────────────────────────┐
│  ✦ AI Project Planner                             [×] │
│  ─────────────────────────────────────────────────    │
│  Stage 3 of 7: Clarification                          │
│  ●●●○○○○                                              │
│                                                       │
│  I need a few things before I can generate tasks:     │
│                                                       │
│  1. Will users log in with email/password, SSO, both? │
│     ○ Email/password only                             │
│     ● SSO (Google/GitHub)                             │
│     ○ Both                                            │
│                                                       │
│  2. Should the app support mobile browsers?           │
│     ● Yes    ○ No                                     │
│                                                       │
│  [Continue →]                                         │
│                                                       │
│  ─ Generated Plan Preview ──────────────────────────  │
│  12 tasks · 3 roles · Sprint 3 ready                  │
│  [Review & Approve]  [Reject]                         │
└───────────────────────────────────────────────────────┘
```

- Slide-in right panel (520px), does not navigate away from board/backlog
- Progress dot-track shows pipeline stage (7 stages)
- Clarification questions as styled radio/checkbox groups
- Plan preview: task count, role breakdown, sprint fit estimate
- "Review & Approve" → full-screen approval view before any DB write

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `C` | Create new issue |
| `B` | Go to Board |
| `L` | Go to Backlog |
| `T` | Go to Timeline |
| `⌘K` | Open search |
| `⌘/` | Open command palette |
| `Esc` | Close modal / drawer |
| `?` | Show shortcuts help overlay |

---

## Launch Roadmap

### Phase 1 — Foundation (Week 1–2)
- [ ] Next.js 15 project setup with TypeScript
- [ ] shadcn/ui theme with workflowz dark palette
- [ ] Lenis scroll provider (`LenisProvider.tsx`)
- [ ] Navbar + Footer components
- [ ] Typography system (Geist, Clash Display, Space Mono via `next/font`)

### Phase 2 — Hero & Wow (Week 2–3)
- [ ] Three.js hero shader neural graph scene
- [ ] Hero copy + entrance animations (SplitText, ScrambleText)
- [ ] Social proof ticker (infinite CSS scroll)
- [ ] Mobile shader fallback (CSS aurora)

### Phase 3 — Content Sections (Week 3–4)
- [ ] Problem/Solution sticky-scroll section
- [ ] 3D Kanban feature demo (Three.js)
- [ ] Feature card grid (6 cards)
- [ ] Comparison table (vs JIRA/Linear/Asana)

### Phase 4 — Conversion (Week 4–5)
- [ ] Testimonials masonry grid
- [ ] Pricing section with monthly/annual toggle
- [ ] Final CTA with 21st.dev aurora background
- [ ] All scroll-triggered entrance animations

### Phase 5 — Polish & Ship (Week 5–6)
- [ ] Performance audit (Lighthouse > 90 all metrics)
- [ ] Responsive QA across all breakpoints
- [ ] SEO metadata, OG image, favicon
- [ ] Analytics (PostHog / Plausible)
- [ ] A/B test hero headline variants

---

## Conversion Design Principles

1. **Single primary CTA** — "Start Free" appears exactly 4×: Navbar, Hero, Pricing, Final CTA
2. **Remove friction** — "No credit card" on every CTA
3. **JIRA migration hook** — "Import from JIRA in 1 click" addresses the #1 adoption blocker
4. **Social proof density** — Company logos, star ratings, testimonials visible above the fold
5. **Clarity over cleverness** — Every feature described in one sentence, benefit-first
6. **Speed as product** — Buttery Lenis scroll is the live product demo before signup

---

## Differentiators vs JIRA

| Feature | JIRA | workflowz.ai |
|---------|------|-------------|
| Visual style | Corporate blue, dense | Dark-luxe, spacious, editorial |
| AI task generation | None | 7-stage HITL pipeline (native) |
| Dark mode | Secondary option | First-class default |
| Issue drawer | Full-page navigation | Slide-in panel (no nav break) |
| Blocker prediction | Manual | Automatic, AI-driven |
| Setup time | 2–3 weeks | 5 minutes |
| Natural language input | No | Yes — describe in plain English |
| Mobile | Limited | Tablet-responsive |
| Scroll experience | Standard browser | Lenis buttery smooth |
| Onboarding | Complex wizard | Guided with AI-assist |

---

*workflowz.ai — Built with intelligence. Designed for humans.*
