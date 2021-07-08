# Calculate the longitude of a station from its Maidenhead grid

class CalculateLongitude:
    def calculate_longitude(grid):
        value_1 = ord(grid[0]) - 65
        value_1 = value_1 * 20
        value_2 = int(grid[2]) * 2
        value_3 = ord(grid[4]) - 97
        value_3 = value_3 / 12
        value_3 = value_3 + (1/24)
        longitude = value_1 + value_2 + value_3 - 180
        return longitude
