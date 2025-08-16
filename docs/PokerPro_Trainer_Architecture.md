## PokerPro Trainer — Architecture v1.0

### Core tenets
- Single-threaded, event-driven GameDirector coordinates timing.
- Single source of truth (Store) per session; UI is pure render.
- No blocking ops in UI; no timers/threading in logic; no global state leaks.

### Layers
- Domain (Engines/FPSM): game rules, simulations, estimators; no UI/timing.
- Application (GameDirector + Services): SessionController, TimerManager, Sound/Animation, Logger; owns scheduling.
- UI: AppShell + Tabs; CanvasManager, LayerManager, RendererPipeline; stateless components.

### Session wiring
1) AppShell creates session_id, Store, services; mounts Tab.
2) SessionController bridges FPSM events → store actions; UI intents → FPSM calls.
3) EventBus topics are namespaced: `session_id:kind:event`.

### State & reducers
- State shape: `{ table, seats, board, pot, hud, theme, simStatus, practice, review, bankroll }`.
- Reducers handle SET_TABLE_DIM, SET_POT, SET_SEATS, SET_BOARD, SET_THEME, SET_SIM_STATUS, APPEND_HAND, SET_FILTERS, BANKROLL_TXN.

### Rendering pipeline
- CanvasManager emits size; RendererPipeline clears-by-tag and renders components.
- LayerManager enforces z-order; overlay reserved for animations/HUD.

### Theming
- ThemeManager provides token lookups (colors, typography); profiles persisted; subscribable.

### Engines
- Range Engine: 13×13 range matrices with frequency.
- Simulation Engine: rollout Monte-Carlo; light CFR/CFR+ spot solves; equity oracle cache.
- Estimator: quick EV/GTO approximations with budgets.

### Persistence & importers
- JSON for strategies/hands; SQLite for sessions/bankroll; importers for bot/live.

### Testing & diagnostics
- Deterministic unit tests for reducers/selectors; snapshot tests for UI components.
- Logs routed to `logs/` with rotation; no console spam; identifiers only (no PII).

### Security & privacy
- Local-first data; explicit consent to sync; redact sensitive info in logs.


