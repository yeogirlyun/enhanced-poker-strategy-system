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

### Button Design System

#### Design Principles
- **Contrast first**: Active vs inactive states must be immediately obvious
- **Casino aesthetic**: Deep greens, burgundy reds, gold accents, dark steel blues
- **Accessibility**: WCAG contrast compliance for color-blind users
- **Consistency**: All buttons follow same state pattern across themes

#### Button States

| State | Description | Visual Treatment |
|-------|-------------|------------------|
| **Default (Idle)** | Neutral resting state | Dark charcoal background, thin metallic border, silver text |
| **Hover** | Mouse over interaction | Theme color background, bright gold text, subtle glow |
| **Active/Pressed** | Currently selected/pressed | Bold theme color, gold text, inner shadow |
| **Disabled** | Unavailable action | Dim grey, desaturated text, no hover response |

#### Theme Color Variations

**Emerald Casino Theme**
- Default: Background #1E1E1E, Border #A0A0A0, Text #E0E0E0
- Hover: Background #2D5A3D, Text #FFD700
- Active: Background #008F4C, Text #FFD700, inner shadow
- Disabled: Background #3A3A3A, Text #777777

**Burgundy Royale Theme**  
- Default: Background #1E1E1E, Border #A0A0A0, Text #E0E0E0
- Hover: Background #7A1C1C, Text #E6C76E
- Active: Background #B22222, Text #FFD700, inner shadow
- Disabled: Background #2B2B2B, Text #777777

**Midnight Blue Theme**
- Default: Background #1E1E1E, Border #A0A0A0, Text #D9D9D9
- Hover: Background #1D3557, Text #D9D9D9
- Active: Background #0A192F, Text #D9D9D9, inner shadow
- Disabled: Background #444444, Text #777777

#### UI Enhancements
- Rounded edges (3-4px border radius)
- 2-3px gold border on active state
- Subtle glow effect on hover (box-shadow)
- Smooth transitions (120-200ms) between states
- Poker chip/card table aesthetic inspiration

#### Critical Implementation Details (macOS Compatibility)

**🚨 IMPORTANT: Use `tk.Label` for Custom Button Colors**

**Problem:** On macOS, `tk.Button` widgets are overridden by the system appearance (light/dark mode), making custom background colors appear as white/system colors regardless of the `bg` parameter.

**Solution:** Use `tk.Label` with click bindings to create button-like widgets that respect custom colors.

**Working Implementation Pattern:**
```python
# ✅ WORKS: tk.Label with click binding
button = tk.Label(
    parent,
    text="🔥 Button Text",
    bg="#1E1E1E",      # Custom colors work!
    fg="#E0E0E0",
    relief='raised',    # Button-like appearance
    borderwidth=2,
    cursor='hand2'
)
button.bind('<Button-1>', on_click)
button.bind('<Enter>', on_hover_enter)
button.bind('<Leave>', on_hover_leave)

# ❌ FAILS: tk.Button (system overrides colors)
button = tk.Button(
    parent,
    text="Button Text", 
    bg="#1E1E1E",      # Ignored by macOS - shows white!
    fg="#E0E0E0"
)
```

**Required Event Bindings for Labels-as-Buttons:**
- `<Button-1>`: Click handling
- `<Enter>`: Hover enter (apply hover colors)
- `<Leave>`: Hover leave (restore default colors)
- Manual `relief='sunken'` on click for press feedback

**Visual States Implementation:**
- Default: `relief='raised'`, `bg=default_color`
- Hover: `bg=hover_color`, maintain relief
- Active/Press: `relief='sunken'`, `bg=active_color`, restore after 100ms
- Disabled: `bg=disabled_color`, disable event bindings

This approach is **mandatory** for all custom-colored interactive elements in the poker UI on macOS.

### Testing
- Snapshot tests: state → canvas items per component tag.
- Deterministic unit tests for reducers/selectors and SessionController mappings.

### Open items (tracked)
- BetAnimationManager (chips path, non-blocking); SoundManager session scope.
- Collections & Flashcards in Review.
- Strategy Builder editor and Quick simulator UI.


