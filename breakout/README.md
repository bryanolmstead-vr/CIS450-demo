# Breakout

Open `index.html` directly in a modern desktop browser. No installation,
server, internet connection, or build step is needed. Keep the three application
files together.

Click **Start game** or press **Space**. Hold the left or right arrow key to move
the paddle, and release it to stop. Clear all 30 bricks to win. A miss ends the
game and resets the ball and paddle; the final score and remaining bricks stay
visible until restart. Space or **Restart game** starts a fresh game at any time.

## Manual acceptance checks

1. Open the file with the network disconnected. Confirm the ready message,
   score 0, centered ball/paddle, and three rows of ten royal-blue bricks.
   The bricks should reach both edges of the playing area.
2. Start with the button, then restart using Space. Hold each arrow key to its
   boundary. The paddle should remain inside the area and stop on release.
   Switch windows while holding a key; returning should not leave it moving.
3. Observe the ball bouncing off the top and both side walls, and returning
   upward after hitting the paddle. Watch brick top/bottom and side impacts:
   they should reverse vertical and horizontal movement respectively.
4. Check that each destroyed brick disappears and adds exactly one point.
   Revisiting its empty space must not add another point.
5. Move away from the falling ball. Confirm **Game Over**, stopped gameplay,
   and the ball/paddle back at their starting positions. Wait a few seconds:
   neither score nor ball position should change.
6. Restart after losing. Confirm score 0, all 30 bricks restored, starting
   positions restored, and a moving ball.
7. Clear all bricks. Confirm score 30, **You win!**, and stopped gameplay.
   Restart and confirm a fresh game. Also try restarting during active play.
8. Check the browser console for errors and resize the window to ensure the
   playing area remains visible with its proportions preserved.

Implementation checks performed: file references, brick count and edge coverage,
required color, and source whitespace. Browser execution, visual inspection,
interactive gameplay, and full win/loss acceptance tests have not been performed.

## Files and license

- `index.html`: game area, score, instructions, and controls.
- `style.css`: page and responsive canvas styling.
- `game.js`: drawing, keyboard input, physics, scoring, and game states.

The implementation uses original code and no third-party assets or dependencies.
It is distributed under the existing MIT `LICENSE`; retain that license with
copies or substantial portions of the software.
