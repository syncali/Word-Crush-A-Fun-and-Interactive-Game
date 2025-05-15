import pygame
import random
import time
import math

pygame.init()

# Game dimensions and layout
WIDTH, HEIGHT = 600, 700
GRID_SIZE = 6
TILE_SIZE = 80
GRID_WIDTH = GRID_SIZE * TILE_SIZE
GRID_HEIGHT = GRID_SIZE * TILE_SIZE
HEADER_HEIGHT = 100
GRID_MARGIN_X = (WIDTH - GRID_WIDTH) // 2
GRID_MARGIN_Y = (HEIGHT - GRID_HEIGHT - HEADER_HEIGHT) // 2 + HEADER_HEIGHT
GRID_X = GRID_MARGIN_X
GRID_Y = GRID_MARGIN_Y
PATTERN_SIZE = 40
ANIMATION_SPEED = 15
TOTAL_MOVES = 10  # Set initial move count
TIMER_START = 180  # 3 minutes in seconds

LETTER_SCORES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1,
    "J": 8, "K": 5, "L": 1, "M": 3, "N": 1, "O": 1, "P": 3, "Q": 10, "R": 1,
    "S": 1, "T": 1, "U": 1, "V": 4, "W": 4, "X": 8, "Y": 4, "Z": 10
}

LETTER_DISTRIBUTION = {
    'A': 6, 'B': 3, 'C': 3, 'D': 4, 'E': 8, 'F': 3, 'G': 3, 'H': 3, 'I': 6,
    'J': 2, 'K': 2, 'L': 4, 'M': 3, 'N': 4, 'O': 5, 'P': 3, 'Q': 2, 'R': 4,
    'S': 4, 'T': 4, 'U': 3, 'V': 3, 'W': 3, 'X': 2, 'Y': 3, 'Z': 2
}

# Letter groups for grid generation strategy
LETTER_GROUPS = {
    'VOWELS': ['A', 'E', 'I', 'O', 'U', 'Y'],
    'COMMON_CONSONANTS': ['R', 'S', 'T', 'N', 'L'],
    'RARE_CONSONANTS': ['Q', 'X', 'Z', 'J', 'K'],
    'SUFFIX_LETTERS': ['S', 'D', 'R']
}

# Common English letter pairs to avoid generating too many valid words
COMMON_BIGRAMS = {
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ND', 'ON', 'EN', 'AT', 
    'ES', 'OR', 'AR', 'AL', 'TE', 'CO', 'DE', 'TO', 'RA', 'ET'
}

LETTER_POOL = []
for letter, count in LETTER_DISTRIBUTION.items():
    LETTER_POOL.extend([letter] * count)

# Colors
WHITE = (255, 255, 255)
DARK_PURPLE = (100, 0, 180)
LIGHT_PURPLE = (150, 50, 220)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (70, 70, 70, 100)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
OVERLAY_COLOR = (0, 0, 0, 180)
GAME_OVER_BG = (60, 20, 100)
GOLD = (255, 215, 0)
RECOMMENDATION_LIGHT = (180, 120, 240)
HOVER_COLOR = (200, 200, 100, 120)
PAUSED_COLOR = (0, 100, 200, 80)
SELECTED_GLOW = (255, 255, 0)  # Yellow glow for selected tile
SELECTED_BORDER = (255, 220, 0)  # Bright yellow for selected tile border

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
    
def check_word(word):
    """Checks if a string is a valid word in our dictionary."""
    return word in word_list and len(word) >= 3

def get_new_letter(adjacent_letters=None):
    """Get a new letter based on strategic distribution to minimize word formation."""
    vowels = ['A', 'E', 'I', 'O', 'U']
    
    # Apply strategic letter selection when we have adjacent letters
    if adjacent_letters:
        # Avoid placing vowels next to vowels
        vowel_count = sum(1 for letter in adjacent_letters if letter in LETTER_GROUPS['VOWELS'])
        if vowel_count >= 2:
            # Too many vowels nearby, avoid adding another vowel
            consonants = [l for l in LETTER_POOL if l not in LETTER_GROUPS['VOWELS']]
            return random.choice(consonants)
        
        # Avoid placing common consonant pairs
        for letter in adjacent_letters:
            for adjacent in adjacent_letters:
                if letter + adjacent in COMMON_BIGRAMS:
                    # Avoid letters that would complete common pairs
                    uncommon = LETTER_GROUPS['RARE_CONSONANTS']
                    if uncommon:
                        return random.choice(uncommon)
    
    # 30% chance to force a vowel (reduced from 40%)
    if random.random() < 0.3:
        # Weight vowels according to their frequency in the pool
        vowel_weights = {v: LETTER_DISTRIBUTION[v] for v in vowels}
        total = sum(vowel_weights.values())
        r = random.random() * total
        cumulative = 0
        for vowel, weight in vowel_weights.items():
            cumulative += weight
            if r <= cumulative:
                return vowel
    
    # Otherwise use the standard letter pool
    return random.choice(LETTER_POOL)


def generate_grid_without_words():
    """Generate a grid with no valid words already formed."""
    attempts = 0
    max_attempts = 100  # Prevent infinite loop
    
    while attempts < max_attempts:
        attempts += 1
        
        # Create initial random grid with smarter letter placement
        new_grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Fill grid with strategic letter placement
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Get adjacent letters (that are already placed)
                adjacent_letters = set()  # Using set for faster lookups
                # Check left
                if c > 0 and new_grid[r][c-1]:
                    adjacent_letters.add(new_grid[r][c-1])
                # Check above
                if r > 0 and new_grid[r-1][c]:
                    adjacent_letters.add(new_grid[r-1][c])
                # Check diagonals if needed
                if r > 0 and c > 0 and new_grid[r-1][c-1]:
                    adjacent_letters.add(new_grid[r-1][c-1])
                
                # Get a new letter considering adjacent letters
                new_grid[r][c] = get_new_letter(list(adjacent_letters))
        
        # Check if the grid has any valid words
        valid_words_found = False
        
        # Check rows
        for r in range(GRID_SIZE):
            row_str = ''.join(new_grid[r])
            for start in range(GRID_SIZE - 2):  # Minimum 3-letter word
                for end in range(start + 2, GRID_SIZE):
                    word = row_str[start:end+1]
                    if check_word(word):
                        valid_words_found = True
                        break
                if valid_words_found:
                    break
            if valid_words_found:
                break
        
        if not valid_words_found:
            # Check columns
            for c in range(GRID_SIZE):
                col_str = ''.join(new_grid[r][c] for r in range(GRID_SIZE))
                for start in range(GRID_SIZE - 2):  # Minimum 3-letter word
                    for end in range(start + 2, GRID_SIZE):
                        word = col_str[start:end+1]
                        if check_word(word):
                            valid_words_found = True
                            break
                    if valid_words_found:
                        break
                if valid_words_found:
                    break
        
        # If no valid words were found, use this grid
        if not valid_words_found:
            print(f"Found grid with no words after {attempts} attempts")
            return new_grid
    
    # If we can't find a grid without words after max attempts,
    # create a grid with minimal valid words by replacing problematic letters
    print(f"Could not find grid with no words after {max_attempts} attempts")
    print("Creating grid with manual fixes...")
    
    # Create an initial grid
    fallback_grid = [[get_new_letter() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Replace tiles that form words with less common letters (Q, Z, X)
    uncommon = ['Q', 'Z', 'X', 'J', 'K']
    
    # Check and fix rows
    for r in range(GRID_SIZE):
        row_str = ''.join(fallback_grid[r])
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    # Replace middle letter with uncommon letter
                    mid = start + (end - start) // 2
                    fallback_grid[r][mid] = random.choice(uncommon)
    
    # Check and fix columns
    for c in range(GRID_SIZE):
        col_str = ''.join(fallback_grid[r][c] for r in range(GRID_SIZE))
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    # Replace middle letter with uncommon letter
                    mid = start + (end - start) // 2
                    fallback_grid[mid][c] = random.choice(uncommon)
    
    return fallback_grid


# Initialize grid with weighted random letters
grid = generate_grid_without_words()

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Puzzle Game")

selected_tile = None
moves_left = TOTAL_MOVES
score = 0
hints_used = 0
recommended_swaps = [] 
start_time = time.time()

# Timer pausing variables
paused_time = 0  # Total time paused
is_paused = False  # Is timer currently paused
pause_start_time = 0  # When the current pause began


def draw_gradient_tile(surface, x, y, width, height, color1, color2, opacity=255):
    """Creates a gradient effect from top to bottom inside a tile."""
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        r = color1[0] + (color2[0] - color1[0]) * (i / height)
        g = color1[1] + (color2[1] - color1[1]) * (i / height)
        b = color1[2] + (color2[2] - color1[2]) * (i / height)
        pygame.draw.line(temp_surface, (int(r), int(g), int(b), opacity), (0, i), (width, i))
    surface.blit(temp_surface, (x, y))

def draw_background_and_header():
    """Ensures consistent rendering of background and header across all screens."""
    # Clear the screen
    screen.fill(WHITE)
    
    # Draw background
    texture = generate_background_texture()
    screen.blit(texture, (0, 0))
    
    # Draw header/scoreboard
    draw_header()
    
    return texture  # Return the texture in case it's needed for additional rendering

def generate_background_texture():
    """Generate a simple elegant gradient background."""
    texture = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    # Create a smooth, elegant gradient from dark purple to a slightly lighter shade
    for y in range(HEIGHT):
        progress = y / HEIGHT
        # Elegant purple gradient - deep to lighter purple
        r = 35 + int(25 * progress)
        g = 10 + int(5 * progress) 
        b = 60 + int(40 * progress)
        pygame.draw.line(texture, (r, g, b, 255), (0, y), (WIDTH, y))
    
    return texture

def draw_grid_container():
    """Draws the container box for the grid with rounded corners."""
    grid_container_padding = 20
    container_x = GRID_X - grid_container_padding
    container_y = GRID_Y - grid_container_padding
    container_width = GRID_WIDTH + (grid_container_padding * 2)
    container_height = GRID_HEIGHT + (grid_container_padding * 2)
    
    # Draw a semi-transparent container to visually separate the grid from the background
    container_surface = pygame.Surface((container_width, container_height), pygame.SRCALPHA)
    container_surface.fill((255, 255, 255, 30))  # Very light semi-transparent white
    pygame.draw.rect(container_surface, (255, 255, 255, 60), 
                    (0, 0, container_width, container_height), 
                    3, border_radius=15)  # Border with rounded corners
    screen.blit(container_surface, (container_x, container_y))

def draw_grid_tiles(empty_positions=None, fading_tiles=None):
    """Draws only the grid tiles with specified empty or fading tile positions."""
    if empty_positions is None:
        empty_positions = set()
    if fading_tiles is None:
        fading_tiles = {}  # Dictionary of (row, col): alpha_value
        
    # Create a set of positions involved in recommended swaps for easy lookup
    recommended_positions = set()
    recommended_pairs = {}  # Map positions to their paired positions and scores

    # Assign unique colors for each recommended swap
    swap_colors = [
        (255, 200, 200),  # Light Red
        (200, 255, 200),  # Light Green
        (200, 200, 255),  # Light Blue
        (255, 255, 200),  # Light Yellow
        (255, 200, 255),  # Light Pink
    ]

    # Collect all positions involved in recommended swaps
    for i, (score, pos1, pos2) in enumerate(recommended_swaps):
        recommended_positions.add(pos1)
        recommended_positions.add(pos2)
        recommended_pairs[pos1] = (pos2, score, swap_colors[i % len(swap_colors)])
        recommended_pairs[pos2] = (pos1, score, swap_colors[i % len(swap_colors)])
          # Get mouse position for hover effect
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # Adjust mouse coordinates to account for grid centering
    grid_mouse_x = mouse_x - GRID_X
    grid_mouse_y = mouse_y - GRID_Y
    hover_col = grid_mouse_x // TILE_SIZE
    hover_row = grid_mouse_y // TILE_SIZE
    hover_pos = (hover_row, hover_col)
    
    # Draw each tile in the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):            
            pos = (row, col)
            x, y = GRID_X + col * TILE_SIZE, GRID_Y + row * TILE_SIZE
            
            # Skip drawing if this position should be empty
            if pos in empty_positions:
                continue
                
            # Draw fading tile if this position is fading
            if pos in fading_tiles:
                alpha = fading_tiles[pos]
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
                continue
            
            # Handle normal tile drawing
            # Check if this position is in a recommended swap or it's the selected tile
            is_recommended = pos in recommended_positions
            is_selected = selected_tile is not None and pos == selected_tile
              # Draw tile background (normal, highlighted, or hover)
            if is_selected:
                # Calculate pulse effect (0.0 to 1.0)
                pulse = (math.sin(time.time() * 5) + 1) / 2
                
                # Draw outer glow
                glow_size = 4 + int(pulse * 3)
                glow_surface = pygame.Surface((TILE_SIZE + glow_size*2, TILE_SIZE + glow_size*2), pygame.SRCALPHA)
                glow_color = (SELECTED_GLOW[0], SELECTED_GLOW[1], SELECTED_GLOW[2], 100 + int(pulse * 155))
                pygame.draw.rect(glow_surface, glow_color, 
                               (0, 0, TILE_SIZE + glow_size*2, TILE_SIZE + glow_size*2), 
                               0, border_radius=8)
                screen.blit(glow_surface, (x - glow_size, y - glow_size))
                
                # Draw gradient tile background
                draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, 255)
                
                # Draw pulsating border
                border_thickness = 2 + int(pulse * 3)
                pygame.draw.rect(screen, SELECTED_BORDER, 
                               (x, y, TILE_SIZE, TILE_SIZE), 
                               border_thickness, border_radius=4)
            elif is_recommended:
                # Recommended tiles get a matching color highlight
                paired_pos, score, highlight_color = recommended_pairs[pos]
                
                # Apply highlight effect
                highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                highlight_surface.fill((highlight_color[0], highlight_color[1], highlight_color[2], 40))  # Semi-transparent
                
                # Draw base tile
                draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                
                # Add highlight overlay
                screen.blit(highlight_surface, (x, y))
                
                # Draw directional indicator to paired tile
                paired_row, paired_col = paired_pos
                pygame.draw.line(screen, 
                                highlight_color, 
                                (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 
                                (GRID_X + paired_col * TILE_SIZE + TILE_SIZE // 2, 
                                 GRID_Y + paired_row * TILE_SIZE + TILE_SIZE // 2), 
                                3)
                
                # Draw score gain indicator
                if score > 0:
                    score_text = f"+{score}"
                    score_render = SCORE_FONT.render(score_text, True, GOLD)
                    score_x = x + TILE_SIZE // 2 - score_render.get_width() // 2
                    score_y = y + TILE_SIZE // 2 - score_render.get_height() // 2
                    score_bg = pygame.Surface((score_render.get_width() + 10, score_render.get_height() + 6), pygame.SRCALPHA)
                    score_bg.fill((0, 0, 0, 150))  # Semi-transparent black background
                    screen.blit(score_bg, (score_x - 5, score_y - 3))
                    screen.blit(score_render, (score_x, score_y))
            elif pos == hover_pos:
                # Hover effect for tile under mouse cursor
                draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                
                # Add hover highlight
                highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                highlight_surface.fill(HOVER_COLOR)  # Semi-transparent highlight
                screen.blit(highlight_surface, (x, y))
            else:
                # Normal tile
                draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
            
            # Draw the letter and score on the tile
            letter = grid[row][col]
            if letter:
                text_surface = FONT.render(letter, True, TEXT_COLOR)
                score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                
                screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))

def draw_grid():
    """Draws the letter grid with proper margins and overlays recommended swaps."""
    # Use the helper function to ensure consistent background and header
    draw_background_and_header()
    
    # Draw the grid container
    draw_grid_container()
    
    # Draw all grid tiles using our helper function
    draw_grid_tiles()
    
    # Get mouse position for hover effect
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # Adjust mouse coordinates to account for grid centering
    grid_mouse_x = mouse_x - GRID_X
    grid_mouse_y = mouse_y - GRID_Y
    hover_col = grid_mouse_x // TILE_SIZE
    hover_row = grid_mouse_y // TILE_SIZE
    hover_pos = (hover_row, hover_col)
    
    is_valid_hover = (0 <= hover_row < GRID_SIZE and 0 <= hover_col < GRID_SIZE 
                     and 0 <= grid_mouse_x < GRID_WIDTH and 0 <= grid_mouse_y < GRID_HEIGHT)    # Create a set of positions involved in recommended swaps for easy lookup
    recommended_positions = set()
    recommended_pairs = {}  # Map positions to their paired positions and scores

    # Assign unique colors for each recommended swap
    swap_colors = [
        (255, 200, 200),  # Light Red
        (200, 255, 200),  # Light Green
        (200, 200, 255),  # Light Blue
        (255, 255, 200),  # Light Yellow
        (255, 200, 255),  # Light Pink
    ]

    # Collect all positions involved in recommended swaps
    for i, (score, pos1, pos2) in enumerate(recommended_swaps):
        recommended_positions.add(pos1)
        recommended_positions.add(pos2)
        recommended_pairs[pos1] = (pos2, score, swap_colors[i % len(swap_colors)])
        recommended_pairs[pos2] = (pos1, score, swap_colors[i % len(swap_colors)])

    # Draw each tile in the grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):            
            pos = (row, col)
            x, y = GRID_X + col * TILE_SIZE, GRID_Y + row * TILE_SIZE  # Use grid margins

            # Determine the appearance of the tile based on selection and recommendation status
            if selected_tile == pos:
                # Selected tile gets a slightly transparent appearance
                opacity = 200
                tile_color1, tile_color2 = DARK_PURPLE, LIGHT_PURPLE
            elif pos in recommended_positions:
                # Recommended swap tiles get a unique color
                _, _, tile_color1 = recommended_pairs[pos]
                tile_color2 = LIGHT_PURPLE
                opacity = 255
            else:
                # Regular tiles
                opacity = 255
                tile_color1, tile_color2 = DARK_PURPLE, LIGHT_PURPLE

            # Draw the tile with appropriate colors
            draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, tile_color1, tile_color2, opacity)

            # Add a white border around the tile
            pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)

            # Draw the letter and its score
            letter = grid[row][col]
            text_surface = FONT.render(letter, True, TEXT_COLOR)
            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)

            # Center letter
            screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
            # Display score at bottom right
            screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))

    # Highlight the hovered tile and its pair
    if is_valid_hover and hover_pos in recommended_pairs:
        # Get the paired position and score for this recommended move
        other_pos, swap_score, highlight_color = recommended_pairs[hover_pos]
        other_row, other_col = other_pos        # Highlight the hovered tile
        hover_x = GRID_X + hover_col * TILE_SIZE
        hover_y = GRID_Y + hover_row * TILE_SIZE
        highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, HOVER_COLOR,
                         (0, 0, TILE_SIZE, TILE_SIZE), 0, border_radius=4)
        screen.blit(highlight_surface, (hover_x, hover_y))

        # Highlight the paired tile
        other_x = GRID_X + other_col * TILE_SIZE
        other_y = GRID_Y + other_row * TILE_SIZE
        screen.blit(highlight_surface, (other_x, other_y))

        # Display the score pop-up above the tiles
        mid_x = (hover_x + other_x) // 2 + TILE_SIZE // 2
        mid_y = (hover_y + other_y) // 2 - 20

        # Create a small score bubble
        score_text = f"+{swap_score}"
        score_surface = HEADER_FONT.render(score_text, True, WHITE)

        # Background for the score
        padding = 10
        bubble_width = score_surface.get_width() + padding * 2
        bubble_height = score_surface.get_height() + padding

        bubble_x = mid_x - bubble_width // 2
        bubble_y = mid_y - bubble_height // 2

        # Draw score bubble background
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (0, 0, 0, 180),
                         (0, 0, bubble_width, bubble_height), 0, border_radius=8)
        pygame.draw.rect(bubble_surface, GOLD,
                         (0, 0, bubble_width, bubble_height), 2, border_radius=8)

        # Draw score text on bubble
        bubble_surface.blit(score_surface,
                            (padding, padding // 2))

        # Draw bubble on screen
        screen.blit(bubble_surface, (bubble_x, bubble_y))
                    
def draw_header():
    """Displays the timer, moves left, score, and hint button."""
    global moves_left, score, paused_time, is_paused, hints_used
    
    # Draw header background directly to the screen first
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEADER_HEIGHT))
    
    # Draw a border around the header
    pygame.draw.rect(screen, DARK_PURPLE, (0, 0, WIDTH, HEADER_HEIGHT), 3)

    # Calculate remaining time, accounting for pauses
    if is_paused:
        current_pause_duration = time.time() - pause_start_time
        total_paused = paused_time + current_pause_duration
    else:
        total_paused = paused_time

    elapsed_time = int(time.time() - start_time - total_paused)
    remaining_time = max(0, TIMER_START - elapsed_time)
    minutes = remaining_time // 60
    seconds = remaining_time % 60

    # Format timer text
    timer_text = f"{minutes}:{seconds:02d}"
    timer_color = DARK_PURPLE

    # Header labels
    headers = ["Time", "Moves", "Score", ""]
    values = [timer_text, str(moves_left), str(score), f"{3 - hints_used}"]
    colors = [timer_color, DARK_PURPLE, DARK_PURPLE, (0, 150, 0) if hints_used < 3 else (150, 0, 0)]
    cell_width = WIDTH // len(headers)

    # Draw table structure
    for i in range(len(headers)):
        pygame.draw.rect(screen, DARK_PURPLE, (i * cell_width, 0, cell_width, HEADER_HEIGHT), 2)

        header_surface = HEADER_FONT.render(headers[i], True, BLACK)
        value_surface = HEADER_FONT.render(values[i], True, colors[i])

        screen.blit(header_surface, (i * cell_width + (cell_width // 2 - header_surface.get_width() // 2), 15))
        screen.blit(value_surface, (i * cell_width + (cell_width // 2 - value_surface.get_width() // 2), 55))

    # Draw the "Hint" button
    hint_button_width = 100
    hint_button_height = 40
    hint_button_x = WIDTH - hint_button_width - 25
    hint_button_y = HEADER_HEIGHT // 3 - hint_button_height // 2

    # Change button color based on availability
    button_color = (0, 200, 0) if hints_used < 3 else (200, 0, 0)
    pygame.draw.rect(screen, button_color, (hint_button_x, hint_button_y, hint_button_width, hint_button_height), 0, border_radius=8)
    pygame.draw.rect(screen, WHITE, (hint_button_x, hint_button_y, hint_button_width, hint_button_height), 2, border_radius=8)

    # Add "Hint" text to the button
    hint_text = HEADER_FONT.render("Hint", True, WHITE)
    screen.blit(hint_text, (hint_button_x + (hint_button_width - hint_text.get_width()) // 2, hint_button_y + (hint_button_height - hint_text.get_height()) // 2))


def animate_swap(pos1, pos2):
    """Smoothly moves two tiles between positions."""
    global grid, moves_left, score    
    r1, c1 = pos1
    r2, c2 = pos2
    # Adjust x,y to account for grid centering
    x1, y1 = GRID_X + c1 * TILE_SIZE, GRID_Y + r1 * TILE_SIZE    
    x2, y2 = GRID_X + c2 * TILE_SIZE, GRID_Y + r2 * TILE_SIZE    
    steps = ANIMATION_SPEED
    
    # Create a set to track the animated positions
    animated_positions = {pos1, pos2}
    
    for i in range(steps + 1):
        # Use our consistent background drawing
        draw_background_and_header()
        
        # Draw the grid container
        draw_grid_container()
        
        # Calculate interpolation progress
        t = i / steps
        new_x1 = x1 * (1 - t) + x2 * t
        new_y1 = y1 * (1 - t) + y2 * t
        new_x2 = x2 * (1 - t) + x1 * t
        new_y2 = y2 * (1 - t) + y1 * t
        
        # Draw all tiles - first the static ones
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                pos = (row, col)
                if pos in animated_positions:
                    continue  # Skip animated tiles for now
                
                # Draw normal tiles
                tile_x = GRID_X + col * TILE_SIZE
                tile_y = GRID_Y + row * TILE_SIZE
                draw_gradient_tile(screen, tile_x, tile_y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                pygame.draw.rect(screen, WHITE, (tile_x + 1, tile_y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                
                letter = grid[row][col]
                if letter:  # Check if letter exists
                    text_surface = FONT.render(letter, True, TEXT_COLOR)
                    score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                    
                    screen.blit(text_surface, (tile_x + TILE_SIZE // 3, tile_y + TILE_SIZE // 4))
                    screen.blit(score_surface, (tile_x + TILE_SIZE - 20, tile_y + TILE_SIZE - 25))
        
        # Now draw the animated tiles on a separate surface to maintain transparency
        animation_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Draw first moving tile
        draw_gradient_tile(animation_surface, new_x1, new_y1, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, 220)
        pygame.draw.rect(animation_surface, WHITE, (new_x1 + 1, new_y1 + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
        text1 = FONT.render(grid[r1][c1], True, TEXT_COLOR)
        score1 = SCORE_FONT.render(str(LETTER_SCORES[grid[r1][c1]]), True, WHITE)
        animation_surface.blit(text1, (new_x1 + TILE_SIZE // 3, new_y1 + TILE_SIZE // 4))
        animation_surface.blit(score1, (new_x1 + TILE_SIZE - 20, new_y1 + TILE_SIZE - 25))
        
        # Draw second moving tile
        draw_gradient_tile(animation_surface, new_x2, new_y2, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, 220)
        pygame.draw.rect(animation_surface, WHITE, (new_x2 + 1, new_y2 + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
        text2 = FONT.render(grid[r2][c2], True, TEXT_COLOR)
        score2 = SCORE_FONT.render(str(LETTER_SCORES[grid[r2][c2]]), True, WHITE)
        animation_surface.blit(text2, (new_x2 + TILE_SIZE // 3, new_y2 + TILE_SIZE // 4))
        animation_surface.blit(score2, (new_x2 + TILE_SIZE - 20, new_y2 + TILE_SIZE - 25))
        
        # Add movement trail (optional visual enhancement)
        if i > 1:
            trail_alpha = 100 - int(80 * (i / steps))
            trail_color1 = (200, 200, 255, trail_alpha)
            trail_color2 = (200, 255, 200, trail_alpha)
            
            # Trail behind first tile
            trail_length = 10
            pygame.draw.line(animation_surface, trail_color1, 
                           (new_x1 + TILE_SIZE//2, new_y1 + TILE_SIZE//2), 
                           (x1 + TILE_SIZE//2, y1 + TILE_SIZE//2), trail_length)
            
            # Trail behind second tile
            pygame.draw.line(animation_surface, trail_color2, 
                           (new_x2 + TILE_SIZE//2, new_y2 + TILE_SIZE//2), 
                           (x2 + TILE_SIZE//2, y2 + TILE_SIZE//2), trail_length)
        
        # Blit animation surface onto main screen
        screen.blit(animation_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(10)

    # Perform the actual swap
    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
    moves_left -= 1  # Reduce move count
    
    # Process valid words with animations
    process_valid_words()
    
    greedy_best_first_search_for_swaps()


def get_words_and_positions():
    """Check for valid words in rows and columns, returns words with their positions."""
    all_words = []
    
    # Check rows - only left to right direction
    for r in range(GRID_SIZE):
        row_str = ''.join(grid[r])
        for start in range(GRID_SIZE - 2):  # Minimum 3-letter word
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    # Store word and positions: (word, [(r,c), (r,c+1), ...])
                    positions = [(r, start + i) for i in range(end - start + 1)]
                    all_words.append((word, positions))
    
    # Check columns - only top to bottom direction
    for c in range(GRID_SIZE):
        col_chars = [grid[r][c] for r in range(GRID_SIZE)]
        col_str = ''.join(col_chars)
        for start in range(GRID_SIZE - 2):  # Minimum 3-letter word
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    # Store word and positions: (word, [(r,c), (r+1,c), ...])
                    positions = [(start + i, c) for i in range(end - start + 1)]
                    all_words.append((word, positions))
    
    # Filter out subwords - only keep the longest word when positions overlap
    valid_words = []
    
    # Pre-sort words by length for better efficiency
    all_words.sort(key=lambda x: len(x[0]), reverse=True)
    
    # Use set for faster position tracking
    covered_positions = set()
    
    for word, positions in all_words:
        pos_set = frozenset(positions)  # Immutable set for faster comparisons
        if not pos_set.intersection(covered_positions):
            valid_words.append((word, positions))
            covered_positions.update(pos_set)
    
    return valid_words

def simulate_swap_and_evaluate(pos1, pos2):
    """Simulate swap directly on the real grid and calculate score gain, then restore grid."""
    global grid
    r1, c1 = pos1
    r2, c2 = pos2

    # Swap directly
    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]

    # Capture score before processing
    initial_score = 0
    temp_score = 0
    temp_score += calculate_grid_total_score()

    # Undo the swap back to original grid (restoring the grid)
    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]

    # Return score gain
    return temp_score - initial_score

def calculate_grid_total_score():
    """Process all valid words, calculate total score, and return it (without animations or drops)."""
    total_score = 0
    valid_words = get_words_and_positions()
    for word, positions in valid_words:
        total_score += calculate_word_score(word)
    return total_score

def greedy_best_first_search_for_swaps():
    """Greedy Best-First Search: Recommend the best swaps ranked by potential score gain."""
    global recommended_swaps
    moves = []

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if c + 1 < GRID_SIZE:
                score_gain = simulate_swap_and_evaluate((r, c), (r, c + 1))
                moves.append((score_gain, (r, c), (r, c + 1)))
            if r + 1 < GRID_SIZE:
                score_gain = simulate_swap_and_evaluate((r, c), (r + 1, c))
                moves.append((score_gain, (r, c), (r + 1, c)))

    moves.sort(reverse=True, key=lambda x: x[0])

    # Store the top 5 recommendations
    recommended_swaps = moves[:3]


def calculate_word_score(word):
    # Cache common word scores
    if not hasattr(calculate_word_score, 'score_cache'):
        calculate_word_score.score_cache = {}
    
    if word in calculate_word_score.score_cache:
        return calculate_word_score.score_cache[word]
    
    score = sum(LETTER_SCORES[letter] for letter in word)
    calculate_word_score.score_cache[word] = score
    return score

def highlight_words(words_positions):
    """Highlight valid words with animations showing the word and score."""
    if not words_positions:
        return
    
    # Animation settings
    highlight_time = 1500  # Total time in ms
    frames = 30
    delay_per_frame = highlight_time // frames
    
    # Create a set of positions that are part of words
    word_positions_set = set()
    for _, positions in words_positions:
        for pos in positions:
            word_positions_set.add(pos)
    
    # Animate each frame
    for i in range(frames):
        # Use our consistent background and header drawing approach
        draw_background_and_header()
        
        # Draw the grid container
        draw_grid_container()
        
        # Always draw all grid tiles first to ensure they're visible
        draw_grid_tiles()
        
        progress = i / frames
        
        # First half: grow highlight, second half: maintain
        scale_factor = min(1.0, progress * 2)
        alpha = min(255, progress * 510)  # Faster fade-in
        
        # For each word, create highlighting effects
        for word, positions in words_positions:
            word_score = calculate_word_score(word)
            
            # Calculate the center of the word, accounting for grid position
            avg_row = sum(pos[0] for pos in positions) / len(positions)
            avg_col = sum(pos[1] for pos in positions) / len(positions)
            center_x = GRID_X + avg_col * TILE_SIZE + TILE_SIZE // 2
            center_y = GRID_Y + avg_row * TILE_SIZE + TILE_SIZE // 2
            
            # 1. Draw connecting line between tiles in the word
            if len(positions) > 1:
                # Sort positions by row/col depending on word orientation
                if all(pos[0] == positions[0][0] for pos in positions):  # Horizontal word
                    sorted_pos = sorted(positions, key=lambda pos: pos[1])
                else:  # Vertical word
                    sorted_pos = sorted(positions, key=lambda pos: pos[0])
                
                # Draw line connecting the centers of the tiles, accounting for grid position
                line_points = [(GRID_X + p[1] * TILE_SIZE + TILE_SIZE // 2, 
                               GRID_Y + p[0] * TILE_SIZE + TILE_SIZE // 2) for p in sorted_pos]
                
                # Create a thicker line with glow effect
                line_width = int(4 + 3 * scale_factor)
                line_color = (100, 255, 100, min(180, int(alpha * 0.7)))
                
                # Draw line with pygame.draw.lines
                line_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.lines(line_surface, line_color, False, line_points, line_width)
                screen.blit(line_surface, (0, 0))
            
            # 2. Highlight each tile in the word with a growing effect
            for r, c in positions:
                x, y = GRID_X + c * TILE_SIZE, GRID_Y + r * TILE_SIZE
                
                # Create a slightly larger highlight rect that grows with the animation
                grow_amount = int(TILE_SIZE * 0.2 * scale_factor)
                highlight_x = x - grow_amount // 2
                highlight_y = y - grow_amount // 2
                highlight_size = TILE_SIZE + grow_amount
                
                # Draw a semi-transparent highlight behind the tile
                highlight_surface = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                highlight_color = (100, 255, 100, min(100, int(alpha * 0.4)))
                pygame.draw.rect(highlight_surface, highlight_color, 
                                (0, 0, highlight_size, highlight_size), 0, border_radius=8)
                screen.blit(highlight_surface, (highlight_x, highlight_y))
                
                # Draw a border around the tile
                border_color = (0, 200, 0, min(255, int(alpha)))
                border_width = max(2, int(3 * scale_factor))
                pygame.draw.rect(screen, border_color, 
                                (x, y, TILE_SIZE, TILE_SIZE), 
                                border_width, border_radius=4)
            
            # 3. Show the word and score with a floating animation
            if progress > 0.2:  # Start showing the word after a brief delay
                # Calculate word display position above the tiles
                if len(positions) > 2:
                    disp_x = center_x - 20 * len(word)
                    disp_y = center_y - TILE_SIZE * 1.5
                else:  # For shorter words, position more precisely
                    disp_x = center_x - 20 * len(word)
                    disp_y = center_y - TILE_SIZE
                
                # Floating animation
                float_offset = math.sin(progress * math.pi * 2) * 5
                disp_y += float_offset
                
                # Create word display with shadow effect
                word_alpha = min(255, int((progress - 0.2) * 425))  # Fade in
                
                # Create a background panel for better visibility
                word_text = f"{word}: +{word_score}"
                text_size = HEADER_FONT.size(word_text)
                panel_width = text_size[0] + 20
                panel_height = text_size[1] + 10
                
                # Draw background panel with rounded corners
                panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                bg_color = (0, 0, 0, min(180, int(word_alpha * 0.7)))  # Semi-transparent black background
                pygame.draw.rect(panel_surface, bg_color, 
                                (0, 0, panel_width, panel_height), 
                                0, border_radius=8)
                
                # Add a colored border to the panel
                border_color = (50, 255, 50, word_alpha)
                pygame.draw.rect(panel_surface, border_color, 
                                (0, 0, panel_width, panel_height), 
                                2, border_radius=8)
                
                # Position the panel
                panel_x = disp_x - 10
                panel_y = disp_y - 5
                screen.blit(panel_surface, (panel_x, panel_y))
                
                # Main text - more vibrant colors for better contrast
                word_surface = HEADER_FONT.render(word_text, True, (220, 255, 220))
                word_surface.set_alpha(word_alpha)
                
                # Position text centered on the panel
                text_x = panel_x + (panel_width - text_size[0]) // 2
                text_y = panel_y + (panel_height - text_size[1]) // 2
                screen.blit(word_surface, (text_x, text_y))
        
        pygame.display.flip()
        pygame.time.delay(delay_per_frame)
        
        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

def pop_tiles(positions):
    """Animate tiles fading out when they form a valid word."""
    # Create a set of positions to be removed
    empty_positions = set(positions)
    if not empty_positions:
        return
    
    # Simplified animation - just fade out the tiles that form words
    frames = 10
    for i in range(frames):
        # Use consistent background and header rendering
        draw_background_and_header()
        
        # Draw the grid container
        draw_grid_container()
        
        # Calculate alpha for fading
        alpha = 255 - int((i / frames) * 255)
        
        # Create a dictionary of fading tiles with their alpha values
        fading_tiles = {pos: alpha for pos in empty_positions}
        
        # Draw all grid tiles including fading ones
        # This ensures the grid remains visible
        draw_grid_tiles(empty_positions=set(), fading_tiles=fading_tiles)
        
        # Add particle effects around the fading tiles
        if alpha > 50:  # Only show particles when alpha is still visible
            for row, col in empty_positions:
                x = GRID_X + col * TILE_SIZE + TILE_SIZE // 2
                y = GRID_Y + row * TILE_SIZE + TILE_SIZE // 2
                
                # Add some sparkle particles
                particle_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                num_particles = 5
                for _ in range(num_particles):
                    # Random position around the center of the tile
                    spread = TILE_SIZE // 2 * (1 - i/frames)  # Particles spread out as tile fades
                    p_x = x + random.randint(-int(spread), int(spread))
                    p_y = y + random.randint(-int(spread), int(spread))
                    
                    # Random size between 2 and 6 pixels
                    p_size = random.randint(2, 6)
                    
                    # Particle color (green/gold with fading alpha)
                    p_color = (200, 255, 100, alpha)
                    
                    # Draw the particle
                    pygame.draw.circle(particle_surface, p_color, (p_x, p_y), p_size)
                
                # Add the particles to the screen
                screen.blit(particle_surface, (0, 0))
        
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
            
            # Add new letter at the top using our smart algorithm
            # Get adjacent letters to consider when placing the new one
            adjacent_letters = []
            # Check left and right neighbors for the top row
            if col > 0 and grid[0][col-1]:
                adjacent_letters.append(grid[0][col-1])
            if col < GRID_SIZE - 1 and grid[0][col+1]:
                adjacent_letters.append(grid[0][col+1])
            # Check the tile below if it exists
            if grid[1][col]:
                adjacent_letters.append(grid[1][col])
                
            grid[0][col] = get_new_letter(adjacent_letters)
            
        # Step 2: Animate the dropping with a simple smooth motion
        steps = 8
        for step in range(steps + 1):
            # Use our consistent background and header function
            draw_background_and_header()
            
            # Draw the grid container
            draw_grid_container()
            
            # Calculate progress of the dropping animation
            progress = step / steps
            
            # Create a dictionary to track animated tile positions
            animated_tiles = {}  # Format: {(row, col): (current_y, letter)}
            
            # First draw all static tiles (all columns except the current one being animated)
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    # Skip the column we're animating
                    if c == col and r < len(empty_spaces):
                        # Calculate the drop position for animated tiles
                        source_y = GRID_Y + (r - 1) * TILE_SIZE
                        if r == 0:
                            source_y = GRID_Y - TILE_SIZE  # Coming from above the grid
                        target_y = GRID_Y + r * TILE_SIZE
                        current_y = source_y + (target_y - source_y) * progress
                        
                        # Store animated tile info
                        animated_tiles[(r, c)] = (current_y, grid[r][c])
                        continue
                    
                    # Draw stationary tiles using helper function
                    x, y = GRID_X + c * TILE_SIZE, GRID_Y + r * TILE_SIZE
                    if grid[r][c]:  # Only draw if there's a letter
                        draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                        pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                        
                        text_surface = FONT.render(grid[r][c], True, TEXT_COLOR)
                        score_surface = SCORE_FONT.render(str(LETTER_SCORES[grid[r][c]]), True, WHITE)
                        screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                        screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))
            
            # Now draw all animated tiles on top
            for (r, c), (current_y, letter) in animated_tiles.items():
                if letter:  # Only draw if we have a valid letter
                    # Draw the animated tile
                    draw_gradient_tile(screen, GRID_X + c * TILE_SIZE, current_y, TILE_SIZE, TILE_SIZE, 
                                     DARK_PURPLE, LIGHT_PURPLE)
                    pygame.draw.rect(screen, WHITE, 
                                    (GRID_X + c * TILE_SIZE + 1, current_y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                    
                    # Draw letter and score
                    text_surface = FONT.render(letter, True, TEXT_COLOR)
                    score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                    
                    screen.blit(text_surface, (GRID_X + c * TILE_SIZE + TILE_SIZE // 3, current_y + TILE_SIZE // 4))
                    screen.blit(score_surface, (GRID_X + c * TILE_SIZE + TILE_SIZE - 20, current_y + TILE_SIZE - 25))
                    
                    # Add a subtle trail effect
                    if progress > 0.2:
                        trail_surface = pygame.Surface((TILE_SIZE, TILE_SIZE // 4), pygame.SRCALPHA)
                        trail_alpha = int(100 * (1 - progress))  # Trail fades as animation progresses
                        trail_color = (200, 200, 255, trail_alpha)
                        pygame.draw.rect(trail_surface, trail_color, 
                                        (0, 0, TILE_SIZE, TILE_SIZE // 4), 0, border_radius=4)
                        # Position trail behind the falling tile
                        trail_y = current_y - TILE_SIZE // 6
                        screen.blit(trail_surface, (GRID_X + c * TILE_SIZE, trail_y))
            
            pygame.display.flip()
            pygame.time.delay(30)
            
            # Check for quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

def process_valid_words():
    """Check for valid words, update score, and handle tile movements."""
    global score, recommended_swaps, is_paused, pause_start_time, paused_time

    # Step 1: Find valid words
    valid_words = get_words_and_positions()
    if not valid_words:
        # If no words found and timer was paused, resume it
        if is_paused:
            # Calculate how long we were paused and add to total paused time
            current_pause_duration = time.time() - pause_start_time
            paused_time += current_pause_duration
            is_paused = False
        return False  # No valid words found

    # If this is the start of a chain reaction, pause the timer
    if not is_paused:
        is_paused = True
        pause_start_time = time.time()

    # Clear recommendations during animations
    recommended_swaps = []

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
    else:
        # No more words found, chain reaction is over, resume timer
        if is_paused:
            # Calculate how long we were paused and add to total paused time
            current_pause_duration = time.time() - pause_start_time
            paused_time += current_pause_duration
            is_paused = False

    if valid_words:
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
        
    # Clean up and prepare for final display
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    
    # Create gradient background for the game over box
    for y in range(box_height):
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
      # Sequential text appearance animation
    for i in range(30):
        # Redraw background and box each frame
        screen.blit(overlay, (0, 0))
        screen.blit(box_surface, (box_x, box_y))
        
        # Calculate text transparency for fade-in effect
        alpha = min(255, i * 10)
        
        # Game Over text appears first
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
    
    # If we can't find a grid without words after max attempts,
    # create a grid with minimal valid words by replacing problematic letters
    print(f"Could not find grid with no words after {max_attempts} attempts")
    print("Creating grid with manual fixes...")
    
    # Create an initial grid
    fallback_grid = [[get_new_letter() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Replace tiles that form words with less common letters (Q, Z, X)
    uncommon = ['Q', 'Z', 'X', 'J', 'K']
    
    # Check and fix rows
    for r in range(GRID_SIZE):
        row_str = ''.join(fallback_grid[r])
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    # Replace middle letter with uncommon letter
                    mid = start + (end - start) // 2
                    fallback_grid[r][mid] = random.choice(uncommon)
    
    # Check and fix columns
    for c in range(GRID_SIZE):
        col_str = ''.join(fallback_grid[r][c] for r in range(GRID_SIZE))
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    # Replace middle letter with uncommon letter
                    mid = start + (end - start) // 2
                    fallback_grid[mid][c] = random.choice(uncommon)
    
    return fallback_grid


# Game loop
running = True
game_over = False

while running:
    # Check for game over conditions - account for paused time
    if is_paused:
        current_pause_duration = time.time() - pause_start_time
        total_paused = paused_time + current_pause_duration
    else:
        total_paused = paused_time

    elapsed_time = int(time.time() - start_time - total_paused)
    time_over = elapsed_time >= TIMER_START
    moves_over = moves_left <= 0

    if (time_over or moves_over) and not game_over:
        if is_paused:
            is_paused = False
            paused_time += (time.time() - pause_start_time)
        
        game_over = True
        show_game_over_menu()
        running = False
        continue
    
    # Draw the game interface 
    # draw_grid now calls draw_background_and_header internally
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Check if the "Hint" button was clicked
            hint_button_x = WIDTH - 110
            hint_button_y = HEADER_HEIGHT // 2 - 20
            if hint_button_x <= x <= hint_button_x + 100 and hint_button_y <= y <= hint_button_y + 40:
                if hints_used < 3:  # Only allow hints if the player has hints remaining
                    hints_used += 1
                    greedy_best_first_search_for_swaps()  # Calculate the top 3 recommended moves
            
            # Handle tile selection and swapping
            elif y > HEADER_HEIGHT and moves_left > 0 and not time_over:
                # Adjust for grid position
                grid_x = x - GRID_X
                grid_y = y - GRID_Y
                
                # Check if click is within grid bounds
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    col = grid_x // TILE_SIZE
                    row = grid_y // TILE_SIZE                    
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:  # Ensure within bounds
                        if selected_tile is None:
                            # Set this tile as selected
                            selected_tile = (row, col)
                            
                            # Create a quick "selected" flash effect
                            flash_x = GRID_X + col * TILE_SIZE
                            flash_y = GRID_Y + row * TILE_SIZE
                            flash_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            flash_surface.fill((255, 255, 255, 180))  # White flash
                            screen.blit(flash_surface, (flash_x, flash_y))
                            pygame.display.update(pygame.Rect(flash_x, flash_y, TILE_SIZE, TILE_SIZE))
                            pygame.time.delay(50)  # Brief delay for the flash effect
                        else:
                            # Check if tiles are adjacent
                            if abs(row - selected_tile[0]) + abs(col - selected_tile[1]) == 1:
                                animate_swap(selected_tile, (row, col))
                                recommended_swaps = []  # Clear recommendations after a swap
                            
                            # Always clear selection
                            selected_tile = None
                            # Redraw the grid to remove selection highlight
                            draw_grid()
                            pygame.display.update()

    pygame.display.flip()

pygame.quit()