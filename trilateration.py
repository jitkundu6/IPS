import math

def trilaterate(anchor1, anchor2, anchor3, distance1, distance2, distance3):
    math_offset = 0.0000001

    # Calculate the differences between anchor points
    delta_x21 = anchor2[0] - anchor1[0] + math_offset
    delta_y21 = anchor2[1] - anchor1[1] + math_offset
    delta_x31 = anchor3[0] - anchor1[0] + math_offset
    delta_y31 = anchor3[1] - anchor1[1] + math_offset

    # Calculate the square of distances
    d1_sq = distance1**2 + math_offset
    d2_sq = distance2**2 + math_offset
    d3_sq = distance3**2 + math_offset

    x1_sq = anchor1[0]**2 + math_offset
    x2_sq = anchor2[0]**2 + math_offset
    x3_sq = anchor3[0]**2 + math_offset
    y1_sq = anchor1[1]**2 + math_offset
    y2_sq = anchor2[1]**2 + math_offset
    y3_sq = anchor3[1]**2 + math_offset

    # Calculate intermediate values
    # A = (d1_sq - d2_sq + delta_x21**2 + delta_y21**2) / 2
    # B = (d1_sq - d3_sq + delta_x31**2 + delta_y31**2) / 2
    A = (d1_sq - d2_sq - x1_sq + x2_sq - y1_sq + y2_sq) / 2
    B = (d1_sq - d3_sq - x1_sq + x3_sq - y1_sq + y3_sq) / 2

    # Calculate the unknown point
    x = (A * delta_y31 - B * delta_y21) / (delta_x21 * delta_y31 - delta_x31 * delta_y21)
    y = (A - delta_x21 * x) / delta_y21

    estimated_point = (x, y)
    return estimated_point

def calc_distance(anchor1, anchor2):
    delta_x21 = anchor2[0] - anchor1[0]
    delta_y21 = anchor2[1] - anchor1[1]

    distance = math.sqrt(delta_x21**2 + delta_y21**2)
    return distance


# Example usage with non-zero coordinates:
anchor1 = (4, 2)
anchor2 = (1, 5)
anchor3 = (1, 2)
distance1 = 3.0
distance2 = 1.5  # Approximate square root of 18
distance3 = 1.5

estimated_point = trilaterate(anchor1, anchor2, anchor3, distance1, distance2, distance3)
print("Estimated Point:", estimated_point)
print(f"d1 = {calc_distance(estimated_point, anchor1)}, {distance1}")
print(f"d2 = {calc_distance(estimated_point, anchor2)}, {distance2}")
print(f"d3 = {calc_distance(estimated_point, anchor3)}, {distance3}")

estimated_point2 = trilaterate(anchor2, anchor1, anchor3, distance2, distance1, distance3)
print("Estimated Point2:", estimated_point2)

estimated_point3 = trilaterate(anchor2, anchor3, anchor1, distance2, distance3, distance1)
print("Estimated Point3:", estimated_point3)

estimated_point4 = trilaterate(anchor1, anchor3, anchor2, distance1, distance3, distance2)
print("Estimated Point3:", estimated_point4)

estimated_point5 = trilaterate(anchor3, anchor1, anchor2, distance3, distance1, distance2)
print("Estimated Point2:", estimated_point5)

estimated_point6 = trilaterate(anchor3, anchor2, anchor1, distance3, distance2, distance1)
print("Estimated Point2:", estimated_point6)
