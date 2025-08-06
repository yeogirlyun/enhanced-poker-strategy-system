# 🎤 Voice Announcement System Setup Guide

## 🎯 Overview

The PokerPro Trainer now includes a professional casino-style voice announcement system that plays AI voices during poker actions like check, call, bet, raise, and fold.

## 📋 Available Voice Types

1. **dealer_male** - Professional male casino dealer
   - Style: authoritative, clear, casino-style
   - Best for: all announcements

2. **dealer_female** - Professional female casino dealer  
   - Style: friendly, clear, welcoming
   - Best for: all announcements

3. **announcer_male** - Casino announcer voice
   - Style: dramatic, exciting, tournament-style
   - Best for: big actions, all-ins, winners

4. **announcer_female** - Female casino announcer
   - Style: elegant, professional, sophisticated
   - Best for: all announcements

## 🎮 Supported Poker Actions

- **check** - "Check"
- **call** - "Call" 
- **bet** - "Bet"
- **raise** - "Raise"
- **fold** - "Fold"
- **all_in** - "All in!"
- **winner** - "Winner!"
- **your_turn** - "Your turn"
- **dealing** - "Dealing cards"
- **shuffling** - "Shuffling deck"

## 📁 Voice File Structure

Create this folder structure in your `sounds` directory:

```
sounds/voice/
├── dealer_male/
│   ├── check.wav
│   ├── call.wav
│   ├── bet.wav
│   ├── raise.wav
│   ├── fold.wav
│   ├── all_in.wav
│   ├── winner.wav
│   ├── your_turn.wav
│   ├── dealing.wav
│   └── shuffling.wav
├── dealer_female/
│   ├── check.wav
│   ├── call.wav
│   └── ... (same files)
├── announcer_male/
│   ├── check.wav
│   ├── call.wav
│   └── ... (same files)
└── announcer_female/
    ├── check.wav
    ├── call.wav
    └── ... (same files)
```

## 🚀 How to Use

### 1. Add Voice Files

1. **Get professional voice files** (WAV format recommended)
2. **Place them in the correct folders** as shown above
3. **Use descriptive filenames** like `check.wav`, `call.wav`, etc.

### 2. Configure in GUI

1. **Launch the app**: `python3 launch_pokerpro.py`
2. **Open Settings**: Click the settings menu
3. **Go to Sound Settings**: Click "🎵 Sound Settings"
4. **Access Voice Settings**: Click "🎤 Voice Settings"
5. **Test voices**: Use the test buttons to hear your voice files
6. **Change voice type**: Select different voice types from the dropdown

### 3. Voice Settings Panel Features

- **Voice Type Selection**: Choose between dealer_male, dealer_female, announcer_male, announcer_female
- **Test Buttons**: Test individual voice announcements
- **Volume Control**: Adjust voice volume
- **Enable/Disable**: Turn voice announcements on/off

## 🎮 Integration with Poker Game

### Automatic Voice Playback

Voices play automatically during poker actions:

- **Check**: "Check" voice plays
- **Call**: "Call" voice plays  
- **Bet**: "Bet" voice plays
- **Raise**: "Raise" voice plays
- **Fold**: "Fold" voice plays
- **All-in**: "All in!" voice plays
- **Winner**: "Winner!" voice plays

### Combined Sound + Voice

The system plays both:
1. **Sound effects** (chips, cards, etc.)
2. **Voice announcements** (professional casino voices)

## ⚙️ Configuration Options

### Voice Type Selection
```python
# Change voice type programmatically
voice_system.set_voice_type('dealer_female')
```

### Volume Control
```python
# Adjust voice volume
voice_system.set_volume(0.8)  # 80% volume
```

### Enable/Disable
```python
# Disable voice announcements
voice_system.disable_voices()

# Enable voice announcements  
voice_system.enable_voices()
```

## 🎯 Example Usage

### Basic Voice Announcement
```python
from voice_announcement_system import voice_system

# Play a voice announcement
voice_system.play_voice_announcement('check')
voice_system.play_voice_announcement('call')
voice_system.play_voice_announcement('raise')
```

### Combined Action with Voice
```python
# Play action with both sound and voice
voice_system.play_action_with_voice('player_bet', amount=50)
voice_system.play_action_with_voice('player_call', amount=25)
```

### Change Voice Type
```python
# Switch to female dealer voice
voice_system.set_voice_type('dealer_female')
voice_system.play_voice_announcement('check')
```

## 🔧 Troubleshooting

### No Voice Files Found
- **Solution**: Add voice files to `sounds/voice/[voice_type]/` folders
- **Check**: Ensure files are named correctly (e.g., `check.wav`)

### Voice Not Playing
- **Check**: Voice files are in correct format (WAV recommended)
- **Check**: File permissions allow reading
- **Check**: Voice system is enabled in settings

### Wrong Voice Type
- **Solution**: Change voice type in GUI or programmatically
- **Check**: Voice files exist for selected voice type

## 🎉 Benefits

1. **Professional Experience**: Casino-style voice announcements
2. **Immersive Gameplay**: Combines sounds + voices
3. **Multiple Voice Types**: Choose your preferred style
4. **Automatic Integration**: Works seamlessly with poker actions
5. **Customizable**: Easy to add your own voice files

## 📝 Next Steps

1. **Add voice files** to the `sounds/voice/` directories
2. **Test in GUI** using the voice settings panel
3. **Play a practice session** to hear voices during actual poker actions
4. **Customize** voice types and volumes to your preference

The voice system is now fully integrated and will enhance your poker training experience with professional casino-style announcements! 🎤 