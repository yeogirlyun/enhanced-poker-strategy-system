## PokerPro Trainer — Product Requirements (PRD) v1.0

### 0) Executive summary
PokerPro Trainer is a desktop-first suite for No-Limit Hold’em training across four core experiences plus tools:
- Strategy Builder & Evaluator
- Practice vs. Bots
- GTO Learning Session
- Hands Review
- Bankroll & Session Tools

Unified UI architecture (Store + Event Bus + Renderer Pipeline), shared Theme Manager, and a single domain model enable consistency, speed, and testability.

### 1) Goals & success metrics
- Real-time executability of authored strategies at the table.
- Skill uplift: SEE score, BB/100, error-rate reduction in 4 weeks.
- Study velocity: draft + first sim < 60 minutes.
- Retention: ≥ 4 active days/week in Practice or Review.

Core KPIs: BB/100, EV/hand, SEE score, time-to-decision, exploitability delta, recall accuracy, usage streaks.

### 2) Users & workflows
- Live Grinder: compact, executable system; drills; quick tags; SEE focus.
- Strategy Builder: parametric strategies; backtests; sensitivity checks.
- Theory Learner: node-locking; equilibrium visualizations; sub-solves.
- Record-keeper: imports; tagging; personal compendium; flashcards.

### 3) Experiences (pillars)
#### Strategy Builder & Evaluator
- Range matrix editor (13×13 with frequency heatmap).
- Postflop node designer (textures + sizings + frequencies).
- Executability meter (SEE score) with constraints (max 2 sizings/node, freq step).
- Sim modes: Quick, Standard, Deep sample; JSON import/export.

#### Practice vs. Bots
- Opponents: GTO bot (approx) and Strategy‑Perfect bot (executes user strategy exactly).
- Modes: Drills, Free play, Scenario deck.
- SEE scoring (latency, deviation, sizing penalties) + HUD coach overlay.

#### GTO Learning Session
- Visual frequencies for SRP/3bp/4bp by texture grid.
- Node-locking and sensitivity tools with fast sub-solves/estimators.
- Flashcards: spaced repetition on board classes.

#### Hands Review
- Library: legendary, bot sessions, imported live hands.
- Filters: positions, pot type, stack depth, line, themes, SPR, depth.
- Study modes: replay, solver diff, recall quiz, explain my mistake.
- Collections: memorize curated hand sets.

#### Bankroll & Session Tools
- Session timer; buy-in/out logging; notes; goals; trends; CSV/XLSX export.

### 4) Data model (concise)
- Strategy JSON: meta, game config, preflop positions, vs_open, postflop nodes, constraints; 13×13 base64 ranges; simple texture DSL.
- Hand record: table, players, streets, actions, showdown, tags, notes, metrics.
- Bankroll: sessions array; transactions; goals and stats.

### 5) Non-functional
- Responsiveness: < 16ms UI budget; non-blocking sims.
- Stability: all timers canceled on tab hide/unmount.
- Testability: pure renderers; snapshot tests for state→draw.
- Persistence: JSON/SQLite; importers for bot/live formats.

### 6) Telemetry & analytics (local by default)
- Per-decision logs: latency, chosen vs. policy, severity.
- Aggregations: position leaks, sizing misuse, tilt timing.
- Local-first; explicit consent to sync.

### 7) UI architecture contract
- Store state: { table, seats, board, pot, hud, theme, simStatus, practice, review, bankroll }.
- Reducers: SET_TABLE_DIM, SET_POT, SET_SEATS, SET_BOARD, SET_THEME, SET_SIM_STATUS, APPEND_HAND, SET_FILTERS, BANKROLL_TXN.
- Selectors: ranges by position; current node context; SEE score.
- Events: sim:progress/done, practice:decision, review:load, bankroll:updated.

### 8) Acceptance criteria (MVP)
- Build a preflop + three flop-node strategy; export JSON.
- Quick sim returns BB/100 and a frequency heatmap in ≤ 3s.
- Practice 200 hands vs. Strategy‑Perfect bot with SEE report.
- Load 50 hands; filter by tags; replay with solver‑diff overlay.
- Log 3 sessions; dashboard shows BB/100 trend and stop‑loss warnings.
- Theme switch is instant across all tabs.

### 9) Rollout plan
1) Foundations: Store, EventBus, ThemeManager, Canvas/Layers, TimerManager.
2) Practice tab (fast iteration): Pot/Seats/Community + Strategy‑Perfect bot.
3) Strategy Builder editor & JSON I/O; basic Quick sim.
4) GTO visuals + node-locking estimator.
5) Hands Review import, tags, replay, collections.
6) Bankroll logger, reports, stop‑loss; CSV export.
7) Polish themes, accessibility, sound/animations.


