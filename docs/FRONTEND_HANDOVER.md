# FRONTEND HANDOVER — Executive Benchmark Engine (Premium Web UI)

> **Handover Author:** Antigravity (Solutions Architect)
> **Handover Date:** 2026-03-26T22:24:00-03:00
> **Target Agent:** Gemini 3 Pro High
> **Project Root:** `d:\VMs\Projetos\Smart_AI_Resume`
> **Frontend Root:** `d:\VMs\Projetos\Smart_AI_Resume\frontend\`

---

## 0. BEFORE YOU START

### Mandatory Reading
1. `docs/AGENTIC_PROTOCOL.md` — You MUST follow this. Every change requires a timestamped log entry with your agent name.
2. `docs/HANDOVER.md` — Full project context and architecture.
3. `docs/AGENTS_LOG.md` — Read last 5 entries for project history.

### Log Your Onboarding
Add an onboarding entry to `docs/AGENTS_LOG.md` before writing any code (format is in `AGENTIC_PROTOCOL.md` Section 5).

### Available Resources
You have access to **1000+ specialized skills** in the global skills library (`~/.gemini/antigravity/skills/`), including:
- `antigravity-design-expert` — Glassmorphism, GSAP, spatial UI
- `frontend-developer` — React 19, Next.js 15, modern patterns
- `nextjs-app-router-patterns` — App Router, Server Components
- `tailwind-design-system` — Design tokens, component variants
- `react-flow-architect` — Complex interactive visualizations
- `claude-d3js-skill` — D3.js data visualization
- `ui-ux-pro-max` — Comprehensive design guide
- `design-spells` — Premium micro-interactions
- `scroll-experience` — Scroll-driven animations
- `3d-web-experience` — Three.js if needed
- `frontend-ui-dark-ts` — Dark-themed React + Tailwind system
- `shadcn` — Component library patterns
- `baseline-ui` — Typography, accessibility, layout validation
- And hundreds more...

**If you have any doubt about design patterns, accessibility, animation, or component architecture — check the skills library first.** Run `ls ~/.gemini/antigravity/skills/` to browse.

---

## 1. MISSION

Build a **Fortune 500 / Big Tech caliber** web dashboard for the Executive CV Benchmark Engine. This is NOT a prototype — it must look and feel like an enterprise product from Google, Stripe, or Linear.

### Design North Stars
- **Stripe Dashboard** — Clean data density, premium typography
- **Linear App** — Smooth animations, dark mode, keyboard shortcuts
- **Vercel Dashboard** — Glassmorphism, real-time feedback
- **Notion** — Content-rich but uncluttered

---

## 2. TECH STACK

| Layer | Technology | Reason |
|-------|------------|--------|
| Framework | **Next.js 15** (App Router) | SSR, file-based routing, API routes for proxy |
| Styling | **Tailwind CSS v4** | Utility-first, design token control |
| Charts | **Recharts** (primary) + **D3.js** (radar chart) | Score visualizations |
| Components | **shadcn/ui** or hand-built | Premium accessible components |
| Animations | **Framer Motion** | Page transitions, micro-interactions |
| Icons | **Lucide React** | Consistent icon set |
| Font | **Inter** or **Geist** (from Google Fonts/Vercel) | Modern, professional |
| HTTP Client | **fetch** or **SWR** | API calls to FastAPI backend |
| State | **Zustand** or React Context | Lightweight global state |

**No Streamlit. No Bootstrap. No Material UI.** This must be custom and premium.

---

## 3. BACKEND API CONTRACT

The FastAPI backend runs at `http://localhost:8000`. CORS is enabled for all origins.

### Endpoints

#### `GET /health`
```json
Response: { "status": "ok", "service": "smart-ai-resume" }
```

#### `POST /api/v1/analyze` — Text Input
```json
Request: {
  "cv_text": "string (raw CV text)",
  "jd_text": "string (raw JD text or URL)"
}

Response: {
  "run_id": "uuid-string",
  "final_score": 95.0,
  "iterations_used": 2,
  "overall_positioning_score": 81.8,
  "benchmark": {
    "fortune100": "Above Average",
    "bigTech": "Top 10%",
    "tier1Consulting": "Average",
    "ipo_ma": "Above Average",
    "global": "Average"
  },
  "differentiators": ["string", "string", "string"],
  "weaknesses": ["string", "string"],
  "risks": {
    "scale": { "level": "Low", "explanation": "..." },
    "international_exposure": { "level": "Medium", "explanation": "..." },
    "financial_impact": { "level": "Low", "explanation": "..." },
    "strategic_narrative": { "level": "Medium", "explanation": "..." },
    "operational_bias": { "level": "High", "explanation": "..." }
  },
  "improved_cv_markdown": "# Full markdown CV...",
  "output_docx_path": "outputs/uuid/cv.docx",
  "output_pdf_path": null
}
```

#### `POST /api/v1/analyze/upload` — File Upload
```
Content-Type: multipart/form-data
Fields:
  cv_file: File (docx/pdf/txt)
  jd_text: string
Response: Same as /analyze
```

#### `GET /api/v1/runs/{run_id}/download?format=docx`
Returns the generated CV as a file download.

---

## 4. PAGE STRUCTURE

### 4.1 — Landing / Upload Page (`/`)
- Dark gradient background with subtle grid pattern
- Centered card with glassmorphism effect
- Two input zones:
  - **CV Upload**: Drag-and-drop zone with file icon animation (accepts .docx, .pdf, .txt)
  - **Job Description**: Rich textarea with placeholder text
- "Analyze" button with loading state animation
- Subtle brand mark in corner

### 4.2 — Processing Page (`/analyzing`)
- Full-screen animated progress indicator
- 8 pipeline phases shown as a vertical timeline or stepper
- Each phase lights up with a smooth animation as it completes:
  1. Extraction
  2. Market Positioning
  3. Benchmark Analysis
  4. Distinctiveness Assessment
  5. Risk Evaluation
  6. CV Generation
  7. Re-Evaluation (show iteration count)
  8. Export & Finalize
- Estimated time remaining
- Subtle particle or gradient animation in background

### 4.3 — Results Dashboard (`/results/{run_id}`)
This is the hero page. It must be stunning.

#### Top Bar
- Final score as a large animated counter (e.g., "95.0" with count-up animation)
- Score quality badge: "Exceptional" / "Strong" / "Needs Work" with color coding
- Iterations used badge
- Download buttons (DOCX, PDF)

#### Section A — Market Positioning Radar
- **Radar/Spider chart** (D3.js) showing all 8 category scores
  - Scale, Strategic Complexity, Transformation History, Competitive Differentiation
  - International Experience, Career Progression Speed, Financial Impact, Executive Presence
- Hover tooltips with score values
- Smooth entrance animation

#### Section B — Executive Benchmark Comparison
- Horizontal bar chart or tier badge display showing archetype classifications:
  - Fortune 100, Big Tech, Tier-1 Consulting, IPO/M&A, Global
- Each with a colored tier badge (Below Average → Top 1%)
- Visual distinction between tiers using gradient colors

#### Section C — Differentiators & Weaknesses
- Two side-by-side cards:
  - **Differentiators** (green accent) — 3 items with check icons
  - **Weaknesses** (amber accent) — items with warning icons
- Clean typography, no clutter

#### Section D — Risk Assessment Heatmap
- 5 risk categories displayed as a horizontal risk matrix
- Color-coded severity: Low (green) → Medium (yellow) → High (orange) → Critical (red)
- Each with expandable explanation text
- Smooth hover/expand transitions

#### Section E — Generated CV Preview
- Rendered markdown preview in a styled document container
- Toggle between "Preview" and "Raw Markdown" views
- Syntax-highlighted markdown view
- "Download DOCX" and "Copy Markdown" buttons

### 4.4 — History Page (`/history`) — Optional/Stretch
- List of past runs with scores, dates, and quick-compare functionality

---

## 5. DESIGN SYSTEM REQUIREMENTS

### Color Palette (Dark Mode Primary)
```
Background:     hsl(220, 20%, 6%)    — near-black with blue undertone
Surface:        hsl(220, 18%, 10%)   — card backgrounds
Surface-hover:  hsl(220, 16%, 14%)   — interactive surfaces
Border:         hsl(220, 14%, 18%)   — subtle borders
Text-primary:   hsl(0, 0%, 95%)      — white-ish
Text-secondary: hsl(0, 0%, 60%)      — muted

Accent:         hsl(250, 80%, 65%)   — vibrant purple (primary actions)
Accent-hover:   hsl(250, 80%, 72%)
Success:        hsl(145, 70%, 50%)   — green (high scores, differentiators)
Warning:        hsl(35, 90%, 55%)    — amber (medium risk, weaknesses)
Danger:         hsl(0, 75%, 55%)     — red (critical risk)
Info:           hsl(200, 80%, 55%)   — blue (benchmarks)
```

### Typography
- **Font:** Inter (400, 500, 600, 700) or Geist Sans
- **Scale:** 12px / 14px / 16px / 20px / 24px / 32px / 48px
- **Score numbers:** Tabular numerals, font-variant-numeric: tabular-nums

### Spacing
- Base unit: 4px
- Consistent padding: 16px (cards), 24px (sections), 32px (page)

### Animations
- Page transitions: 300ms ease-out
- Card hover: 150ms scale(1.01) + shadow
- Score counter: 1.5s count-up on mount
- Chart entrance: 800ms staggered fade-in
- Risk expansion: 200ms height transition

### Glassmorphism (used sparingly)
```css
background: rgba(255, 255, 255, 0.04);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.06);
```

---

## 6. ACCEPTANCE CRITERIA

1. `npm run dev` starts the frontend at `localhost:3000`
2. File upload + text input both work against `localhost:8000` backend
3. All 5 dashboard sections render real data from the API
4. Radar chart shows 8 category scores with hover tooltips
5. Risk heatmap shows 5 categories with correct severity colors
6. DOCX download works via the API
7. Page transitions are smooth (Framer Motion)
8. Responsive: works at 1440px, 1024px, and 768px widths
9. Lighthouse Performance score >= 90
10. Zero console errors in production build

---

## 7. PROJECT STRUCTURE

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout (dark theme, font, metadata)
│   ├── page.tsx             # Landing / Upload page
│   ├── analyzing/
│   │   └── page.tsx         # Processing animation page
│   └── results/
│       └── [runId]/
│           └── page.tsx     # Results dashboard
├── components/
│   ├── ui/                  # Base UI components (Button, Card, Badge, etc.)
│   ├── charts/
│   │   ├── RadarChart.tsx   # 8-category score radar
│   │   ├── BenchmarkBars.tsx
│   │   └── RiskHeatmap.tsx
│   ├── upload/
│   │   ├── DropZone.tsx
│   │   └── TextArea.tsx
│   ├── results/
│   │   ├── ScoreHero.tsx
│   │   ├── Differentiators.tsx
│   │   ├── CVPreview.tsx
│   │   └── DownloadActions.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Footer.tsx
├── lib/
│   ├── api.ts               # API client (fetch wrappers)
│   ├── types.ts             # TypeScript types matching API schema
│   └── utils.ts             # Formatters, color helpers
├── styles/
│   └── globals.css          # Tailwind base + custom properties
├── public/
│   └── (logo, OG image)
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

---

## 8. MANDATORY DOC UPDATES

After completing the frontend, update:
- `docs/AGENTS_LOG.md` — Your build entries
- `docs/DELIVERABLES.md` — Add deliverable #39 (Premium Web UI)
- `CHANGELOG.md` — Add frontend section under v0.3.0
- `docs/HANDOVER.md` — Mark UI item as completed

**Format:** See `docs/AGENTIC_PROTOCOL.md` for the exact entry format.

---

## 9. GETTING STARTED

```bash
cd d:\VMs\Projetos\Smart_AI_Resume

# Start the backend (keep running)
.venv\Scripts\python.exe -m uvicorn smart_resume.api.app:app --reload --port 8000

# Initialize the frontend
cd frontend
npx -y create-next-app@latest ./ --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --turbopack --no-git
npm install recharts framer-motion lucide-react d3 @types/d3
npm run dev
```

Then build the pages and components as described in Section 4.
