# Word Crush: A Fun and Interactive Word Puzzle Game

Word Crush is an engaging puzzle game that combines word-finding strategy with tile-swapping mechanics. Players swap letter tiles strategically to create valid English words while managing limited moves and time.

## 🎮 Game Overview

Word Crush challenges you to create words by swapping adjacent letter tiles. The game features:

- A 6×6 grid of letter tiles with strategic letter distribution
- Score system based on Scrabble-style letter values
- Time limit of 3 minutes per game
- Limited moves (10) that must be used strategically
- Chain reaction mechanics when multiple words form
- Hint system to suggest optimal moves

## 📖 How to Play

1. **Objective**: Create valid English words (3+ letters) by swapping adjacent tiles to earn points
2. **Controls**: 
   - Click on a tile to select it
   - Click an adjacent tile to swap positions
   - Click the "Hint" button (up to 3 times per game) for move suggestions
3. **Scoring**:
   - Each letter has a point value (rare letters like Q, Z, X are worth more)
   - Longer words earn more points
   - Chain reactions occur when word removals create new words

## 🎬 Demo Video

[Insert demo video here]

## ✨ Features

### Game Mechanics
- **Smart Letter Distribution**: Balanced algorithm ensures playable but challenging grid
- **Chain Reactions**: Words automatically clear and create cascading matches
- **Strategic Hint System**: Limited hints show the most valuable possible swaps

### Visual Elements
- **Elegant Purple UI**: Smooth gradients and animations create a polished experience
- **Feedback Animations**: 
  - Word highlights with connecting lines
  - Tile drop animations
  - Score pop-ups
  - Particle effects for matched words

### Technical Implementation
- **Efficient Word Checking**: Uses NLTK corpus for comprehensive dictionary
- **Fallback Systems**: Mini-dictionary available if NLTK not installed
- **Strategic Grid Generation**: Algorithm creates grids with minimal pre-formed words
- **Performance Optimizations**: Score caching and efficient position tracking

## 🛠️ Installation

1. Ensure you have Python installed (3.6+ recommended)
2. Install required packages:
   ```
   pip install pygame
   pip install nltk
   ```
3. Run the game:
   ```
   python wordcrush.py
   ```

## 🧠 Strategy Tips

- Look for high-value letters (Q, Z, J, X) and position them strategically
- Plan multi-word combos by setting up chain reactions
- Save hints for critical moments when stuck
- Watch the timer - prioritize quick, valuable moves as time runs low
- Focus on creating long words rather than many short ones

## 🔜 Future Enhancements

- Leaderboard system to track high scores
- Difficulty levels with different grid sizes
- Alternative game modes (endless, challenge, etc.)
- Word themes and categories
- Mobile touch support

## 📝 Credits

Developed as a Python project exploring game design, AI algorithms, and interactive graphics with Pygame.

---

Enjoy playing Word Crush! Feel free to contribute or provide feedback to help improve the game.