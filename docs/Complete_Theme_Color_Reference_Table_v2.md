# 🎨 Complete Theme Color Reference Table v2
## Token Normalization (Authoritative)

To prevent drift, **dot.notation** is the preferred naming for all tokens. Keep a compatibility map for legacy underscores.

**Preferred:** `bg.primary`, `bg.secondary`, `a11y.focus`  
**Legacy (compat):** `primary_bg` → `bg.primary`, `secondary_bg` → `bg.secondary`

> Components must **not** hardcode colors. Always use ThemeManager tokens.

### Compatibility Map (initial)
| Legacy token | Preferred token |
|---|---|
| `primary_bg` | `bg.primary` |
| `secondary_bg` | `bg.secondary` |
| `player_name` | `text.playerName` |
| `chip_gold` | `chip.gold` |

> Continue extending this table as you migrate; keep both names active during transition.

## Non-Color Tokens (additive)
Define and centralize non-color tokens used throughout the app:

- **Typography**: `font.body`, `font.caption`, `font.display`  
- **Spacing**: `space.xs`, `space.sm`, `space.md`, `space.lg`, `space.xl`  
- **Elevation**: `elev.0`, `elev.1`, `elev.2`, `elev.3`  
- **Radius**: `radius.sm`, `radius.md`, `radius.lg`, `radius.xl`  

## Accessibility (WCAG)
- Minimum contrast: **≥ 4.5:1** for text; **≥ 3:1** for large text and UI glyphs.
- Focus rings use `a11y.focus` and must be visible at all times.
- Tap targets: **≥ 44×44** px.


## All UI Elements & Color Coding Across 11 Professional Themes

> **Last Updated**: Latest luxury theme integration  
> **Total Themes**: 11 (3 Luxury + 8 Professional Casino)  
> **Total Elements**: 50+ core UI components  

---

## 📊 **LUXURY THEME COLLECTION** (LV Noir Series)

### **💎 LV Noir** - *Deep Mahogany & Antique Gold*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#2A120F` | Deep mahogany felt |
| | `table.rail` | `#1B1612` | Dark leather rail |
| | `table.railHighlight` | `#C3A568` | Antique gold highlight |
| | `table.inlay` | `#6B5B3E` | Aged brass inlay |
| | `table.edgeGlow` | `#3B201A` | Subtle edge glow |
| | `table.center` | `#3B201A` | Center accent |
| **Typography** | `text.primary` | `#F3EAD7` | Warm parchment |
| | `text.secondary` | `#C9BFA9` | Secondary text |
| | `text.muted` | `#948B79` | Muted text |
| | `text_gold` | `#C3A568` | Antique gold text |
| **Gold System** | `gold.base` | `#C3A568` | Antique gold |
| | `gold.bright` | `#E8C87B` | Bright gold |
| | `gold.dim` | `#9E8756` | Dim gold |
| **Burgundy System** | `burgundy.base` | `#7E1D1D` | Burgundy base |
| | `burgundy.deep` | `#4A0F12` | Deep burgundy |
| | `burgundy.bright` | `#A22A2A` | Bright burgundy |
| **Backgrounds** | `primary_bg` | `#141110` | Main background |
| | `secondary_bg` | `#2A2622` | Secondary background |
| | `panel.bg` | `#141110` | Panel background |
| | `panel.fg` | `#F3EAD7` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#3A2D1E` | Pot badge background |
| | `pot.badgeRing` | `#C3A568` | Pot badge ring |
| | `pot.valueText` | `#F7ECD1` | Pot value text |
| | `chip_gold` | `#C3A568` | Gold chips |
| **Player Seats** | `seat.bg.idle` | `#1B1612` | Idle seat |
| | `seat.bg.active` | `#2A2622` | Active seat |
| | `seat.bg.acting` | `#3A2D1E` | Acting seat |
| | `player.name` | `#C9BFA9` | Player names |
| | `player.stack` | `#C3A568` | Stack amounts |
| **Cards** | `board.cardBack` | `#7E1D1D` | Burgundy card backs |
| | `board.cardFaceFg` | `#F3EAD7` | Card face text |
| | `board.border` | `#6B5B3E` | Card borders |
| **Buttons** | `btn.default.bg` | `#1E1A17` | Default button |
| | `btn.hover.bg` | `#2A2521` | Hover state |
| | `btn.active.bg` | `#3A2F24` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#F1E3B2` | Antique gold |
| | `dealer.buttonFg` | `#3A2D1E` | Dark text |
| | `dealer.buttonBorder` | `#C3A568` | Gold border |

### **🏆 Crimson Monogram** - *Deep Crimson & Bright Gold*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#3B0E11` | Deep crimson felt |
| | `table.rail` | `#1B1612` | Dark leather rail |
| | `table.railHighlight` | `#E8C87B` | Bright gold highlight |
| | `table.edgeGlow` | `#4A1013` | Crimson edge glow |
| **Typography** | `text_gold` | `#E8C87B` | Bright gold text |
| **Burgundy System** | `burgundy.base` | `#A22A2A` | Brighter burgundy |
| | `burgundy.bright` | `#CC3C52` | Bright burgundy |
| **Backgrounds** | `secondary_bg` | `#4A1013` | Crimson background |
| | `panel.border` | `#4A1013` | Crimson borders |
| **Pot & Chips** | `pot.badgeBg` | `#4A1013` | Crimson pot badge |
| | `pot.badgeRing` | `#E8C87B` | Gold badge ring |

### **🌟 Diamond Elite** - *Deep Navy & Platinum*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#0F1A2E` | Deep navy felt |
| | `table.rail` | `#1B1612` | Dark leather rail |
| | `table.railHighlight` | `#E5E4E2` | Platinum highlight |
| | `table.edgeGlow` | `#1A2B4A` | Navy edge glow |
| **Typography** | `text_platinum` | `#E5E4E2` | Platinum text |
| **Platinum System** | `platinum.base` | `#E5E4E2` | Platinum base |
| | `platinum.bright` | `#F5F5F5` | Bright platinum |
| | `platinum.dim` | `#C0C0C0` | Dim platinum |
| **Navy System** | `navy.base` | `#0F1A2E` | Navy base |
| | `navy.deep` | `#0A0F1A` | Deep navy |
| | `navy.bright` | `#1A2B4A` | Bright navy |
| **Backgrounds** | `primary_bg` | `#0A0F1A` | Main background |
| | `secondary_bg` | `#1A2B4A` | Secondary background |
| | `panel.bg` | `#0A0F1A` | Panel background |
| | `panel.fg` | `#E5E4E2` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#1A2B4A` | Navy pot badge |
| | `pot.badgeRing` | `#E5E4E2` | Platinum badge ring |
| | `pot.valueText` | `#F5F5F5` | Pot value text |
| | `chip_platinum` | `#E5E4E2` | Platinum chips |
| **Player Seats** | `seat.bg.idle` | `#0F1A2E` | Idle seat |
| | `seat.bg.active` | `#1A2B4A` | Active seat |
| | `seat.bg.acting` | `#2A3B5A` | Acting seat |
| | `player.name` | `#C0C0C0` | Player names |
| | `player.stack` | `#E5E4E2` | Stack amounts |
| **Cards** | `board.cardBack` | `#0F1A2E` | Navy card backs |
| | `board.cardFaceFg` | `#E5E4E2` | Card face text |
| | `board.border` | `#1A2B4A` | Card borders |
| **Buttons** | `btn.default.bg` | `#0F1A2E` | Default button |
| | `btn.hover.bg` | `#1A2B4A` | Hover state |
| | `btn.active.bg` | `#2A3B5A` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#E5E4E2` | Platinum |
| | `dealer.buttonFg` | `#0F1A2E` | Navy text |
| | `dealer.buttonBorder` | `#1A2B4A` | Navy border |

---

## 🎰 **PROFESSIONAL CASINO THEME COLLECTION**

### **🔵 Classic Blue** - *Traditional Casino Blue*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#1E3A8A` | Classic casino blue |
| | `table.rail` | `#1E40AF` | Darker blue rail |
| | `table.railHighlight` | `#3B82F6` | Bright blue highlight |
| | `table.edgeGlow` | `#1E40AF` | Blue edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#3B82F6` | Blue accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#1E3A8A` | Blue pot badge |
| | `pot.badgeRing` | `#3B82F6` | Blue badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_blue` | `#3B82F6` | Blue chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#3B82F6` | Stack amounts |
| **Cards** | `board.cardBack` | `#1E3A8A` | Blue card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#3B82F6` | Blue card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#3B82F6` | Blue |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#1E3A8A` | Dark blue border |

### **🟢 Emerald Green** - *Professional Green*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#065F46` | Professional green |
| | `table.rail` | `#047857` | Darker green rail |
| | `table.railHighlight` | `#10B981` | Bright green highlight |
| | `table.edgeGlow` | `#047857` | Green edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#10B981` | Green accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#065F46` | Green pot badge |
| | `pot.badgeRing` | `#10B981` | Green badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_green` | `#10B981` | Green chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#10B981` | Stack amounts |
| **Cards** | `board.cardBack` | `#065F46` | Green card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#10B981` | Green card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#10B981` | Green |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#065F46` | Dark green border |

### **🔴 Ruby Red** - *Bold Casino Red*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#7F1D1D` | Bold casino red |
| | `table.rail` | `#991B1B` | Darker red rail |
| | `table.railHighlight` | `#EF4444` | Bright red highlight |
| | `table.edgeGlow` | `#991B1B` | Red edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#EF4444` | Red accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#7F1D1D` | Red pot badge |
| | `pot.badgeRing` | `#EF4444` | Red badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_red` | `#EF4444` | Red chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#EF4444` | Stack amounts |
| **Cards** | `board.cardBack` | `#7F1D1D` | Red card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#EF4444` | Red card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#EF4444` | Red |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#7F1D1D` | Dark red border |

### **🟡 Golden Yellow** - *Warm Casino Gold*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#92400E` | Warm casino gold |
| | `table.rail` | `#B45309` | Darker gold rail |
| | `table.railHighlight` | `#F59E0B` | Bright gold highlight |
| | `table.edgeGlow` | `#B45309` | Gold edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#F59E0B` | Gold accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#92400E` | Gold pot badge |
| | `pot.badgeRing` | `#F59E0B` | Gold badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_gold` | `#F59E0B` | Gold chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#F59E0B` | Stack amounts |
| **Cards** | `board.cardBack` | `#92400E` | Gold card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#F59E0B` | Gold card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#F59E0B` | Gold |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#92400E` | Dark gold border |

### **🟣 Royal Purple** - *Elegant Casino Purple*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#581C87` | Elegant casino purple |
| | `table.rail` | `#6B21A8` | Darker purple rail |
| | `table.railHighlight` | `#A855F7` | Bright purple highlight |
| | `table.edgeGlow` | `#6B21A8` | Purple edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#A855F7` | Purple accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#581C87` | Purple pot badge |
| | `pot.badgeRing` | `#A855F7` | Purple badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_purple` | `#A855F7` | Purple chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#A855F7` | Stack amounts |
| **Cards** | `board.cardBack` | `#581C87` | Purple card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#A855F7` | Purple card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#A855F7` | Purple |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#581C87` | Dark purple border |

### **🟠 Sunset Orange** - *Warm Casino Orange*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#C2410C` | Warm casino orange |
| | `table.rail` | `#EA580C` | Darker orange rail |
| | `table.railHighlight` | `#FB923C` | Bright orange highlight |
| | `table.edgeGlow` | `#EA580C` | Orange edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#FB923C` | Orange accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#C2410C` | Orange pot badge |
| | `pot.badgeRing` | `#FB923C` | Orange badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_orange` | `#FB923C` | Orange chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#FB923C` | Stack amounts |
| **Cards** | `board.cardBack` | `#C2410C` | Orange card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#FB923C` | Orange card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#FB923C` | Orange |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#C2410C` | Dark orange border |

### **🔷 Steel Blue** - *Modern Casino Steel*
| **Category** | **Element** | **Color Code** | **Description** |
|--------------|-------------|----------------|-----------------|
| **Table Surface** | `table.felt` | `#1E40AF` | Modern casino steel |
| | `table.rail` | `#1D4ED8` | Darker steel rail |
| | `table.railHighlight` | `#60A5FA` | Bright steel highlight |
| | `table.edgeGlow` | `#1D4ED8` | Steel edge glow |
| **Typography** | `text.primary` | `#FFFFFF` | White text |
| | `text.secondary` | `#E5E7EB` | Light gray text |
| | `text.accent` | `#60A5FA` | Steel accent text |
| **Backgrounds** | `primary_bg` | `#111827` | Dark background |
| | `secondary_bg` | `#1F2937` | Secondary background |
| | `panel.bg` | `#374151` | Panel background |
| | `panel.fg` | `#FFFFFF` | Panel foreground |
| **Pot & Chips** | `pot.badgeBg` | `#1E40AF` | Steel pot badge |
| | `pot.badgeRing` | `#60A5FA` | Steel badge ring |
| | `pot.valueText` | `#FFFFFF` | White pot text |
| | `chip_steel` | `#60A5FA` | Steel chips |
| **Player Seats** | `seat.bg.idle` | `#1F2937` | Idle seat |
| | `seat.bg.active` | `#374151` | Active seat |
| | `seat.bg.acting` | `#4B5563` | Acting seat |
| | `player.name` | `#E5E7EB` | Player names |
| | `player.stack` | `#60A5FA` | Stack amounts |
| **Cards** | `board.cardBack` | `#1E40AF` | Steel card backs |
| | `board.cardFaceFg` | `#FFFFFF` | White card text |
| | `board.border` | `#60A5FA` | Steel card borders |
| **Buttons** | `btn.default.bg` | `#374151` | Default button |
| | `btn.hover.bg` | `#4B5563` | Hover state |
| | `btn.active.bg` | `#6B7280` | Active state |
| **Dealer Button** | `dealer.buttonBg` | `#60A5FA` | Steel |
| | `dealer.buttonFg` | `#FFFFFF` | White text |
| | `dealer.buttonBorder` | `#1E40AF` | Dark steel border |

---

## 🎨 **TOKEN USAGE GUIDELINES**

### **Component Implementation**
```python
# ✅ Correct: Using theme tokens
button.configure(
    bg=theme_manager.get_token('btn.primary.bg'),
    fg=theme_manager.get_token('btn.primary.fg'),
    font=theme_manager.get_token('font.button')
)

# ❌ Incorrect: Hardcoded colors
button.configure(
    bg='#3B82F6',  # Don't hardcode!
    fg='#FFFFFF',
    font=('Arial', 12)
)
```

### **Theme Switching**
```python
def switch_theme(self, theme_name):
    # Load new theme
    self.theme_manager.load_theme(theme_name)
    
    # Re-render all components with new theme
    self._refresh_all_components()
    
    # Update theme selector
    self.theme_selector.set(theme_name)
```

### **Accessibility Compliance**
```python
def validate_contrast(self, bg_color, fg_color):
    """Ensure WCAG 2.1 AA compliance"""
    contrast_ratio = calculate_contrast_ratio(bg_color, fg_color)
    return contrast_ratio >= 4.5  # Minimum for normal text
```

---

## 📋 **MIGRATION CHECKLIST**

### **Phase 1: Token Standardization**
- [ ] Audit all hardcoded colors in components
- [ ] Create compatibility map for legacy tokens
- [ ] Update component implementations to use theme tokens
- [ ] Test theme switching functionality

### **Phase 2: Component Updates**
- [ ] Update Enhanced RPGW components
- [ ] Update session tab components
- [ ] Update button and control components
- [ ] Update text and label components

### **Phase 3: Testing & Validation**
- [ ] Test all themes for visual consistency
- [ ] Validate accessibility compliance
- [ ] Performance testing with theme switching
- [ ] User acceptance testing

---

*This document serves as the authoritative reference for all theme and color usage in the PokerPro Trainer. All components must use theme tokens and comply with accessibility standards.*
