import pygame
import cv2
import mediapipe as mp
import random
import sys
import time

# --- Configuration ---
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 7  # Snake speed (Slower for better control)ī

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        
        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            sys.exit()

    def get_direction(self):
        """
        Reads a frame from the webcam, processes it for hand landmarks,
        and determines the direction based on the hand's position relative to the center.
        Returns:
            direction (tuple or None): The detected direction (UP, DOWN, LEFT, RIGHT) or None.
            frame (numpy array): The annotated camera frame to display.
        """
        success, frame = self.cap.read()
        if not success:
            return None, None

        # Flip frame horizontally for mirror effect (more intuitive)
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        center_x, center_y = w // 2, h // 2
        
        # Convert to RGB for MediaPipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        direction = None
        
        # Draw "Joystick" Zones on the frame for visual feedback
        # Central Neutral Zone
        zone_radius = 80
        cv2.circle(frame, (center_x, center_y), zone_radius, (255, 255, 255), 2)
        
        # Draw lines separating sectors
        cv2.line(frame, (0, 0), (w, h), (50, 50, 50), 1)
        cv2.line(frame, (w, 0), (0, h), (50, 50, 50), 1)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Use the index finger tip position for pointing
                landmark = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP] 
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                
                # Draw a circle at the tracking point
                cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)

                # Determine direction based on position relative to center
                dx = cx - center_x
                dy = cy - center_y
                
                # Check if outside the neutral zone
                if dx**2 + dy**2 > zone_radius**2:
                    if abs(dx) > abs(dy):
                        # Horizontal movement
                        if dx > 0:
                            direction = RIGHT
                            cv2.putText(frame, "RIGHT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            direction = LEFT
                            cv2.putText(frame, "LEFT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        # Vertical movement
                        if dy > 0:
                            direction = DOWN
                            cv2.putText(frame, "DOWN", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            direction = UP
                            cv2.putText(frame, "UP", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "NEUTRAL", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        return direction, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Hand Controlled Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.reset_game()

    def reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.direction_cooldown = 0

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def handle_input(self, new_direction):
        if self.direction_cooldown > 0:
            self.direction_cooldown -= 1
            return

        # Prevent reversing direction directly
        if new_direction:
            if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
                self.direction = new_direction
                self.direction_cooldown = 2  # Small delay to prevent twitching

    def update(self):
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collisions
        # Screen Wrap Logic
        if new_head[0] < 0:
            new_head = (GRID_WIDTH - 1, new_head[1])
        elif new_head[0] >= GRID_WIDTH:
            new_head = (0, new_head[1])
        
        if new_head[1] < 0:
            new_head = (new_head[0], GRID_HEIGHT - 1)
        elif new_head[1] >= GRID_HEIGHT:
            new_head = (new_head[0], 0)

        # Check self-collision only
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw(self):
        self.screen.fill(BLACK)

        # Draw Snake
        # Draw Snake with improved visuals
        for i, segment in enumerate(self.snake):
            x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
            center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
            
            if i == 0:
                # Draw Head
                pygame.draw.circle(self.screen, (0, 200, 0), center, GRID_SIZE // 2 + 2)
                
                # Eyes
                eye_radius = 3
                pupil_radius = 1
                
                # Determine eye positions based on direction
                dx, dy = self.direction
                if dx == 1: # Right
                    eye1 = (center[0] + 4, center[1] - 4)
                    eye2 = (center[0] + 4, center[1] + 4)
                elif dx == -1: # Left
                    eye1 = (center[0] - 4, center[1] - 4)
                    eye2 = (center[0] - 4, center[1] + 4)
                elif dy == -1: # Up
                    eye1 = (center[0] - 4, center[1] - 4)
                    eye2 = (center[0] + 4, center[1] - 4)
                else: # Down
                    eye1 = (center[0] - 4, center[1] + 4)
                    eye2 = (center[0] + 4, center[1] + 4)

                pygame.draw.circle(self.screen, WHITE, eye1, eye_radius)
                pygame.draw.circle(self.screen, WHITE, eye2, eye_radius)
                pygame.draw.circle(self.screen, BLACK, eye1, pupil_radius)
                pygame.draw.circle(self.screen, BLACK, eye2, pupil_radius)
                
                # Tongue
                tongue_length = 8
                tongue_end = (center[0] + dx * tongue_length, center[1] + dy * tongue_length)
                pygame.draw.line(self.screen, RED, center, tongue_end, 2)

            else:
                # Draw Body (Alternating colors)
                color = (0, 255, 0) if i % 2 == 0 else (0, 200, 0)
                rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect, border_radius=4)

        # Draw Food
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, RED, food_rect)

        # Draw Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if not self.game_over:
            info = self.font.render("Show hand and move it away from center to steer", True, GRAY)
            self.screen.blit(info, (10, 40))

        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
            
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 20))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

def main():
    tracker = HandTracker()
    game = SnakeGame()

    running = True
    while running:
        # 1. Handle Pygame Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game.reset_game()
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 2. Get Hand Input
        hand_direction, frame = tracker.get_direction()
        
        # 3. Update Game State
        if not game.game_over:
            game.handle_input(hand_direction)
            game.update()
        
        # 4. Draw Game
        game.draw()

        # 5. Show Camera Feed
        if frame is not None:
            cv2.imshow("Hand Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False

        # Control Game Speed
        game.clock.tick(FPS)

    tracker.release()
    pygame.quit()

if __name__ == "__main__":
    main()
