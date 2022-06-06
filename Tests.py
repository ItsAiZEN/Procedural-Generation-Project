import numpy as np
import math

def create_gradient_map(map_width=800, map_height=600):
    gradient_map = np.zeros((map_width, map_height))
    for i in range(map_width):
        for j in range(map_height):
            gradient_map[i][j] = (
                abs(1 - abs(math.dist((map_width // 2, map_height // 2), (i, j))) / (max(map_width, map_height) / 2)))**2
        # gradient_map[i][j] = # TODO: create circular\ square gradient between 0 to 1
        # calculate distance from center and divide by half the width\length and inverse the results
    return gradient_map


print(create_gradient_map(7, 5))
