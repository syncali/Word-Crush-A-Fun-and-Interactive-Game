import pygame
import random
import time
import math

pygame.init()

WIDTH, HEIGHT = 600, 700
GRID_SIZE = 6
TILE_SIZE = WIDTH // GRID_SIZE
HEADER_HEIGHT = 100
ANIMATION_SPEED = 15
TOTAL_MOVES = 10
TIMER_START = 180

LETTER_SCORES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1,
    "J": 8, "K": 5, "L": 1, "M": 3, "N": 1, "O": 1, "P": 3, "Q": 10, "R": 1,
    "S": 1, "T": 1, "U": 1, "V": 4, "W": 4, "X": 8, "Y": 4, "Z": 10
}

LETTER_DISTRIBUTION = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3, 'H': 2, 'I': 9,
    'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2, 'Q': 1, 'R': 6,
    'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1
}

LETTER_POOL = []
for letter, count in LETTER_DISTRIBUTION.items():
    LETTER_POOL.extend([letter] * count)

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

FONT = pygame.font.Font(None, 50)
HEADER_FONT = pygame.font.Font(None, 40)
SCORE_FONT = pygame.font.Font(None, 20)
LARGE_FONT = pygame.font.Font(None, 80)

try:
    import nltk
    from nltk.corpus import words
    
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words', quiet=True)
    
    word_list = {word.upper() for word in words.words() if len(word) >= 3}
    print(f"Loaded {len(word_list)} words from NLTK corpus")
except ImportError:
    print("NLTK not installed, using fallback dictionary")
    word_list = {"CAT", "DOG", "PIG", "BAT", "HAT", "RUN", "SIT", "FLY", "BIG", 
                "RED", "MAP", "PIN", "CUP", "BOX", "CAR", "BUS", "SUN", "AIR",
                "SEA", "TOP", "LOW", "HOT", "ICE", "ONE", "TWO", "EAT", "TEN"}
    
def check_word(word):
    return word in word_list and len(word) >= 3

def get_new_letter():
    vowels = ['A', 'E', 'I', 'O', 'U']
    
    if random.random() < 0.4:
        vowel_weights = {v: LETTER_DISTRIBUTION[v] for v in vowels}
        total = sum(vowel_weights.values())
        r = random.random() * total
        cumulative = 0
        for vowel, weight in vowel_weights.items():
            cumulative += weight
            if r <= cumulative:
                return vowel
    
    return random.choice(LETTER_POOL)


def generate_grid_without_words():
    attempts = 0
    max_attempts = 100
    
    while attempts < max_attempts:
        attempts += 1
        
        new_grid = [[get_new_letter() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        valid_words_found = False
        
        for r in range(GRID_SIZE):
            row_str = ''.join(new_grid[r])
            for start in range(GRID_SIZE - 2):
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
            for c in range(GRID_SIZE):
                col_str = ''.join(new_grid[r][c] for r in range(GRID_SIZE))
                for start in range(GRID_SIZE - 2):
                    for end in range(start + 2, GRID_SIZE):
                        word = col_str[start:end+1]
                        if check_word(word):
                            valid_words_found = True
                            break
                    if valid_words_found:
                        break
                if valid_words_found:
                    break
        
        if not valid_words_found:
            print(f"Found grid with no words after {attempts} attempts")
            return new_grid
    
    print(f"Could not find grid with no words after {max_attempts} attempts")
    print("Creating grid with manual fixes...")
    
    fallback_grid = [[get_new_letter() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    uncommon = ['Q', 'Z', 'X', 'J', 'K']
    
    for r in range(GRID_SIZE):
        row_str = ''.join(fallback_grid[r])
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    mid = start + (end - start) // 2
                    fallback_grid[r][mid] = random.choice(uncommon)
    
    for c in range(GRID_SIZE):
        col_str = ''.join(fallback_grid[r][c] for r in range(GRID_SIZE))
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    mid = start + (end - start) // 2
                    fallback_grid[mid][c] = random.choice(uncommon)
    
    return fallback_grid


grid = generate_grid_without_words()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Word Puzzle Game")

selected_tile = None
moves_left = TOTAL_MOVES
score = 0
start_time = time.time()


def draw_gradient_tile(surface, x, y, width, height, color1, color2, opacity=255):
    temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        r = color1[0] + (color2[0] - color1[0]) * (i / height)
        g = color1[1] + (color2[1] - color1[1]) * (i / height)
        b = color1[2] + (color2[2] - color1[2]) * (i / height)
        pygame.draw.line(temp_surface, (int(r), int(g), int(b), opacity), (0, i), (width, i))
    surface.blit(temp_surface, (x, y))


def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * TILE_SIZE, row * TILE_SIZE + HEADER_HEIGHT
            opacity = 200 if selected_tile == (row, col) else 255
            draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE, opacity)
            pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
            
            letter = grid[row][col]
            text_surface = FONT.render(letter, True, TEXT_COLOR)
            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)

            screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
            screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))


def draw_header():
    global moves_left, score
    screen.fill(WHITE, (0, 0, WIDTH, HEADER_HEIGHT))

    elapsed_time = int(time.time() - start_time)
    remaining_time = max(0, TIMER_START - elapsed_time)
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f"{minutes}:{seconds:02d}"

    headers = ["Time", "Moves", "Score"]
    values = [timer_text, str(moves_left), str(score)]
    cell_width = WIDTH // len(headers)

    for i in range(len(headers)):
        pygame.draw.rect(screen, DARK_PURPLE, (i * cell_width, 0, cell_width, HEADER_HEIGHT), 2)

        header_surface = HEADER_FONT.render(headers[i], True, BLACK)
        value_surface = HEADER_FONT.render(values[i], True, DARK_PURPLE)

        screen.blit(header_surface, (i * cell_width + (cell_width // 2 - header_surface.get_width() // 2), 15))
        screen.blit(value_surface, (i * cell_width + (cell_width // 2 - value_surface.get_width() // 2), 55))


def animate_swap(pos1, pos2):
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

    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
    moves_left -= 1
    
    process_valid_words()

def get_words_and_positions():
    all_words = []
    
    for r in range(GRID_SIZE):
        row_str = ''.join(grid[r])
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    positions = [(r, start + i) for i in range(end - start + 1)]
                    all_words.append((word, positions))
    
    for c in range(GRID_SIZE):
        col_chars = [grid[r][c] for r in range(GRID_SIZE)]
        col_str = ''.join(col_chars)
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    positions = [(start + i, c) for i in range(end - start + 1)]
                    all_words.append((word, positions))
    
    valid_words = []
    
    all_words.sort(key=lambda x: len(x[0]), reverse=True)
    
    covered_positions = set()
    
    for word, positions in all_words:
        pos_set = set(positions)
        
        if not any(pos in covered_positions for pos in pos_set):
            valid_words.append((word, positions))
            covered_positions.update(pos_set)
    
    return valid_words

def calculate_word_score(word):
    return sum(LETTER_SCORES[letter] for letter in word)

def highlight_words(words_positions):
    if not words_positions:
        return
    
    highlight_time = 1500
    frames = 30
    delay_per_frame = highlight_time // frames
    
    for i in range(frames):
        screen.fill(WHITE)
        draw_header()
        draw_grid()
        
        progress = i / frames
        
        scale_factor = min(1.0, progress * 2)
        alpha = min(255, progress * 510)
        
        for word, positions in words_positions:
            word_score = calculate_word_score(word)
            
            avg_row = sum(pos[0] for pos in positions) / len(positions)
            avg_col = sum(pos[1] for pos in positions) / len(positions)
            center_x = avg_col * TILE_SIZE + TILE_SIZE // 2
            center_y = avg_row * TILE_SIZE + HEADER_HEIGHT + TILE_SIZE // 2
            
            if len(positions) > 1:
                if all(pos[0] == positions[0][0] for pos in positions):
                    sorted_pos = sorted(positions, key=lambda pos: pos[1])
                else:
                    sorted_pos = sorted(positions, key=lambda pos: pos[0])
                
                line_points = [(p[1] * TILE_SIZE + TILE_SIZE // 2, 
                              p[0] * TILE_SIZE + HEADER_HEIGHT + TILE_SIZE // 2) for p in sorted_pos]
                
                line_width = int(4 + 3 * scale_factor)
                line_color = (100, 255, 100, min(180, int(alpha * 0.7)))
                
                line_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.lines(line_surface, line_color, False, line_points, line_width)
                screen.blit(line_surface, (0, 0))
            
            for r, c in positions:
                x, y = c * TILE_SIZE, r * TILE_SIZE + HEADER_HEIGHT
                
                grow_amount = int(TILE_SIZE * 0.2 * scale_factor)
                highlight_x = x - grow_amount // 2
                highlight_y = y - grow_amount // 2
                highlight_size = TILE_SIZE + grow_amount
                
                highlight_surface = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
                highlight_color = (100, 255, 100, min(100, int(alpha * 0.4)))
                pygame.draw.rect(highlight_surface, highlight_color, 
                                (0, 0, highlight_size, highlight_size), 0, border_radius=8)
                screen.blit(highlight_surface, (highlight_x, highlight_y))
                
                border_color = (0, 200, 0, min(255, int(alpha)))
                border_width = max(2, int(3 * scale_factor))
                pygame.draw.rect(screen, border_color, 
                                (x, y, TILE_SIZE, TILE_SIZE), 
                                border_width, border_radius=4)
            
            if progress > 0.2:
                if len(positions) > 2:
                    disp_x = center_x - 20 * len(word)
                    disp_y = center_y - TILE_SIZE * 1.5
                else:
                    disp_x = positions[0][1] * TILE_SIZE
                    disp_y = positions[0][0] * TILE_SIZE + HEADER_HEIGHT - TILE_SIZE
                
                float_offset = math.sin(progress * math.pi * 2) * 5
                disp_y += float_offset
                
                word_alpha = min(255, int((progress - 0.2) * 425))
                
                word_text = f"{word}: +{word_score}"
                text_size = HEADER_FONT.size(word_text)
                panel_width = text_size[0] + 20
                panel_height = text_size[1] + 10
                
                panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                bg_color = (0, 0, 0, min(180, int(word_alpha * 0.7)))
                pygame.draw.rect(panel_surface, bg_color, 
                                (0, 0, panel_width, panel_height), 
                                0, border_radius=8)
                
                border_color = (50, 255, 50, word_alpha)
                pygame.draw.rect(panel_surface, border_color, 
                                (0, 0, panel_width, panel_height), 
                                2, border_radius=8)
                
                panel_x = disp_x - 10
                panel_y = disp_y - 5
                screen.blit(panel_surface, (panel_x, panel_y))
                
                word_surface = HEADER_FONT.render(word_text, True, (220, 255, 220))
                word_surface.set_alpha(word_alpha)
                
                text_x = panel_x + (panel_width - text_size[0]) // 2
                text_y = panel_y + (panel_height - text_size[1]) // 2
                screen.blit(word_surface, (text_x, text_y))
        
        pygame.display.flip()
        pygame.time.delay(delay_per_frame)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

def pop_tiles(positions):
    empty_positions = set(positions)
    if not empty_positions:
        return
    
    frames = 10
    for i in range(frames):
        screen.fill(WHITE)
        draw_header()
        
        alpha = 255 - int((i / frames) * 255)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = col * TILE_SIZE, row * TILE_SIZE + HEADER_HEIGHT
                
                if (row, col) in empty_positions:
                    temp_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    draw_gradient_tile(temp_surface, 0, 0, TILE_SIZE, TILE_SIZE, 
                                     DARK_PURPLE, LIGHT_PURPLE, alpha)
                    
                    letter = grid[row][col]
                    if letter:
                        text_color = (TEXT_COLOR[0], TEXT_COLOR[1], TEXT_COLOR[2], alpha)
                        text_surface = FONT.render(letter, True, text_color)
                        temp_surface.blit(text_surface, (TILE_SIZE // 3, TILE_SIZE // 4))
                    
                    screen.blit(temp_surface, (x, y))
                else:
                    draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                    pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                    
                    letter = grid[row][col]
                    if letter:
                        text_surface = FONT.render(letter, True, TEXT_COLOR)
                        score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                        
                        screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                        screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))
        
        pygame.display.flip()
        pygame.time.delay(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
    
    for row, col in positions:
        grid[row][col] = None

def drop_new_tiles():
    for col in range(GRID_SIZE):
        empty_spaces = []
        for row in range(GRID_SIZE):
            if grid[row][col] is None:
                empty_spaces.append(row)
        
        if not empty_spaces:
            continue
        
        for empty_row in sorted(empty_spaces):
            for row in range(empty_row, 0, -1):
                grid[row][col] = grid[row-1][col]
            
            grid[0][col] = random.choice(LETTER_POOL)
        
        steps = 8
        for step in range(steps + 1):
            screen.fill(WHITE)
            draw_header()
            
            progress = step / steps
            
            for row in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if c == col and row < len(empty_spaces):
                        source_y = (row - 1) * TILE_SIZE + HEADER_HEIGHT
                        if row == 0:
                            source_y = -TILE_SIZE + HEADER_HEIGHT
                        target_y = row * TILE_SIZE + HEADER_HEIGHT
                        current_y = source_y + (target_y - source_y) * progress
                        
                        draw_gradient_tile(screen, c * TILE_SIZE, current_y, TILE_SIZE, TILE_SIZE, 
                                          DARK_PURPLE, LIGHT_PURPLE)
                        pygame.draw.rect(screen, WHITE, 
                                        (c * TILE_SIZE + 1, current_y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                        
                        letter = grid[row][c]
                        if letter:
                            text_surface = FONT.render(letter, True, TEXT_COLOR)
                            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                            
                            screen.blit(text_surface, (c * TILE_SIZE + TILE_SIZE // 3, current_y + TILE_SIZE // 4))
                            screen.blit(score_surface, (c * TILE_SIZE + TILE_SIZE - 20, current_y + TILE_SIZE - 25))
                    else:
                        x, y = c * TILE_SIZE, row * TILE_SIZE + HEADER_HEIGHT
                        draw_gradient_tile(screen, x, y, TILE_SIZE, TILE_SIZE, DARK_PURPLE, LIGHT_PURPLE)
                        pygame.draw.rect(screen, WHITE, (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2)
                        
                        letter = grid[row][c]
                        if letter:
                            text_surface = FONT.render(letter, True, TEXT_COLOR)
                            score_surface = SCORE_FONT.render(str(LETTER_SCORES[letter]), True, WHITE)
                            
                            screen.blit(text_surface, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                            screen.blit(score_surface, (x + TILE_SIZE - 20, y + TILE_SIZE - 25))
            
            pygame.display.flip()
            pygame.time.delay(30)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

def process_valid_words():
    global score
    
    valid_words = get_words_and_positions()
    if not valid_words:
        return False
    
    highlight_words(valid_words)
    
    all_positions = set()
    for word, positions in valid_words:
        word_score = calculate_word_score(word)
        score += word_score
        for pos in positions:
            all_positions.add(pos)
    
    pop_tiles(all_positions)
    
    drop_new_tiles()
    
    if get_words_and_positions():
        pygame.time.delay(300)
        process_valid_words()
    
    return True

def show_game_over_menu():
    global score
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))
    
    box_width, box_height = 400, 300
    box_x = WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2
    
    for i in range(20):
        screen.blit(overlay, (0, 0))
        
        scale = i / 20.0
        current_width = int(box_width * scale)
        current_height = int(box_height * scale)
        current_x = WIDTH // 2 - current_width // 2
        current_y = HEIGHT // 2 - current_height // 2
        
        box_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        for y in range(current_height):
            progress = y / current_height
            r = GAME_OVER_BG[0] + (DARK_PURPLE[0] - GAME_OVER_BG[0]) * progress
            g = GAME_OVER_BG[1] + (DARK_PURPLE[1] - GAME_OVER_BG[1]) * progress
            b = GAME_OVER_BG[2] + (DARK_PURPLE[2] - GAME_OVER_BG[2]) * progress
            pygame.draw.line(box_surface, (int(r), int(g), int(b)), 
                            (0, y), (current_width, y))
        
        if i > 10:
            border_radius = min(15, int(15 * scale))
            pygame.draw.rect(box_surface, WHITE, 
                            (0, 0, current_width, current_height), 
                            3, border_radius=border_radius)
        
        screen.blit(box_surface, (current_x, current_y))
        pygame.display.flip()
        pygame.time.delay(20)
    
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    for y in range(box_height):
        progress = y / box_height
        r = GAME_OVER_BG[0] + (DARK_PURPLE[0] - GAME_OVER_BG[0]) * progress
        g = GAME_OVER_BG[1] + (DARK_PURPLE[1] - GAME_OVER_BG[1]) * progress
        b = GAME_OVER_BG[2] + (DARK_PURPLE[2] - GAME_OVER_BG[2]) * progress
        pygame.draw.line(box_surface, (int(r), int(g), int(b)), 
                        (0, y), (box_width, y))
    
    pygame.draw.rect(box_surface, WHITE, 
                    (0, 0, box_width, box_height), 
                    4, border_radius=15)
    
    for i in range(30):
        screen.blit(overlay, (0, 0))
        screen.blit(box_surface, (box_x, box_y))
        
        alpha = min(255, i * 10)
        
        if i > 5:
            game_over_text = LARGE_FONT.render("GAME OVER", True, WHITE)
            game_over_text.set_alpha(alpha)
            text_x = WIDTH // 2 - game_over_text.get_width() // 2
            text_y = box_y + 50
            screen.blit(game_over_text, (text_x, text_y))
        
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
        
        if i > 25:
            continue_text = SCORE_FONT.render("Click anywhere to exit", True, WHITE)
            continue_text.set_alpha(alpha)
            continue_x = WIDTH // 2 - continue_text.get_width() // 2
            continue_y = box_y + box_height - 30
            screen.blit(continue_text, (continue_x, continue_y))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
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
    
    print(f"Could not find grid with no words after {max_attempts} attempts")
    print("Creating grid with manual fixes...")
    
    fallback_grid = [[get_new_letter() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    uncommon = ['Q', 'Z', 'X', 'J', 'K']
    
    for r in range(GRID_SIZE):
        row_str = ''.join(fallback_grid[r])
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = row_str[start:end+1]
                if check_word(word):
                    mid = start + (end - start) // 2
                    fallback_grid[r][mid] = random.choice(uncommon)
    
    for c in range(GRID_SIZE):
        col_str = ''.join(fallback_grid[r][c] for r in range(GRID_SIZE))
        for start in range(GRID_SIZE - 2):
            for end in range(start + 2, GRID_SIZE):
                word = col_str[start:end+1]
                if check_word(word):
                    mid = start + (end - start) // 2
                    fallback_grid[mid][c] = random.choice(uncommon)
    
    return fallback_grid


running = True
game_over = False

while running:
    elapsed_time = int(time.time() - start_time)
    time_over = elapsed_time >= TIMER_START
    moves_over = moves_left <= 0
    
    if (time_over or moves_over) and not game_over:
        game_over = True
        show_game_over_menu()
        running = False
        continue

    screen.fill(WHITE)
    draw_header()
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and moves_left > 0 and not time_over:
            x, y = event.pos
            if y > HEADER_HEIGHT:
                col, row = x // TILE_SIZE, (y - HEADER_HEIGHT) // TILE_SIZE
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if selected_tile is None:
                        selected_tile = (row, col)
                    else:
                        if abs(row - selected_tile[0]) + abs(col - selected_tile[1]) == 1:
                            animate_swap(selected_tile, (row, col))
                        selected_tile = None

    pygame.display.flip()

pygame.quit()
