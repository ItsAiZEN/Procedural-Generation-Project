import numpy as np
import math


def create_round_gradient(map_width=800, map_height=600):
    """
    Creates a 2D matrix with float values between 0 and 1 in a round shape (1 in the center and then lowering)

    Logic: calculating the distance from the center and inverting them
    """
    center_to_edge = (math.sqrt(map_width ** 2 + map_height ** 2) // 2)  # utilized triangle geometry, the median on
    # the hypotenuse of a right triangle divides the triangle into two isosceles triangles, because the median equals
    # one half the hypotenuse
    gradient_map = np.zeros((map_width, map_height))
    map_center = (map_width // 2, map_height // 2)
    for i in range(map_width):
        for j in range(map_height):
            gradient_map[i][j] = abs(1 - (math.dist(map_center, (i, j)) / center_to_edge)) ** 1.5

    return gradient_map


print(create_round_gradient(5, 6))
