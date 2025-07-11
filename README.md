# AI Courtroom Mystery Games

Interactive text-based courtroom mystery games inspired by the Ace Attorney series, powered by AI game masters.

## About This Project

This project creates compelling courtroom mystery experiences through AI collaboration, combining:
- **Investigation phases** with evidence gathering and character interviews
- **Trial phases** with dramatic cross-examinations and witness confrontations
- **Logical consistency** where all evidence chains align perfectly
- **Dynamic storytelling** powered by AI improvisation with entropy prevention
- **Dice-based action resolution** that rewards strategic thinking

## Inspiration

These games are inspired by the Ace Attorney series, particularly the investigation → trial gameplay loop that made those games so compelling. However, this project features entirely original characters, cases, and storylines, making it accessible to newcomers while capturing the essence of what makes courtroom mysteries engaging.

Like other Ace Attorney-inspired games such as Paper Perjury and Aviary Attorney, this project pays homage to the original series while creating something new and unique.

## Key Features

- **Dynamic Case Generation**: Each case is procedurally created using real-world legal inspiration
- **Evidence-Based Progression**: Players must present the right evidence to the right people to advance
- **Dice-Driven Outcomes**: Strategic choices are rewarded with bonuses to dice rolls
- **Compelling Characters**: Original characters with complex motivations and relationships
- **Locked Room Mysteries**: Creative puzzles that require logical deduction to solve
- **Dramatic Courtroom Battles**: Cross-examinations leading to breakthrough confessions

## Game Structure

### Investigation Phase
- Gather evidence from crime scenes
- Interview witnesses and suspects
- Build trust with cooperative characters
- Overcome hostile characters with evidence presentation

### Trial Phase
- Present opening statements
- Cross-examine witnesses
- Object to testimony
- Present evidence to contradict lies
- Achieve dramatic witness breakdowns

### Resolution
- Expose the real killer through logical deduction
- Explain the complete method and motive
- Achieve justice for your client

## Technology

- **AI Game Master**: Claude provides logical consistency and story backbone
- **Creative Obstacles**: ChatGPT generates dramatic tension and challenges
- **Entropy Prevention**: Random word inspiration forces creative breakthrough moments
- **State Management**: Comprehensive tracking of evidence, relationships, and progress

## Installation

### Prerequisites

1. **Install Claude Code**: Follow the installation instructions at [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)

2. **Clone or Download**: Get this project repository on your local machine

3. **Set up Python Environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install required packages
   pip install -r requirements.txt
   ```

4. **Configure OpenAI API Key**:
   - Create a file called `openai_key.txt` in the project root directory
   - Add your OpenAI API key to this file (single line, no quotes)
   - This file is gitignored for security - never commit API keys to version control

### Getting Started

1. **Activate the virtual environment**: `source venv/bin/activate`
2. **Create a new game**: `create new game` (within Claude Code - requires AI collaboration)
3. **Begin playing**: `start game [case_name]`

### Testing the Installation

Run the test suite to ensure everything is working correctly:
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

### Quick Start Verification

Test that all systems are working:
```bash
# Activate virtual environment
source venv/bin/activate

# Test the game state manager
python3 scripts/game_state_manager.py --help

# Test random word generation
python3 -c "from wonderwords import RandomWord; r = RandomWord(); print('Random word test:', r.word())"
```

### Troubleshooting

**Virtual Environment Issues:**
- Make sure you're in the project directory when creating the virtual environment
- Always activate with `source venv/bin/activate` before running any scripts
- If you see "command not found" errors, the virtual environment may not be activated

**Package Installation Issues:**
- If pip install fails, try updating pip first: `pip install --upgrade pip`
- On some systems, you may need to use `python3 -m pip` instead of just `pip`

**OpenAI API Key Issues:**
- Make sure `openai_key.txt` is in the project root directory (same level as README.md)
- The file should contain only your API key on a single line with no quotes or extra characters
- Verify your OpenAI API key is valid and has sufficient credits

**Claude Code Issues:**
- Make sure Claude Code is properly installed and configured
- The project requires Claude Code to create and play games
- See the [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code) for installation help

## Project Structure

```
claude_mystery_games/
├── README.md                 # This file
├── CLAUDE.md                 # Main project documentation and commands
├── requirements.txt          # Python dependencies
├── openai_key.txt           # Your OpenAI API key (create this file)
├── .gitignore               # Git ignore patterns
├── venv/                    # Virtual environment (created by you)
├── config/                  # Shared configuration files
├── scripts/                 # Core game scripts
│   ├── game_state_manager.py    # Main game state management
│   ├── create_new_game_orchestrator.py  # Case creation system
│   └── ...                  # Other utilities
├── tests/                   # Test suite
├── docs/                    # Documentation and examples
├── previous_cases/          # Archive of completed cases
└── [case_name]/             # Active case directories (created by system)
    ├── backbone/            # Case structure and facts
    ├── obstacles/           # ChatGPT-generated challenges
    ├── solution/            # Encoded solution files
    ├── game_state/          # Current progress tracking
    └── saves/               # Save points
```

## Legal

This project is inspired by but not affiliated with the Ace Attorney series. All characters, cases, and storylines are original creations. The project pays tribute to the gameplay mechanics and storytelling style that made the original series compelling while creating entirely new content.