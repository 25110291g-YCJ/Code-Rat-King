# Code Rat King

Code Rat King is an exciting typing-based endless runner game built with Python and Pygame. Play as the "Code Rat King", type words to jump over obstacles, dodge enemies, and defeat bosses in this fast-paced adventure!

## Features

*   **Typing Gameplay:** Type the displayed words correctly to make your character jump and avoid obstacles.
*   **Endless Runner Action:** Run through different environments while dodging trees and houses.
*   **Multiple Levels:** Progress through distinct levels including Sky, Mine, and Volcano.
*   **Boss Battles:** Face off against challenging bosses like Simon, David, and Gio.
*   **Power-ups:** Collect items to aid your journey:
    *   **Health:** Restores HP.
    *   **Shield:** Provides temporary immunity.
    *   **Super Jump:** Boosts your next jump height.
    *   **Coin:** Grants bonus score points.
*   **Dynamic Difficulty:** The game gets faster and harder as you progress.
*   **Visual Effects:** Features parallax backgrounds, particle effects, and smooth animations.
*   **Ranking System:** Get graded based on your performance at the end of the run.

## Controls

*   **Typing (A-Z):** Type the word shown on screen to **JUMP**.
*   **Left Ctrl**: **SLIDE** (to dodge high obstacles).
*   **Space Bar**: Start Game / Toggle Tutorial / Pause.

## Installation

1.  Ensure you have Python 3.x installed on your system.
2.  Clone this repository or download the source code.
3.  Install the required dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

## How to Play

1.  Run the game script:

    ```bash
    python "Code Rat King.py"
    ```

2.  On the main menu, press **SPACE** to start.
3.  **Type the words** that appear above your character to jump over ground obstacles.
4.  **Press Left Ctrl** to slide under high obstacles or dodge attacks.
5.  Survive as long as possible and aim for a high score!

## Ranking System

Your performance is graded based on your final score:

*   **S**: 300+ Points
*   **A**: 250+ Points
*   **B**: 200+ Points
*   **C**: 150+ Points
*   **D**: 100+ Points
*   **E**: 50+ Points
*   **F**: Below 50 Points

## Building the Executable

To create a standalone `.exe` file that can be played without installing Python:

1.  Install PyInstaller and Pillow:
    ```bash
    pip install pyinstaller Pillow
    ```
2.  Generate the icon (optional, if `icon.ico` is missing):
    ```bash
    python convert_icon.py
    ```
3.  Build the game:
    ```bash
    pyinstaller --noconsole --onefile --icon=icon.ico --add-data "assets;assets" "Code Rat King.py"
    ```
4.  The executable will be located in the `dist/` folder.

## Project Structure

*   `Code Rat King.py`: The main game script.
*   `settings.py`: Game configuration and constants.
*   `player.py`: Player character logic and animations.
*   `text_target.py`: Typing mechanic implementation.
*   `background.py`: Parallax background management.
*   `assets/`: Contains all game assets (images, sounds, fonts).
*   `convert_icon.py`: Helper script to generate the game icon.

## Credits

*   **Owner:** 25110291g-YCJ
*   Built with [Pygame](https://www.pygame.org/).
