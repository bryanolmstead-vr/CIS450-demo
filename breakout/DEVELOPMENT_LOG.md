# Development Log - Breakout

Bryan Olmstead
2026.10.27

## First Prompt

Read `AGENTS.md`, `SPEC.md`, and `LICENSE` before beginning.

Implement the Breakout game described in `SPEC.md`, following the instructions in `AGENTS.md` and the licensing requirements in `LICENSE`.

Create all necessary application files, including `index.html` and any CSS or JavaScript files you need. Keep the implementation simple and do not introduce external dependencies.

After implementation, summarize the files you created, explain how to run the game, and describe how to test it against the requirements in `SPEC.md`. Be honest about any tests you have not actually performed.

## First Test

1. The game opens in a browser without installation or build steps. PASS
2. The player can start the game and move the paddle with the keyboard. PASS
3. The paddle remains inside the game boundaries. PASS
4. The ball bounces off the walls and paddle. PASS
5. Bricks disappear when hit, and the score increases correctly. PASS
6. Missing the paddle causes the ball to reset without breaking the game. PASS
7. The game ends after a missed ball. PASS
8. Destroying all bricks produces a win state. PASS
9. The player can restart and play a fresh game. PASS
10. No external dependencies are required. PASS

## Modified Spec

Made modification to spec to be more realistic to original Atari game.

## Second Test

1. 5 rows of bricks: red, orange, yellow, green, blue. PASS
2. half brick gap on left and right. PASS
3. 3 lives. PASS