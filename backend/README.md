# Janggi (Korean Chess) Game

A Python implementation of Janggi, the traditional Korean chess game.

## 🎮 About Janggi

Janggi (장기) is a traditional Korean board game similar to Chinese Xiangqi and Western Chess. It features unique pieces and movement patterns that make it distinct from other chess variants.

## 🚀 Features

- **Complete Janggi Game Engine**: Full implementation of Janggi rules
- **Graphical User Interface**: Modern GUI for playing Janggi
- **AI Opponent**: Computer player with different difficulty levels
- **Game Analysis**: Move validation and game state tracking
- **Save/Load Games**: Persistence for ongoing games

## 📁 Project Structure

```
Janggi/
├── src/           # Main source code
├── tests/         # Unit tests
├── docs/          # Documentation
├── requirements.txt
└── README.md
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Janggi
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python src/main.py
```

## 🎯 Game Rules

### Board Setup
- 9x10 board with palace areas
- 16 pieces per player (Red vs Blue)
- Initial setup follows traditional Janggi rules

### Piece Movements
- **General (King)**: Moves within palace, one step orthogonally
- **Advisors**: Move diagonally within palace
- **Elephants**: Move two steps diagonally
- **Horses**: Move like knight in Western chess
- **Chariots**: Move like rooks in Western chess
- **Cannons**: Move like chariots but capture by jumping over one piece
- **Soldiers**: Move forward or sideways one step

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📚 References

- [Janggi Wikipedia](https://en.wikipedia.org/wiki/Janggi)
- [Korean Chess Rules](https://www.chessvariants.com/rules/janggi) 