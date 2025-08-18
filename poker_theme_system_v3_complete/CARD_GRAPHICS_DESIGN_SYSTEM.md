# 🃏 **Poker Card Graphics Design System**
## Custom Themed Card Decks Specification

### **📐 Card Specifications**

**Standard Dimensions:**
- **Community Cards**: 44×64 pixels (2:1 ratio to hole cards)
- **Hole Cards**: 22×32 pixels (consistent across all themes)
- **Aspect Ratio**: 11:16 (poker standard)
- **Corner Radius**: 3px for community, 2px for hole cards
- **Border Width**: 1px consistent across all cards

---

## **🎨 Theme-Specific Card Design System**

### **🌊 Monet Noir Collection**
**Color Palette**: Cool navy, silver, moonlight teal
**Card Back Design**: 
- Base: Deep midnight blue `#0F1A24`
- Pattern: Silver watercolor brushstrokes `#D7E2E8`
- Center motif: Stylized water lily in silver
- Border: Thin silver line `#C8D5DE`

**Card Face Design**:
- Background: Soft ivory `#F4F8FB` 
- Suit colors: Hearts/Diamonds in muted rose `#C5A3A3`, Spades/Clubs in charcoal `#2C3E50`
- Number/Face styling: Clean, impressionist-inspired typography
- Corner indices: Elegant serif font

---

### **🎭 Caravaggio Noir Collection** 
**Color Palette**: True black, vivid crimson, bright gold
**Card Back Design**:
- Base: Near-black `#0A0A0C`
- Pattern: Dramatic gold baroque scrollwork `#E1C16E`
- Center motif: Crimson rose with gold thorns
- Border: Bold gold frame `#E1C16E`

**Card Face Design**:
- Background: Cream parchment `#FFF7E6`
- Suit colors: Hearts/Diamonds in deep crimson `#B3122E`, Spades/Clubs in rich black `#0A0A0C`
- Number/Face styling: Bold, dramatic chiaroscuro shadows
- Corner indices: Strong serif with gold accents

---

### **🏛️ Klimt Royale Collection**
**Color Palette**: Warm obsidian, rich gold, emerald green
**Card Back Design**:
- Base: Warm obsidian `#17130E`
- Pattern: Intricate gold geometric Art Nouveau `#F4C430`
- Center motif: Emerald and gold mandala
- Border: Ornate gold filigree `#E4C97D`

**Card Face Design**:
- Background: Warm ivory with gold leaf texture `#FFF4D9`
- Suit colors: Hearts/Diamonds in emerald `#166A3E`, Spades/Clubs in obsidian `#17130E`
- Number/Face styling: Art Nouveau ornamental details
- Corner indices: Decorative gold-outlined font

---

### **🌙 Whistler Nocturne Collection**
**Color Palette**: Ethereal midnight blue, pewter, soft silver
**Card Back Design**:
- Base: Deep nocturne blue `#0D1B2A`
- Pattern: Subtle pewter mist effects `#B7C1C8`
- Center motif: Crescent moon and stars in silver
- Border: Soft pewter gradient `#96A3AF`

**Card Face Design**:
- Background: Soft moonlight white `#F8FAFC`
- Suit colors: Hearts/Diamonds in muted blue `#6EA3D6`, Spades/Clubs in charcoal `#32465E`
- Number/Face styling: Ethereal, atmospheric typography
- Corner indices: Gentle sans-serif with soft edges

---

### **💎 LV Noir Collection**
**Color Palette**: Deep mahogany, antique gold, luxury cream
**Card Back Design**:
- Base: Rich mahogany `#2A120F`
- Pattern: Antique gold monogram pattern `#C3A568`
- Center motif: Luxury crest with gold inlay
- Border: Embossed gold frame `#D4B76A`

**Card Face Design**:
- Background: Luxury cream `#F3EAD7`
- Suit colors: Hearts/Diamonds in burgundy `#8B2635`, Spades/Clubs in mahogany `#2A120F`
- Number/Face styling: Elegant luxury typography with gold accents
- Corner indices: Premium serif with subtle gold outline

---

### **🍷 Crimson Monogram Collection**
**Color Palette**: Rich burgundy, warm gold, deep cream
**Card Back Design**:
- Base: Deep burgundy `#3B0E11`
- Pattern: Interlocking gold monograms `#D4AF37`
- Center motif: Royal crest in gold
- Border: Ornate gold braiding `#E6C200`

**Card Face Design**:
- Background: Rich cream `#FFF9EE`
- Suit colors: Hearts/Diamonds in royal burgundy `#722F37`, Spades/Clubs in deep wine `#3B0E11`
- Number/Face styling: Regal, monogrammed details
- Corner indices: Royal serif with gold flourishes

---

### **⚫ Obsidian Emerald Collection**
**Color Palette**: Dark obsidian, emerald highlights, silver accents
**Card Back Design**:
- Base: Dark obsidian `#111A17`
- Pattern: Emerald geometric patterns `#2D5A3D`
- Center motif: Stylized emerald gem
- Border: Silver-green gradient `#7A9B7A`

**Card Face Design**:
- Background: Soft pearl `#F8F9FA`
- Suit colors: Hearts/Diamonds in emerald `#2D5A3D`, Spades/Clubs in obsidian `#111A17`
- Number/Face styling: Modern, geometric precision
- Corner indices: Clean sans-serif with emerald accents

---

### **🌟 Classic Professional Collections**

#### **Emerald Noir** (Tournament Standard)
- Card Back: Professional green `#1B4D3A` with subtle texture
- Pattern: Classic diamond weave in darker green
- Face: Clean white background, traditional red/black suits

#### **PokerStars Classic Pro**
- Card Back: Iconic tournament green `#1B4D3A` 
- Pattern: Professional star pattern in brown `#8B4513`
- Face: Tournament-standard white, bold suit colors

#### **WSOP Championship**
- Card Back: Championship burgundy `#8B1538`
- Pattern: Gold championship rings `#DAA520`
- Face: Premium white, enhanced suit definition

#### **Royal Casino Sapphire**
- Card Back: Deep sapphire `#0F2A44`
- Pattern: Royal crown motifs in silver
- Face: Luxury white with sapphire accents

#### **Emerald Professional**
- Card Back: Rich emerald `#2E5D4A`
- Pattern: Professional weave in brown `#654321`
- Face: Clean tournament standard

---

## **🎯 Implementation Specifications**

### **File Structure**
```
assets/cards/
├── themes/
│   ├── monet_noir/
│   │   ├── back.png
│   │   ├── faces/
│   │   │   ├── hearts/ (A-K)
│   │   │   ├── diamonds/ (A-K)
│   │   │   ├── clubs/ (A-K)
│   │   │   └── spades/ (A-K)
│   ├── caravaggio_noir/
│   ├── klimt_royale/
│   └── [all 14 themes...]
└── fallback/
    ├── default_back.png
    └── default_faces/
```

### **Technical Requirements**
- **Format**: PNG with alpha channel
- **Resolution**: 2x for retina displays (88×128 community, 44×64 hole)
- **Compression**: Optimized for web delivery
- **Naming**: `{theme_name}_{card_value}_{suit}.png`
- **Fallback**: Default deck for missing theme assets

### **Dynamic Loading System**
```python
class ThemeCardManager:
    def get_card_back(self, theme_name: str) -> str:
        """Return card back image path for theme"""
        
    def get_card_face(self, theme_name: str, card: str) -> str:
        """Return card face image path for theme and card"""
        
    def preload_theme_cards(self, theme_name: str):
        """Preload all cards for smooth theme switching"""
```

### **Card Animation System**
- **Deal Animation**: Cards slide from deck position with theme-appropriate motion
- **Flip Animation**: Smooth 3D flip revealing themed card faces
- **Hover Effects**: Subtle glow matching theme accent colors
- **Selection**: Border highlight using theme's primary color

### **Quality Standards**
- **Artistic Consistency**: Each theme's cards must feel cohesive with table design
- **Readability**: All card values clearly visible at both sizes
- **Performance**: Optimized loading and caching for smooth gameplay
- **Accessibility**: High contrast ratios for suit differentiation

---

## **🎨 Design Guidelines**

### **Color Harmony**
- Card backs must complement table felt colors
- Suit colors should maintain readability while matching theme
- Face backgrounds should provide sufficient contrast

### **Typography**
- Corner indices sized appropriately for card dimensions
- Font choices should reflect theme personality
- Consistent weight and spacing across all cards in theme

### **Pattern Design**
- Card back patterns should be subtle enough not to interfere with gameplay
- Motifs should be thematically appropriate and elegant
- Avoid overly busy designs that could cause visual fatigue

### **Cultural Sensitivity**
- All designs should be appropriate for international audiences
- Avoid religious or culturally specific symbols
- Focus on artistic and aesthetic elements

---

## **🚀 Implementation Priority**

**Phase 1**: Core 4 Painter Themes
1. Monet Noir - Impressionist elegance
2. Caravaggio Noir - Dramatic chiaroscuro  
3. Klimt Royale - Art Nouveau luxury
4. Whistler Nocturne - Atmospheric mystery

**Phase 2**: Luxury LV Collection
5. LV Noir - Premium mahogany
6. Crimson Monogram - Royal burgundy
7. Obsidian Emerald - Modern sophistication

**Phase 3**: Professional Tournament
8. PokerStars Classic Pro - Tournament standard
9. WSOP Championship - Championship prestige
10. Royal Casino Sapphire - Luxury gaming

**Phase 4**: Classic Collection
11. Emerald Noir - Traditional professional
12. Royal Indigo - Regal sophistication  
13. Crimson Gold - Vintage luxury
14. Emerald Professional - Modern tournament

This comprehensive card graphics system will create a truly immersive, themed poker experience where every visual element works in harmony! 🃏✨
