// Original project code; distributed under the MIT license in LICENSE.
"use strict";

const canvas = document.getElementById("game");
const context = canvas.getContext("2d");
const scoreDisplay = document.getElementById("score");
const livesDisplay = document.getElementById("lives");
const statusDisplay = document.getElementById("status");
const startButton = document.getElementById("start");
const width = canvas.width;
const height = canvas.height;
const keys = { left: false, right: false };
const paddle = { x: 0, y: height - 36, width: 112, height: 14, speed: 470 };
const ball = { x: 0, y: 0, radius: 8, vx: 185, vy: -285 };
let bricks = [];
let score = 0;
let lives = 3;
const rowColors = ["#ff0000", "#ffa500", "#ffff00", "#008000", "#0000ff"];
let state = "ready";
let previousTime = null;

function resetPositions() {
  paddle.x = (width - paddle.width) / 2;
  ball.x = width / 2;
  ball.y = paddle.y - ball.radius - 2;
  ball.vx = 185;
  ball.vy = -285;
}

function resetGame() {
  score = 0;
  scoreDisplay.textContent = score;
  lives = 3;
  livesDisplay.textContent = lives;
  bricks = [];
  // Ten bricks plus two half-brick margins occupy eleven brick widths.
  const brickWidth = width / 11;
  for (let row = 0; row < rowColors.length; row++) {
    for (let column = 0; column < 10; column++) {
      bricks.push({ x: brickWidth / 2 + column * brickWidth, y: 54 + row * 26,
        width: brickWidth, height: 26, color: rowColors[row], alive: true });
    }
  }
  keys.left = false;
  keys.right = false;
  resetPositions();
}

function startGame() {
  // Launching another chance preserves progress while lives remain.
  if (state === "ready" || state === "won" || state === "lost") resetGame();
  else resetPositions();
  state = "playing";
  previousTime = null;
  statusDisplay.textContent = "Playing — use the left and right arrow keys.";
  startButton.textContent = "Reset ball";
}

function finishGame(won) {
  state = won ? "won" : "lost";
  statusDisplay.textContent = won
    ? "You win! All 50 bricks cleared. Press Space or Restart game."
    : "Game Over — press Space or Restart game to try again.";
  if (!won) resetPositions();
  startButton.textContent = "Restart game";
}

function loseLife() {
  lives--;
  livesDisplay.textContent = lives;
  if (lives === 0) {
    finishGame(false);
    return;
  }
  resetPositions();
  keys.left = false;
  keys.right = false;
  state = "waiting";
  statusDisplay.textContent = `Life lost. ${lives} lives left — press Space or Continue.`;
  startButton.textContent = "Continue";
}

// Resolve a circle against a rectangle using the closest point. The contact
// normal distinguishes side hits from top/bottom hits, including corner hits.
function bounceOffRectangle(rectangle) {
  const closestX = Math.max(rectangle.x, Math.min(ball.x, rectangle.x + rectangle.width));
  const closestY = Math.max(rectangle.y, Math.min(ball.y, rectangle.y + rectangle.height));
  const dx = ball.x - closestX;
  const dy = ball.y - closestY;
  const distance = Math.hypot(dx, dy);
  if (distance >= ball.radius) return false;

  let nx = 0;
  let ny = 0;
  let penetration;
  if (distance > 0) {
    // Choose the impacted face so a side hit reverses only horizontal motion.
    if (Math.abs(dx) > Math.abs(dy)) nx = Math.sign(dx);
    else ny = Math.sign(dy);
    penetration = ball.radius - (nx ? Math.abs(dx) : Math.abs(dy));
  } else {
    const faces = [
      { depth: ball.x - rectangle.x, x: -1, y: 0 },
      { depth: rectangle.x + rectangle.width - ball.x, x: 1, y: 0 },
      { depth: ball.y - rectangle.y, x: 0, y: -1 },
      { depth: rectangle.y + rectangle.height - ball.y, x: 0, y: 1 }
    ];
    const face = faces.reduce((a, b) => a.depth < b.depth ? a : b);
    nx = face.x;
    ny = face.y;
    penetration = ball.radius + face.depth;
  }
  ball.x += nx * penetration;
  ball.y += ny * penetration;
  if (ball.vx * nx + ball.vy * ny < 0) {
    if (nx) ball.vx = -ball.vx;
    if (ny) ball.vy = -ball.vy;
  }
  return true;
}

function update(seconds) {
  // Substeps keep ball and paddle travel below two pixels per collision check.
  const steps = Math.ceil(seconds * Math.max(paddle.speed, Math.hypot(ball.vx, ball.vy)) / 2);
  if (!steps) return;
  const dt = seconds / steps;
  for (let step = 0; step < steps && state === "playing"; step++) {
    const direction = Number(keys.right) - Number(keys.left);
    paddle.x = Math.max(0, Math.min(width - paddle.width, paddle.x + direction * paddle.speed * dt));
    ball.x += ball.vx * dt;
    ball.y += ball.vy * dt;
    if (ball.x < ball.radius) {
      ball.x = ball.radius;
      ball.vx = Math.abs(ball.vx);
    } else if (ball.x > width - ball.radius) {
      ball.x = width - ball.radius;
      ball.vx = -Math.abs(ball.vx);
    }
    if (ball.y < ball.radius) {
      ball.y = ball.radius;
      ball.vy = Math.abs(ball.vy);
    }
    if (ball.vy > 0) bounceOffRectangle(paddle);
    for (const brick of bricks) {
      if (brick.alive && bounceOffRectangle(brick)) {
        brick.alive = false;
        score++;
        scoreDisplay.textContent = score;
        if (score === bricks.length) finishGame(true);
        break;
      }
    }
    if (state === "playing" && ball.y - ball.radius > paddle.y + paddle.height) loseLife();
  }
}

function draw() {
  context.clearRect(0, 0, width, height);
  for (const brick of bricks) {
    if (!brick.alive) continue;
    context.fillStyle = brick.color;
    context.fillRect(brick.x, brick.y, brick.width, brick.height);
    // Inset outlines distinguish neighboring bricks.
    context.strokeStyle = "#080d17";
    context.strokeRect(brick.x + 0.5, brick.y + 0.5, brick.width - 1, brick.height - 1);
  }
  context.fillStyle = "#edf2fc";
  context.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
  context.beginPath();
  context.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
  context.fill();
  if (state !== "playing") {
    context.fillStyle = "#edf2fc";
    context.font = "bold 32px system-ui";
    context.textAlign = "center";
    const message = state === "ready" ? "Ready to play" : state === "won" ? "You win!"
      : state === "waiting" ? "Life lost — press Space" : "Game Over";
    context.fillText(message, width / 2, height / 2);
  }
}

function frame(time) {
  // Ignore long background-tab delays instead of jumping through the board.
  if (previousTime !== null && state === "playing") update(Math.min((time - previousTime) / 1000, 0.05));
  previousTime = time;
  draw();
  requestAnimationFrame(frame);
}

document.addEventListener("keydown", (event) => {
  if (["ArrowLeft", "ArrowRight", "Space"].includes(event.code)) event.preventDefault();
  if (event.code === "ArrowLeft") keys.left = true;
  if (event.code === "ArrowRight") keys.right = true;
  if (event.code === "Space" && !event.repeat) startGame();
});
document.addEventListener("keyup", (event) => {
  if (event.code === "ArrowLeft") keys.left = false;
  if (event.code === "ArrowRight") keys.right = false;
});
window.addEventListener("blur", () => { keys.left = false; keys.right = false; });
startButton.addEventListener("click", startGame);
resetGame();
requestAnimationFrame(frame);
