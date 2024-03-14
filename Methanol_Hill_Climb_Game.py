import pygame
import math, random
import os, sys


# Initialize pygame
os.chdir(sys.path[0])
pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))


# Game variables
car_position = [100, 500]
engine_temp = 195
methanol_supply = 100
distance_climbed = 0.00
game_over = False
game_started = False  # Add this line

# Button variables
button_color = (0, 255, 0)  # Green
button_position = (350, 300)
button_dimensions = (100, 50)

# HUD variables
hud_font = pygame.font.SysFont(None, 25)
car_original_image = pygame.image.load('car_sprite.png')
car_width = 50
car_height = 30
car_original_image = pygame.transform.scale(car_original_image, (car_width, car_height))

# Create a clock object
clock = pygame.time.Clock()

# Terrain generation parameters
terrain_length = 800
terrain = [0] * terrain_length  # Initialize the terrain array with zeros
terrain_height = 100
terrain_amplitude = 100  # The amplitude of the terrain (how high the peaks are)
terrain_frequency = 0.01  # The frequency of the terrain (how often the peaks occur)
terrain_x = 0  # Add this line
terrain_wave_length = 2 * math.pi / terrain_frequency  # The length of each sine wave

def generate_new_terrain_value():
    global terrain_x, terrain_amplitude  # Add this line
    if terrain_x % terrain_wave_length == 0:  # Start a new wave once the previous one stabilizes back at 0
        terrain_amplitude += random.randint(50, 150)  # Increase the amplitude for the next wave
    y = terrain_amplitude * math.sin(terrain_frequency * terrain_x) + screen_height / 2  # Calculate the y-coordinate based on a sine wave
    terrain_x += 1  # Increment the x-coordinate
    return y

# Initialize the terrain with a sine wave
for i in range(terrain_length):
    terrain[i] = generate_new_terrain_value()

# Main game loop
running = True
while running:
    screen.fill((255, 255, 255))
    
    # Cap the frame rate to 1 / 0.3 = ~3 FPS
    clock.tick(20)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Restart game on button click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if pygame.Rect(button_position, button_dimensions).collidepoint(mouse_pos):
                if game_over:
                    # Reset game variables
                    car_position = [100, 500]
                    engine_temp = 195
                    methanol_supply = 100
                    distance_climbed = 0.00
                    game_over = False
                    game_started = False  # Stop the game when it's over
                    
                    
        # Inject methanol if space bar is being held down
        keys = pygame.key.get_pressed()  # Get the state of all keys
        if keys[pygame.K_SPACE]:
            if methanol_supply >= 1 and engine_temp > 5:
                methanol_supply -= 3  # Decrease methanol supply
                # Check if the engine temperature will be less than 170 after cooling
                if engine_temp - 10 < 170:
                    engine_temp = 170  # Set the engine temperature to 170
                else:
                    engine_temp -= 10  # Example cooling effect
                game_started = True  # Start the game when the player injects methanol

    # Game logic for climbing the hill
    if game_started and not game_over:  # Only run the game logic if the game has started and is not over
        distance_climbed += 0.1
        distance_climbed = round(distance_climbed, 1)
        if engine_temp >= 230:
            game_over = True
            
        # Shift terrain to the left
        terrain = terrain[8:] + [generate_new_terrain_value() for _ in range(8)]

    # Adjust car position based on new terrain
    terrain_y = terrain[car_position[0]]  # The y-coordinate of the terrain at the x-coordinate of the car
    car_position[1] = terrain_y - car_height  # Set the car's y-coordinate to the terrain's y-coordinate minus the car's height
    slope = (terrain[(car_position[0] + 1) % terrain_length] - terrain[car_position[0]]) / 8  # Calculate slope
    if (slope < 0 or engine_temp < 195) and not game_over:  # Add condition to check if game is not over
        engine_temp += 2
    
    angle = math.atan(slope)
    if angle < 0:
        angle += math.pi / 4
    else:
        angle = abs(angle)


    # Draw terrain
    for i in range(screen_width):
        pygame.draw.line(screen, (0, 255, 0), (i, terrain[i]), (i, screen_height))
        pygame.draw.line(screen, (0, 0, 0), (i, terrain[i] + 5), (i, terrain[i]))

    car_image = pygame.transform.rotate(car_original_image, math.degrees(angle))
    car_rect = car_image.get_rect(center=car_original_image.get_rect().center)
    screen.blit(car_image, (car_position[0] - car_rect.width // 2, car_position[1] - car_rect.height // 2))

    # Draw HUD
    if engine_temp >= 210:
        text_color = (255, 0, 0)  # Red
    else:
        text_color = (0, 0, 0)  # Black
    
    
    hud_methanol = hud_font.render('Methanol: ' + str(methanol_supply) + "% remaining", True, (0, 0, 0))
    hud_temp = hud_font.render('Engine Temp: ' + str(engine_temp) + "°F", True, text_color)
    hud_distance = hud_font.render('Distance: ' + str(distance_climbed) + " miles", True, (0, 0, 0))
    screen.blit(hud_methanol, (10, 10))
    screen.blit(hud_temp, (10, 40))
    screen.blit(hud_distance, (10, 70))

    # Check for game over
    if game_over:
        font = pygame.font.SysFont(None, 55)
        text = font.render('Game Over', True, (0, 0, 0))
        screen_width, screen_height = pygame.display.get_surface().get_size()
        y_offset = 250
        screen.blit(text, ((screen_width - font.size('Game Over')[0]) // 2, (screen_height - font.size('Game Over')[1]) // 2 - y_offset))

        # Draw restart button
        button_rect = pygame.Rect(button_position, button_dimensions)  # Create a rectangle for the button
        pygame.draw.rect(screen, (0, 0, 0), button_rect)  # Change button color to black
        button_font = pygame.font.SysFont(None, 25)
        button_text = button_font.render('Restart', True, (255, 255, 255))  # Change font color to white

        # Calculate the center of the button
        button_center = (button_rect.x + button_rect.width // 2, button_rect.y + button_rect.height // 2)

        # Calculate the position of the text
        text_width, text_height = button_font.size('Restart')
        text_position = (button_center[0] - text_width // 2, button_center[1] - text_height // 2)

        screen.blit(button_text, text_position)

    # Update display
    pygame.display.flip()

# Clean up
pygame.quit()