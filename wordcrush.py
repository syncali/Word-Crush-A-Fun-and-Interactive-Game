import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 700  # Extra space for header
GRID_SIZE = 6
TILE_SIZE = WIDTH // GRID_SIZE
HEADER_HEIGHT = 100
ANIMATION_SPEED = 15
TOTAL_MOVES = 10  # Set initial move count
TIMER_START = 180  # 3 minutes in seconds

# Scrabble letter scores
LETTER_SCORES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1,
    "J": 8, "K": 5, "L": 1, "M": 3, "N": 1, "O": 1, "P": 3, "Q": 10, "R": 1,
    "S": 1, "T": 1, "U": 1, "V": 4, "W": 4, "X": 8, "Y": 4, "Z": 10
}

# Colors
WHITE = (255, 255, 255)
DARK_PURPLE = (100, 0, 180)
LIGHT_PURPLE = (150, 50, 220)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (70, 70, 70, 100)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)  # For highlighting valid words

# Fonts
FONT = pygame.font.Font(None, 50)
HEADER_FONT = pygame.font.Font(None, 40)
SCORE_FONT = pygame.font.Font(None, 20)

# Load dictionary of valid English words using NLTK
try:
    import nltk
    from nltk.corpus import words
    
    # Download words corpus if not already present
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words', quiet=True)
    
    # Get all words and convert to uppercase for case-insensitive matching
    word_list = {word.upper() for word in words.words() if len(word) >= 3}
    print(f"Loaded {len(word_list)} words from NLTK corpus")
except ImportError:
    print("NLTK not installed, using fallback dictionary")
    # Minimal dictionary as fallback
    word_list = {"CAT", "DOG", "PIG", "BAT", "HAT", "RUN", "SIT", "FLY", "BIG", 
                "RED", "MAP", "PIN", "CUP", "BOX", "CAR", "BUS", "SUN", "AIR",
                "SEA", "TOP", "LOW", "HOT", "ICE", "ONE", "TWO", "EAT", "TEN"}

# Letter Pool
LETTERS = list(LETTER_SCORES.keys())
grid = [[random.choice(LETTERS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Puzzle Game")

selected_tile = None
moves_left = TOTAL_MOVES
score = 0
start_time = time.time()


def draw_gradient_tile(surface, x, y, width, height, color1, color2, opacity=255):
    """Creates a gradient effect from top to bottom inside a tile."""
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        r = color1[0] + (color2[0] - color1[0]) * (i / height)
        g = color1[1] + (color2[1] - color1[1]) * (i / height)
        b = color1[2] + (color2[2] - color1[2]) * (i / height)
        pygame.draw.line(temp_surface, (int(r), int(g), int(b), opacity), (0, i), (width, i))
    surface.blit(temp_surface, (x, y))


def draw_grid():
    """Draws the letter grid."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * TILE_SIZE, row * TILE_SIZE + HEADER_HEIGHT  # Offset for header
            opacity = 200 if selected_tile == (row, col) else 255
            draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, opacity)
            pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
            
            letter = grid[row][col]
            text_surface = FONT.render(letter, True, TEXT_COLOR)
            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)

            # Center letter
            screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
            # Display score at bottom right
            screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))


def draw_header():
    """Displays the timer, moves left, and score in a tabular format."""
    global moves_left, score
    screen.fill(WHITE, (0, 0, WIDTH, HEADER_HEIGHT))  # Clear header area

    # Calculate remaining time
    elapsed_time = int(time.time() - start_time)
    remaining_time = max(0, TIMER_START - elapsed_time)
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f"{minutes}:{seconds:02d}"

    # Header labels
    headers = ["Time", "Moves", "Score"]
    values = [timer_text, str(moves_left), str(score)]
    cell_width = WIDTH // len(headers)

    # Draw table structure
    for i in range(len(headers)):
        pygame.draw.rect(screen, DARK_PURPLE, (i * cell_width, 0, cell_width, HEADER_HEIGHT), 2)

        header_surface = HEADER_FONT.render(headers[i], True, BLACK)
        value_surface = HEADER_FONT.render(values[i], True, DARK_PURPLE)

        screen.blit(header_surface, (i * cell_width + (cell_width // 2 - header_surface.get_width() // 2), 15))
        screen.blit(value_surface, (i * cell_width + (cell_width // 2 - value_surface.get_width() // 2), 55))


def animate_swap(pos1, pos2):
    """Smoothly moves two tiles between positions."""
    global grid, moves_left, score
    r1, c1 = pos1
    r2, c2 = pos2
    x1, y1 = c1 * TILE_SIZE, r1 * TILE_SIZE + HEADER_HEIGHT
    x2, y2 = c2 * TILE_SIZE, r2 * TILE_SIZE + HEADER_HEIGHT

    steps = ANIMATION_SPEED
    for i in range(steps + 1):
        screen.fill(WHITE)
        draw_header()
        draw_grid()
        t = i / steps
        new_x1 = x1 * (1 - t) + x2 * t
        new_y1 = y1 * (1 - t) + y2 * t
        new_x2 = x2 * (1 - t) + x1 * t
        new_y2 = y2 * (1 - t) + y1 * t
        draw_gradient_tile(screen, new_x1, new_y1, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, 220)
        draw_gradient_tile(screen, new_x2, new_y2, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, 220)
        pygame.draw.rect(screen, WHITE, (new_x1 + 1, new_y1 + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
        pygame.draw.rect(screen, WHITE, (new_x2 + 1, new_y2 + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
        text1 = FONT.render(grid[r1][c1], True, TEXT_COLOR)
        text2 = FONT.render(grid[r2][c2], True, TEXT_COLOR)
        screen.blit(text1, (new_x1 + TILE_SIZE // 3, new_y1 + TILE_SIZE // 4))
        screen.blit(text2, (new_x2 + TILE_SIZE // 3, new_y2 + TILE_SIZE // 4))
        pygame.display.flip()
        pygame.time.delay(10)

    # Perform the actual swap
    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
    moves_left -= 1  # Reduce move count
    
    # Check for valid words after the swap
    valid_words = get_words_and_positions()
    if valid_words:
        # Calculate points for all valid words
        for word, positions in valid_words:
            word_score = calculate_word_score(word)
            score += word_score
        
        # Highlight the valid words
        highlight_words(valid_words)


def check_word(word):
    """Checks if a string is a valid word in our dictionary."""
    return word in word_list and len(word) >= 3

def get_words_and_positions():
    """Check for valid words in rows and columns, returns words with their positions."""
    valid_words = []
    
    # Check rows
    for r in range(GRID_SIZE):
        row_str = ''.join(grid[r])
        for start in range(GRID_SIZE - 2):  # Minimum 3-letter word
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    # Store word and positions: (word, [(r,c), (r,c+1), ...])
                    positions = [(r, start + i) for i in range(len(word))]
                    valid_words.append((word, positions))
    
    # Check columns
    for c in range(GRID_SIZE):
        col_str = ''.join(grid[r][c] for r in range(GRID_SIZE))
        for start in range(GRID_SIZE - 2):  # Minimum 3-letter word
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    # Store word and positions: (word, [(r,c), (r+1,c), ...])
                    positions = [(start + i, c) for i in range(len(word))]
                    valid_words.append((word, positions))
                    
    return valid_words

def calculate_word_score(word):
    """Calculate the score for a word based on letter values."""
    return sum(LETTER_SCORES[letter] for letter in word)

def highlight_words(words_positions):
    """Temporarily highlight valid words on the grid."""
    if not words_positions:
        return
        
    # Draw grid with highlighted positions
    for word, positions in words_positions:
        word_score = calculate_word_score(word)
        # Highlight each position of the word
        for r, c in positions:
            x, y = c * TILE_SIZE, r * TILE_SIZE + HEADER_HEIGHT
            pygame.draw.rect(screen, GREEN, (x, y, TILE_SIZE, TILE_SIZE), 4)
            
        # Display word and score
        first_pos = positions[0]
        x = first_pos[1] * TILE_SIZE
        y = first_pos[0] * TILE_SIZE + HEADER_HEIGHT - 30
        word_text = SCORE_FONT.render(f"{word}: +{word_score}", True, GREEN)
        screen.blit(word_text, (x, y))
    
    pygame.display.flip()
    pygame.time.delay(1000)  # Show the highlight for 1 second


# Game loop
running = True
while running:
    screen.fill(WHITE)
    draw_header()
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and moves_left > 0:
            x, y = event.pos
            if y > HEADER_HEIGHT:
                col, row = x // TILE_SIZE, (y - HEADER_HEIGHT) // TILE_SIZE
                if selected_tile is None:
                    selected_tile = (row, col)
                else:
                    if abs(row - selected_tile[0]) + abs(col - selected_tile[1]) == 1:
                        animate_swap(selected_tile, (row, col))
                    selected_tile = None

    pygame.display.flip()

    if time.time() - start_time >= TIMER_START:
        running = False

pygame.quit()
