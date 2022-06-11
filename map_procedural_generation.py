"""
This project is about making terrain using procedural generation utilizing perlin noise and other techniques.
Working towards making both infinite and finite "worlds" based on different seeds generation
"""

import math
import sys

import numpy as np
import pygame
from noise import pnoise2

# from time import time
# from PIL import Image

"""
TODO:   1. try voronoi diagrams instead of pixel coloring
        2. add ability to change seed in infinite world
        3. add a menu, let choose resolution and load worlds, choose mode
        4. add ability to save, both seed and coordinates, resolution and more
        5. add rivers and trails (using path finding/gradient decent or voronoi edges?)
        6. add path finding?, add objective?, find usage?
        7. add biomes?, seasons/day night cycle?
"""


def create_round_gradient(map_width=800, map_height=600):
    """
    Creates a 2D matrix with float values between 0 and 1 in a round shape (1 in the center and then lowering)

    Logic: calculating the distance from the center and inverting them
    """
    min_edge = min(map_width, map_height)  # might be a better constant than center_to_edge for wider screens
    center_to_edge = (math.sqrt(map_width ** 2 + map_height ** 2) // 2)  # utilized triangle geometry, the median on
    # the hypotenuse of a right triangle divides the triangle into two isosceles triangles, because the median equals
    # one half the hypotenuse
    gradient_map = np.zeros((map_width, map_height))
    map_center = (map_width // 2, map_height // 2)
    for i in range(map_width):
        for j in range(map_height):
            gradient_map[i][j] = abs(1 - (math.dist(map_center, (i, j)) / center_to_edge)) ** 1.5

    return gradient_map


def create_perlin_map():
    """
    Creates a 2D matrix with values between -0.5 and 0.5 using perlin noise

    scale: determines at what "distance" to view the noisemap
    octaves: the number of layers of noise stacked on each other
    persistence: determines the height for each octave (z axis = persistence^(octave-1))
    lacunarity: determines the "spread" (adjusts frequency) for each octave (x,y axes) (scale = lacunarity^(octave-1))
    seed: makes a whole different perlin map, and therefore a different "world"
    """
    width, height = 800, 600
    scale = 100.0
    octaves = 6
    persistence = 0.35
    lacunarity = 2.0

    noise_map = np.zeros((height, width) + (3,))
    for i in range(height):
        for j in range(width):
            noise_map[i][j] = pnoise2(i / scale, j / scale, octaves=octaves, persistence=persistence,
                                      lacunarity=lacunarity, base=42)
    return noise_map


def color_by_amplitude(amplitude, threshold):
    """
    assigns RGB color by amplitude

    amplitude: value usually received from perlin noise
    """

    color = (0, 0, 0)

    colors = {"light_blue": (27, 127, 196),
              "medium_blue": (20, 103, 199),
              "blue": (11, 74, 212),
              "dark_blue": (11, 65, 181),
              "light_sand": (205, 182, 115),
              "sand": (199, 149, 95),
              "dark_sand": (172, 130, 78),
              "light_green": (106, 171, 56),
              "green": (56, 158, 35),
              "dark_green": (28, 140, 24),
              "darkest_green": (35, 124, 24),
              "dark_mountain": (90, 160, 79),
              "mountain": (120, 120, 120),
              "medium_mountain": (107, 107, 107),
              "light_mountain": (89, 89, 89),
              "snow": (255, 255, 255)}

    if amplitude < -0.2 + threshold:
        color = colors["dark_blue"]
    elif amplitude < -0.075 + threshold:
        color = colors["blue"]
    elif amplitude < 0.0 + threshold:
        color = colors["medium_blue"]
    elif amplitude < 0.05 + threshold:
        color = colors["light_blue"]
    # if amplitude < 0.05:
    #     color = (0, 0, 100 + abs(300 * amplitude))
    elif amplitude < 0.07 + threshold:
        color = colors["light_sand"]
    elif amplitude < 0.085 + threshold:
        color = colors["sand"]
    elif amplitude < 0.095 + threshold:
        color = colors["dark_sand"]
    elif amplitude < 0.16 + threshold:
        color = colors["darkest_green"]
    elif amplitude < 0.23 + threshold:
        color = colors["dark_green"]
    elif amplitude < 0.3 + threshold:
        color = colors["green"]
    elif amplitude < 0.335 + threshold:
        color = colors["light_green"]
    elif amplitude < 0.36 + threshold:
        color = colors["dark_mountain"]
    elif amplitude < 0.38 + threshold:
        color = colors["mountain"]
    elif amplitude < 0.415 + threshold:
        color = colors["medium_mountain"]
    elif amplitude < 0.495 + threshold:
        color = colors["light_mountain"]
    elif amplitude < 1 + threshold:
        color = colors["snow"]

    return color


def create_infinite_map(map_width=800, map_height=600, horizontal_coordinates=0, vertical_coordinates=0, scale=300,
                        octaves=5, persistence=0.6, lacunarity=2.0, seed=0):
    """
    Creates a 2D matrix with RGB values, representing an image of terrain

    Logic: assigns a value for each pixel using 2D perlin noise and then assigns a color to the pixel according
           to the value

    Complexity: creating the matrix by calculating the perlin noise values and assigning colors in the same loop saves
                time by not having to iterate over the entire matrix twice

    scale: determines at what "distance" to view the noisemap
    octaves: the number of layers of noise stacked on each other
    persistence: determines the height for each octave (z axis = persistence^(octave-1))
    lacunarity: determines the "spread" (adjusts frequency) for each octave (x,y axes) (scale = lacunarity^(octave-1))
    seed: makes a whole different perlin map, and therefore a different "world"
    """

    game_map = np.empty((map_width, map_height) + (3,), dtype=np.uint8)  # creates an "empty" map
    threshold = 0.5
    for i in range(map_width):
        for j in range(map_height):
            amplitude = (pnoise2((i + vertical_coordinates) / scale, (j + horizontal_coordinates) / scale,
                                 octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                                 base=seed) + threshold)
            game_map[i][j] = color_by_amplitude(amplitude, threshold)
    return game_map


def create_finite_map(gradient, map_width, map_height, octaves, persistence, lacunarity, seed, scale):
    """
    Creates a 2D matrix with RGB values, representing an image of terrain while utilizing a round gradient to surround
    the terrain with water

    Logic: assigns a value for each pixel using 2D perlin noise and then assigns a color to the pixel according
           to the value

    Complexity: creating the matrix by calculating the perlin noise values and assigning colors in the same loop saves
                time by not having to iterate over the entire matrix twice

    scale: determines at what "distance" to view the noisemap
    octaves: the number of layers of noise stacked on each other
    persistence: determines the height for each octave (z axis = persistence^(octave-1))
    lacunarity: determines the "spread" (adjusts frequency) for each octave (x,y axes) (scale = lacunarity^(octave-1))
    seed: makes a whole different perlin map, and therefore a different "world"
    """
    game_map = np.empty((map_width, map_height) + (3,), dtype=np.uint8)  # creates an "empty" map
    threshold = 0.15
    for i in range(map_width):
        for j in range(map_height):
            amplitude = (pnoise2(i / scale, j / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity,
                                 base=seed) + 0.5) * gradient[i][j]
            game_map[i][j] = color_by_amplitude(amplitude, threshold)
    return game_map


"""
The following 4 functions allow movement within the terrain
 
Logic: removes a slice of width/height of the matrix and calculates the next slice and stacks them

Complexity: by removing and calculating slices instead of the entire map again this gains a massive performance boost

moving_speed: the size of each slice in pixels
horizontal_offset: the user's horizontal coordinates displacement from the center (0, 0) in pixels
vertical_offset: the user's vertical coordinates displacement from the center (0, 0) in pixels
"""


def move_down(width, height, moving_speed, game_map, horizontal_offset, vertical_offset, seed):
    game_map = game_map[:, moving_speed:]  # slices the part the user moved from
    game_map = np.hstack(
        (game_map, create_infinite_map(width, moving_speed, horizontal_coordinates=height + horizontal_offset,
                                       vertical_coordinates=vertical_offset, seed=seed)))
    # calculates the new slice and joins it to the main map
    return game_map


def move_up(width, height, moving_speed, game_map, horizontal_offset, vertical_offset, seed):
    game_map = game_map[:, :height - moving_speed]  # slices the part the user moved from
    game_map = np.hstack(
        (create_infinite_map(width, moving_speed, horizontal_coordinates=-moving_speed + horizontal_offset,
                             vertical_coordinates=vertical_offset, seed=seed), game_map))
    # calculates the new slice and joins it to the main map
    return game_map


def move_right(width, height, moving_speed, game_map, horizontal_offset, vertical_offset, seed):
    game_map = game_map[moving_speed:, :]  # slices the part the user moved from
    game_map = np.vstack(
        (game_map, create_infinite_map(moving_speed, height, horizontal_coordinates=horizontal_offset,
                                       vertical_coordinates=width + vertical_offset, seed=seed)))
    # calculates the new slice and joins it to the main map
    return game_map


def move_left(width, height, moving_speed, game_map, horizontal_offset, vertical_offset, seed):
    game_map = game_map[:width - moving_speed, :]  # slices the part the user moved from
    game_map = np.vstack((create_infinite_map(moving_speed, height, horizontal_coordinates=horizontal_offset,
                                              vertical_coordinates=-moving_speed + vertical_offset, seed=seed),
                          game_map))
    # calculates the new slice and joins it to the main map
    return game_map


def infinite_map_loop(width, height, moving_speed, vertical_offset, horizontal_offset):
    """
    Creates a window using the pygame module, then calls the relevant functions in order to make a terrain map and
    allowing movement within the terrain

    width: width resolution in pixels
    height: height resolution in pixels
    moving_speed: moving speed in pixels per moving action
    vertical_offset: variable following the user's vertical coordinates displacement from the center (0, 0)
    horizontal_offset: variable following the user's horizontal coordinates displacement from the center (0, 0)
    """
    game_map = create_infinite_map(width, height, lacunarity=2.0, persistence=0.5)
    # im = Image.fromarray(game_map)
    # im.show()
    seed = 0
    pygame.init()
    display = pygame.display.set_mode((width, height))
    pygame.display.set_caption('World explorer')
    while True:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if events.key == pygame.K_UP:
                    game_map = move_up(width, height, moving_speed, game_map, horizontal_offset, vertical_offset, seed)
                    horizontal_offset -= moving_speed
                if events.key == pygame.K_DOWN:
                    game_map = move_down(width, height, moving_speed, game_map, horizontal_offset, vertical_offset,
                                         seed)
                    horizontal_offset += moving_speed
                if events.key == pygame.K_RIGHT:
                    game_map = move_right(width, height, moving_speed, game_map, horizontal_offset, vertical_offset,
                                          seed)
                    vertical_offset += moving_speed
                if events.key == pygame.K_LEFT:
                    game_map = move_left(width, height, moving_speed, game_map, horizontal_offset, vertical_offset,
                                         seed)
                    vertical_offset -= moving_speed
                if events.key == pygame.K_w:
                    seed += 1
                    horizontal_offset = 0
                    vertical_offset = 0
                    game_map = create_infinite_map(width, height, horizontal_offset, vertical_offset, seed=seed)
                if events.key == pygame.K_s:
                    seed -= 1
                    horizontal_offset = 0
                    vertical_offset = 0
                    game_map = create_infinite_map(width, height, horizontal_offset, vertical_offset, seed=seed)
        font = pygame.font.SysFont('arial bold', 30)
        seed_text = font.render('SEED: ' + str(seed), True, (255, 255, 255))
        pygame.pixelcopy.array_to_surface(display, game_map)
        display.blit(seed_text, (10, height - 25))
        pygame.display.flip()


def finite_map_loop(width, height):
    """
    Creates a window using the pygame module, then calls the relevant functions in order to make a terrain map and
    allowing changing values within the terrain

    width: width resolution in pixels
    height: height resolution in pixels
    vertical_offset: variable following the user's vertical coordinates displacement from the center (0, 0)
    horizontal_offset: variable following the user's horizontal coordinates displacement from the center (0, 0)
    """
    scale = 200
    octaves = 5
    persistence = 0.5
    lacunarity = 2.0
    seed = 0
    gradient = create_round_gradient(width, height)
    game_map = create_finite_map(gradient, width, height, octaves, persistence, lacunarity, seed, scale)
    # im = Image.fromarray(game_map)
    # im.show()
    pygame.init()
    display = pygame.display.set_mode((width, height))
    pygame.display.set_caption('World explorer')
    while True:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if events.key == pygame.K_UP:
                    seed += 1
                    game_map = create_finite_map(gradient, width, height, octaves, persistence, lacunarity, seed, scale)
                if events.key == pygame.K_DOWN:
                    seed -= 1
                    game_map = create_finite_map(gradient, width, height, octaves, persistence, lacunarity, seed, scale)
        font = pygame.font.SysFont('arial bold', 30)
        seed_text = font.render('SEED: ' + str(seed), True, (255, 255, 255))
        pygame.pixelcopy.array_to_surface(display, game_map)
        display.blit(seed_text, (10, height - 25))
        pygame.display.flip()


def main():
    width, height = 1000, 1000  # resolution in pixels
    moving_speed = 40  # moving speed in pixels per moving action
    vertical_offset = 0  # variable following the user's vertical coordinates displacement from the center (0, 0)
    horizontal_offset = 0  # variable following the user's horizontal coordinates displacement from the center (0, 0)

    # infinite_map_loop(width, height, moving_speed, vertical_offset, horizontal_offset)
    finite_map_loop(width, height)


if __name__ == "__main__":
    main()
