## PokerPro Trainer — Design Document v1.0

### Design goals
- Deterministic, event-driven UI; single source of truth per session.
- Stateless renderers; no timing or logic in UI components.
- Clear layering: Domain (FPSM/engines), Application (GameDirector/session services), UI (render-only).

### UI architecture
- Store: Redux-like dict state; reducers for table, seats, board, pot, HUD, theme, review.
- Event Bus: session-namespaced pub/sub; no cross-tab leakage.
- Services (DI): ThemeManager (tokens + fonts), TimerManager (central after/cancel), SoundManager, AnimationManager, SessionController (FSM bridge).
- Rendering: CanvasManager + LayerManager + RendererPipeline; components (TableFelt, Seats, Community, DealerButton, PotDisplay, BetAnimations, HUD).
- Z-order: felt < seats < community < pot < overlay.
- Resize: debounced via TimerManager; components re-read size on render.
- Fonts: global Cmd -/= and 0 mapped to ThemeManager; components read `font.*` tokens.

### Data & selectors
- Strategy JSON: compact, executable; 13×13 matrices (base64) and node rules.
- Hand record: tables, actions, tags, metrics.
- Selectors: seat positions, board layout, dealer position, pot text center, HUD view models.

### Interactions
- Practice: UI dispatches intents; SessionController calls FPSM/bots; display snapshots dispatch SET_* actions.
- Review: HandsRepository lists/loads hands; stepper applies snapshots via FpsmEventAdapter.
- GTO: Estimator emits sim:progress events; reducers update simStatus; HUD renders progress.

### Theming & accessibility
- Theme tokens only; three shipped profiles (Emerald Noir, Royal Indigo, Crimson Gold).
- Contrast ≥ 4.5:1 for key text; hit targets ≥ 44×44; focus rings via tokens.

### Testing
- Snapshot tests: state → canvas items per component tag.
- Deterministic unit tests for reducers/selectors and SessionController mappings.

### Open items (tracked)
- BetAnimationManager (chips path, non-blocking); SoundManager session scope.
- Collections & Flashcards in Review.
- Strategy Builder editor and Quick simulator UI.


