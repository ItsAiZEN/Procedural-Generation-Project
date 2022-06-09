import math
import sys

import numpy as np
import pygame
from noise import pnoise2

# from time import time
# from PIL import Image

"""
This project is about making terrain using procedural generation utilizing perlin noise and other techniques.
Working towards making both infinite and finite "worlds" based on different seeds generation

WIP: adding a menu, experimenting with voronoi diagrams instead of each pixel coloring (will add certain style to the
     terrain and might improve running time, also trying to differentiate between an infinite map and a finite map,
     the finite map should use the round gradient and might add several special details that are more complex to add
     to an infinite map
"""


def create_round_gradient(map_width=800, map_height=600):
    """
    Creates a 2D matrix with float values between 0 and 1 in a round shape (1 in the center and then lowering)

    Logic: calculating the distance from the center and inverting them
    """
    gradient_map = np.zeros((map_width, map_height))
    for i in range(map_width):
        for j in range(map_height):
            gradient_map[i][j] = (
                abs(1 - (math.dist((map_width // 2, map_height // 2), (i, j))) / (max(map_width, map_height) // 2)))
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


def create_colored_map(map_width=800, map_height=600, horizontal_coordinates=0, vertical_coordinates=0, scale=300,
                       octaves=5, persistence=0.55, lacunarity=3.2, seed=0):  # gradient_map

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
    # gradient = create_round_gradient(map_width, map_height)
    game_map = np.empty((map_width, map_height) + (3,), dtype=np.uint8)  # creates an "empty" map
    threshold = 0.5
    for i in range(map_width):
        for j in range(map_height):
            val = (pnoise2((i + vertical_coordinates) / scale, (j + horizontal_coordinates) / scale, octaves=octaves,
                           persistence=persistence, lacunarity=lacunarity,
                           base=seed) + threshold)  # * gradient_map[i][j]
            if val < -0.2 + threshold:
                game_map[i][j] = colors["dark_blue"]
            elif val < -0.075 + threshold:
                game_map[i][j] = colors["blue"]
            elif val < 0.0 + threshold:
                game_map[i][j] = colors["medium_blue"]
            elif val < 0.05 + threshold:
                game_map[i][j] = colors["light_blue"]
            # if val < 0.05:
            #     map[i][j] = (0, 0, 100 + abs(300 * val))
            elif val < 0.07 + threshold:
                game_map[i][j] = colors["light_sand"]
            elif val < 0.085 + threshold:
                game_map[i][j] = colors["sand"]
            elif val < 0.095 + threshold:
                game_map[i][j] = colors["dark_sand"]
            elif val < 0.16 + threshold:
                game_map[i][j] = colors["darkest_green"]
            elif val < 0.23 + threshold:
                game_map[i][j] = colors["dark_green"]
            elif val < 0.3 + threshold:
                game_map[i][j] = colors["green"]
            elif val < 0.335 + threshold:
                game_map[i][j] = colors["light_green"]
            elif val < 0.36 + threshold:
                game_map[i][j] = colors["dark_mountain"]
            elif val < 0.38 + threshold:
                game_map[i][j] = colors["mountain"]
            elif val < 0.415 + threshold:
                game_map[i][j] = colors["medium_mountain"]
            elif val < 0.495 + threshold:
                game_map[i][j] = colors["light_mountain"]
            elif val < 1 + threshold:
                game_map[i][j] = colors["snow"]
    return game_map


"""
The following 4 functions allow movement within the terrain
 
Logic: removes a slice of width/height of the matrix and calculates the next slice and stacks them

Complexity: by removing and calculating slices instead of the entire map again this gains a massive performance boost

moving_speed: the size of each slice in pixels
horizontal_offset: the user's horizontal coordinates displacement from the center (0, 0) in pixels
vertical_offset: the user's vertical coordinates displacement from the center (0, 0) in pixels
"""


def move_down(width, height, moving_speed, game_map, horizontal_offset, vertical_offset):
    game_map = game_map[:, moving_speed:]  # slices the part the user moved from
    game_map = np.hstack(
        (game_map, create_colored_map(width, moving_speed, horizontal_coordinates=height + horizontal_offset,
                                      vertical_coordinates=vertical_offset)))
    # calculates the new slice and joins it to the main map
    return game_map


def move_up(width, height, moving_speed, game_map, horizontal_offset, vertical_offset):
    game_map = game_map[:, :height - moving_speed]  # slices the part the user moved from
    game_map = np.hstack(
        (create_colored_map(width, moving_speed, horizontal_coordinates=-moving_speed + horizontal_offset,
                            vertical_coordinates=vertical_offset), game_map))
    # calculates the new slice and joins it to the main map
    return game_map


def move_right(width, height, moving_speed, game_map, horizontal_offset, vertical_offset):
    game_map = game_map[moving_speed:, :]  # slices the part the user moved from
    game_map = np.vstack(
        (game_map, create_colored_map(moving_speed, height, horizontal_coordinates=horizontal_offset,
                                      vertical_coordinates=width + vertical_offset)))
    # calculates the new slice and joins it to the main map
    return game_map


def move_left(width, height, moving_speed, game_map, horizontal_offset, vertical_offset):
    game_map = game_map[:width - moving_speed, :]  # slices the part the user moved from
    game_map = np.vstack((create_colored_map(moving_speed, height, horizontal_coordinates=horizontal_offset,
                                             vertical_coordinates=-moving_speed + vertical_offset), game_map))
    # calculates the new slice and joins it to the main map
    return game_map


def game_loop(width, height, moving_speed, vertical_offset, horizontal_offset):
    """
    Creates a window using the pygame module, then calls the relevant functions in order to make a terrain map and
    allowing movement within the terrain

    width: width resolution in pixels
    height: height resolution in pixels
    moving_speed: moving speed in pixels per moving action
    vertical_offset: variable following the user's vertical coordinates displacement from the center (0, 0)
    horizontal_offset: variable following the user's horizontal coordinates displacement from the center (0, 0)
    """
    game_map = create_colored_map(width, height)  # create_gradient_map(width, height)
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
                    game_map = move_up(width, height, moving_speed, game_map, horizontal_offset, vertical_offset)
                    horizontal_offset -= moving_speed
                if events.key == pygame.K_DOWN:
                    game_map = move_down(width, height, moving_speed, game_map, horizontal_offset, vertical_offset)
                    horizontal_offset += moving_speed
                if events.key == pygame.K_RIGHT:
                    game_map = move_right(width, height, moving_speed, game_map, horizontal_offset, vertical_offset)
                    vertical_offset += moving_speed
                if events.key == pygame.K_LEFT:
                    game_map = move_left(width, height, moving_speed, game_map, horizontal_offset, vertical_offset)
                    vertical_offset -= moving_speed
        pygame.pixelcopy.array_to_surface(display, game_map)
        pygame.display.flip()


def main():
    """
     TODO: Make menu, let user choose seed and options, add world saving option, make tiled?(voronoi diagram),
           add rivers and trails?, biomes?, seasons/day night cycle?, add round gradient, add path finding?,
           add objective?, find usage
    """
    width, height = 800, 600  # resolution in pixels
    moving_speed = 40  # moving speed in pixels per moving action
    vertical_offset = 0  # variable following the user's vertical coordinates displacement from the center (0, 0)
    horizontal_offset = 0  # variable following the user's horizontal coordinates displacement from the center (0, 0)

    game_loop(width, height, moving_speed, vertical_offset, horizontal_offset)


if __name__ == "__main__":
    main()
