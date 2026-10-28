# Breakout

Open `index.html` directly in a modern desktop browser. No installation,
server, internet connection, or build step is needed.

Click **Start game** or press **Space**. Hold the left or right arrow key to
move the paddle; release it to stop. Clear all 50 bricks to win.

You start with three lives. A miss consumes one life and pauses play with the
ball and paddle reset. Press Space or **Continue** to launch again, preserving
score and remaining bricks. During play, Space or **Reset ball** also resets
positions without clearing progress. After Game Over or a win, Space or
**Restart game** restores all bricks, score zero, and three lives.

The specification contains older references to three rows and ending the game
after one miss. This implementation follows the more specific five-row and
three-life requirements. Continuing with lives remaining preserves progress;
restarting after a final loss or win starts a fresh game.

## Manual acceptance checks

1. Open the file offline. Confirm ready state, score 0, three lives, and five
   rows of ten bricks: red, orange, yellow, green, blue from top to bottom.
   Both side margins should equal half a brick width.
2. Start with the button and test Space. Hold each arrow key to its boundary.
   Verify the paddle stays inside and stops on release. Switch windows while
   holding a key; returning should not leave it moving.
3. Observe wall and paddle bounces. Brick top/bottom hits should reverse vertical
   movement; side hits should reverse horizontal movement. Check for tunneling.
4. Verify each destroyed brick disappears and adds one point exactly once.
5. Miss deliberately. Confirm two lives remain, play stops, positions reset,
   and score and destroyed bricks remain unchanged. Continue and repeat for
   one remaining life. The third miss should show Game Over and stop play.
6. Restart after Game Over. Confirm score 0, three lives, and 50 restored bricks.
7. Clear all bricks. Confirm score 50, You win!, and stopped play. Restart and
   verify a fresh game. During play, Reset ball should preserve progress.
8. Check the browser console for errors and resize the window to inspect layout.

## Verification performed

Executed the actual game JavaScript in a JavaScript runtime with stubbed DOM,
canvas, and animation APIs. All 29 assertions passed, covering initial state,
row colors, margins, paddle bounds/stopping, wall/paddle/brick collisions,
one-time scoring, all three misses, continuation, stopped end states, and
fresh games after win/loss. These are controlled logic checks, not browser tests.
Browser rendering, real keyboard input, and a complete interactive playthrough
have not been tested. Source whitespace checks also passed.

## Files and license

- `index.html`: game area, score, lives, instructions, and controls.
- `style.css`: page and responsive canvas styling.
- `game.js`: drawing, input, physics, scoring, lives, and game states.

The implementation uses original code and no third-party assets or dependencies.
The existing MIT `LICENSE` is unchanged; retain it with copies or substantial
portions of the software.
