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
OVERLAY_COLOR = (0, 0, 0, 180)  # Semi-transparent black overlay
GAME_OVER_BG = (60, 20, 100)  # Dark purple for game over box
GOLD = (255, 215, 0)  # Gold color for score highlight

# Fonts
FONT = pygame.font.Font(None, 50)
HEADER_FONT = pygame.font.Font(None, 40)
SCORE_FONT = pygame.font.Font(None, 20)
LARGE_FONT = pygame.font.Font(None, 80)

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
    
    # Process valid words with animations
    process_valid_words()


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


def pop_tiles(positions):
    """Animate tiles fading out when they form a valid word."""
    # Create a set of positions to be removed
    empty_positions = set(positions)
    if not empty_positions:
        return
    
    # Simplified animation - just fade out the tiles that form words
    frames = 10
    for i in range(frames):
        screen.fill(WHITE)
        draw_header()
        
        # Calculate alpha for fading
        alpha = 255 - int((i / frames) * 255)
        
        # Draw the grid with fading effect for valid word tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = col * TILE_SIZE, row * TILE_SIZE + HEADER_HEIGHT
                
                if (row, col) in empty_positions:
                    # Draw fading tile
                    temp_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    draw_gradient_tile(temp_surface, 0, 0, TILE_SIZE, TILE_SIZE, 
                                     DARK_PURPLE, LIGHT_PURPLE, alpha)
                    
                    letter = grid[row][col]
                    if letter:
                        # Fade text along with tile
                        text_color = (TEXT_COLOR[0], TEXT_COLOR[1], TEXT_COLOR[2], alpha)
                        text_surface = FONT.render(letter, True, text_color)
                        temp_surface.blit(text_surface, (TILE_SIZE // 3, TILE_SIZE // 4))
                    
                    screen.blit(temp_surface, (x, y))
                else:
                    # Draw normal tiles
                    draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                    pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                    
                    letter = grid[row][col]
                    if letter:  # Check if letter exists
                        text_surface = FONT.render(letter, True, TEXT_COLOR)
                        score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                        
                        screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                        screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))
        
        pygame.display.flip()
        pygame.time.delay(30)
        
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
    
    # Remove popped tiles from the grid
    for row, col in positions:
        grid[row][col] = None

def drop_new_tiles():
    """Fill empty spaces by dropping tiles from above and adding new ones at the top."""
    # Process each column individually
    for col in range(GRID_SIZE):
        # Count how many empty spaces in this column
        empty_spaces = []
        for row in range(GRID_SIZE):
            if grid[row][col] is None:
                empty_spaces.append(row)
        
        if not empty_spaces:
            continue  # No empty spaces in this column
        
        # Step 1: Shift existing tiles down
        for empty_row in sorted(empty_spaces):
            # Move all tiles above this empty space down
            for row in range(empty_row, 0, -1):
                grid[row][col] = grid[row-1][col]
            
            # Add new random letter at the top
            grid[0][col] = random.choice(LETTERS)
        
        # Step 2: Animate the dropping with a simple smooth motion
        steps = 8
        for step in range(steps + 1):
            screen.fill(WHITE)
            draw_header()
            
            # Calculate progress of the dropping animation
            progress = step / steps
            
            # Draw all tiles
            for row in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    # For columns with dropping tiles
                    if c == col and row < len(empty_spaces):
                        # Calculate the drop position
                        source_y = (row - 1) * TILE_SIZE + HEADER_HEIGHT
                        if row == 0:
                            source_y = -TILE_SIZE + HEADER_HEIGHT  # Coming from above the grid
                        target_y = row * TILE_SIZE + HEADER_HEIGHT
                        current_y = source_y + (target_y - source_y) * progress
                        
                        # Draw the dropping tile
                        draw_gradient_tile(screen, c * TILE_SIZE, current_y, TILE_SIZE, TILE_SIZE, 
                                          DARK_PURPLE, LIGHT_PURPLE)
                        pygame.draw.rect(screen, WHITE, 
                                        (c * TILE_SIZE + 1, current_y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                        
                        letter = grid[row][c]
                        if letter:  # Ensure we have a valid letter
                            text_surface = FONT.render(letter, True, TEXT_COLOR)
                            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                            
                            screen.blit(text_surface, (c * TILE_SIZE + TILE_SIZE // 3, current_y + TILE_SIZE // 4))
                            screen.blit(score_surface, (c * TILE_SIZE + TILE_SIZE - 20, current_y + TILE_SIZE - 25))
                    else:
                        # Draw stationary tiles
                        x, y = c * TILE_SIZE, row * TILE_SIZE + HEADER_HEIGHT
                        draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                        pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                        
                        letter = grid[row][c]
                        if letter:  # Check if letter exists
                            text_surface = FONT.render(letter, True, TEXT_COLOR)
                            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                            
                            screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                            screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))
            
            pygame.display.flip()
            pygame.time.delay(30)
            
            # Check for quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

def process_valid_words():
    """Check for valid words, update score, and handle tile movements."""
    global score
    
    # Step 1: Find valid words
    valid_words = get_words_and_positions()
    if not valid_words:
        return False  # No valid words found
    
    # Step 2: Highlight valid words
    highlight_words(valid_words)
    
    # Step 3: Collect positions of tiles to be removed and update score
    all_positions = set()
    for word, positions in valid_words:
        word_score = calculate_word_score(word)
        score += word_score
        # Only add positions of tiles that form valid words
        for pos in positions:
            all_positions.add(pos)
    
    # Step 4: Remove tiles and animate
    pop_tiles(all_positions)
    
    # Step 5: Drop tiles to fill gaps
    drop_new_tiles()
    
    # Step 6: Check for new valid words after dropping
    # Recursively call this function if new valid words are formed
    if get_words_and_positions():
        pygame.time.delay(300)  # Brief delay before checking for new matches
        process_valid_words()
    
    return True

def show_game_over_menu():
    """Display an attractive game over screen with the final score."""
    global score
    
    # Create a semi-transparent overlay for the entire screen
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))
    
    # Create the game over box
    box_width, box_height = 400, 300
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    
    # Animation for the box appearing (scaling up)
    for i in range(20):
        # Clear overlay each frame
        screen.blit(overlay, (0, 0))
        
        # Calculate scaled size for animation
        scale = i / 20.0
        current_width = int(box_width * scale)
        current_height = int(box_height * scale)
        current_x = WIDTH // 2 - current_width // 2
        current_y = HEIGHT // 2 - current_height // 2
        
        # Draw box with rounded corners and gradient
        box_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        for y in range(current_height):
            # Create vertical gradient
            progress = y / current_height
            r = GAME_OVER_BG[0] + (DARK_PURPLE[0] - GAME_OVER_BG[0]) * progress
            g = GAME_OVER_BG[1] + (DARK_PURPLE[1] - GAME_OVER_BG[1]) * progress
            b = GAME_OVER_BG[2] + (DARK_PURPLE[2] - GAME_OVER_BG[2]) * progress
            pygame.draw.line(box_surface, (int(r), int(g), int(b)), 
                            (0, y), (current_width, y))
        
        # Draw border
        if i > 10:  # Only draw border when box is big enough
            border_radius = min(15, int(15 * scale))
            pygame.draw.rect(box_surface, WHITE, 
                            (0, 0, current_width, current_height), 
                            3, border_radius=border_radius)
        
        screen.blit(box_surface, (current_x, current_y))
        pygame.display.flip()
        pygame.time.delay(20)
    
    # Draw final box with content
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    for y in range(box_height):
        # Create vertical gradient
        progress = y / box_height
        r = GAME_OVER_BG[0] + (DARK_PURPLE[0] - GAME_OVER_BG[0]) * progress
        g = GAME_OVER_BG[1] + (DARK_PURPLE[1] - GAME_OVER_BG[1]) * progress
        b = GAME_OVER_BG[2] + (DARK_PURPLE[2] - GAME_OVER_BG[2]) * progress
        pygame.draw.line(box_surface, (int(r), int(g), int(b)), 
                        (0, y), (box_width, y))
    
    # Draw border with rounded corners
    pygame.draw.rect(box_surface, WHITE, 
                    (0, 0, box_width, box_height), 
                    4, border_radius=15)
    
    # Animate text appearing
    for i in range(30):
        # Copy the background and box
        screen.blit(overlay, (0, 0))
        screen.blit(box_surface, (box_x, box_y))
        
        # Calculate text transparency
        alpha = min(255, i * 10)
        
        # Game Over text
        if i > 5:
            game_over_text = LARGE_FONT.render("GAME OVER", True, WHITE)
            game_over_text.set_alpha(alpha)
            text_x = WIDTH // 2 - game_over_text.get_width() // 2
            text_y = box_y + 50
            screen.blit(game_over_text, (text_x, text_y))
        
        # Score text
        if i > 15:
            score_label = HEADER_FONT.render("Your Score:", True, WHITE)
            score_label.set_alpha(alpha)
            score_text = LARGE_FONT.render(str(score), True, GOLD)
            score_text.set_alpha(alpha)
            
            label_x = WIDTH // 2 - score_label.get_width() // 2
            label_y = box_y + 130
            score_x = WIDTH // 2 - score_text.get_width() // 2
            score_y = box_y + 170
            
            screen.blit(score_label, (label_x, label_y))
            screen.blit(score_text, (score_x, score_y))
        
        # Continue text
        if i > 25:
            continue_text = SCORE_FONT.render("Click anywhere to exit", True, WHITE)
            continue_text.set_alpha(alpha)
            continue_x = WIDTH // 2 - continue_text.get_width() // 2
            continue_y = box_y + box_height - 30
            screen.blit(continue_text, (continue_x, continue_y))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    # Wait for click to exit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
                
        pygame.time.delay(100)
    
    return False


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

show_game_over_menu()
pygame.quit()
