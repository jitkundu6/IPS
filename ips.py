import json
import math
import time
from datetime import datetime
import threading
import serial   # pip install pyserial
from flask import Flask, jsonify    # pip install Flask


# Define the serial port device (e.g., '/dev/ttyUSB0' or '/dev/ttyS0')
serial_port = '/dev/ttyACM0'
# serial_port = '/dev/ttyACM1'
baud_rate = 115200  # Set the baud rate to match your device configuration

anchor1_mac = 'FC:03:15:32:DE:54'
anchor2_mac = "CE:45:7C:90:D3:D5"   # 'DD:F8:63:2F:91:E3'
anchor3_mac = 'FA:25:A4:44:D3:FC'
tag1_mac = 'DD:F8:63:2F:91:E3'

# Coordinate location of the room where anchors are placed
room_location = {
    "A": (-10.5, -12.5),
    "B": (-10.5, 12.5),
    "C": (10.5, 12.5),
    "D": (10.5, -12.5),
}

# Coordinate location of all anchors
# anchors_location = {  # For AC Room
#     anchor1_mac: (1.6, 0),
#     anchor2_mac: (3.3, 1.3),
#     anchor3_mac: (1.8, 3.25),
# }
anchors_location = {    # For Dining Room
    anchor1_mac: (0, 1.3),
    anchor2_mac: (2.45, 2.4),
    # anchor3_mac: (5.3, 1.0),
    anchor3_mac: (4, 0.1),
    # anchor3_mac: (3.3, -3.6),
}

# Parameters for measured distance error correction
distance_offsets = {
    # anchor1_mac:  0, # -0.8,  # 'CE:45:7C:90:D3:D5'
    # anchor2_mac:  0, # -0.4,  # "FC:03:15:32:DE:54"
    # anchor3_mac:  0, # -0.3,     # 'FA:25:A4:44:D3:FC'
    anchor1_mac: -0.8,  # 'CE:45:7C:90:D3:D5'
    anchor2_mac: -0.4,  # "FC:03:15:32:DE:54"
    anchor3_mac: -0.3,  # 'FA:25:A4:44:D3:FC'
}
distance_correction_factors = {
    anchor1_mac: 1.0,  # 'CE:45:7C:90:D3:D5'
    anchor2_mac: 1.0,  # "FC:03:15:32:DE:54"
    anchor3_mac: 1.0,  # 'FA:25:A4:44:D3:FC'
}
max_count = 3

# Calculated/Measured values
anchors_distance = {
    anchor1_mac: 0,
    anchor2_mac: 0,
    anchor3_mac: 0,
}
anchors_back_calc_distance = {
    anchor1_mac: 0,
    anchor2_mac: 0,
    anchor3_mac: 0,
}
anchors_distance_update_time = {
    anchor1_mac: datetime.now(),  # 'CE:45:7C:90:D3:D5'
    anchor2_mac: datetime.now(),  # "FC:03:15:32:DE:54"
    anchor3_mac: datetime.now(),  # 'FA:25:A4:44:D3:FC'
}
tags_location = {
    tag1_mac: [0,0]
}

# Creating Flask app and declaring apis
app = Flask(__name__)

ipAddress = '127.0.0.5'
port = 8000
index_api = '/'
room_api = '/coordinate/room'
anchors_api = '/coordinate/anchors'
tags_api = '/coordinate/tags'


@app.route(index_api, methods=['GET'])
def get_index():
    return jsonify({
        'room': room_location,
        'anchors': anchors_location,
        'tags': tags_location,
        'api': {
            'index': index_api,
            'room': room_api,
            'anchors': anchors_api,
            'tags': tags_api,
        }
    })

@app.route(room_api, methods=['GET'])
def get_room():
    return jsonify(room_location)

@app.route(anchors_api, methods=['GET'])
def get_anchors():
    return jsonify(anchors_location)

@app.route(tags_api, methods=['GET'])
def get_tag():
    return jsonify(tags_location)

# Run Flask app in a separate thread
def run_app_thread():
    t = threading.Thread(target=app.run, kwargs={'debug':False, 'host':ipAddress, 'port':port})
    t.setDaemon(True)
    t.start()
    return t


# Trilateration to using 3 anchor points and respective distance
def trilaterate(anchor1, anchor2, anchor3, distance1, distance2, distance3):
    math_offset = 0.000001

    # print("######### 1<")
    # Calculate the differences between anchor points
    delta_x21 = anchor2[0] - anchor1[0] + math_offset
    delta_y21 = anchor2[1] - anchor1[1] + math_offset
    delta_x31 = anchor3[0] - anchor1[0] + math_offset
    delta_y31 = anchor3[1] - anchor1[1] + math_offset

    # print("######### 2<")
    # Calculate the square of distances
    d1_sq = distance1**2 + math_offset
    d2_sq = distance2**2 + math_offset
    d3_sq = distance3**2 + math_offset

    # print("######### 3<")
    x1_sq = anchor1[0]**2 + math_offset
    x2_sq = anchor2[0]**2 + math_offset
    x3_sq = anchor3[0]**2 + math_offset
    y1_sq = anchor1[1]**2 + math_offset
    y2_sq = anchor2[1]**2 + math_offset
    y3_sq = anchor3[1]**2 + math_offset

    # print("######### 4<")
    # Calculate intermediate constant values
    # A = (d1_sq - d2_sq + delta_x21**2 + delta_y21**2) / 2
    # B = (d1_sq - d3_sq + delta_x31**2 + delta_y31**2) / 2
    A = (d1_sq - d2_sq - x1_sq + x2_sq - y1_sq + y2_sq) / 2
    B = (d1_sq - d3_sq - x1_sq + x3_sq - y1_sq + y3_sq) / 2

    # print("######### 5<")
    # Calculate the unknown point
    x = (A * delta_y31 - B * delta_y21) / ((delta_x21 * delta_y31 - delta_x31 * delta_y21) + math_offset)
    y = (A - delta_x21 * x) / (delta_y21 + math_offset)

    # print("######### 6<")
    estimated_point = (round(x,2), round(y,2))
    return estimated_point


# Calculate distance between 2 coordinate points
def calc_distance(point1, point2):
    delta_x21 = point2[0] - point1[0]
    delta_y21 = point2[1] - point1[1]
    distance = math.sqrt(delta_x21**2 + delta_y21**2)
    # print("point1 : ", point1)
    # print("point2 : ", point2)
    # print("delta_x21 : ", delta_x21)
    # print("delta_x21 : ", delta_x21)
    # print("distance : ", distance)
    return distance


# Calculate tag location based on anchors location and distance from tag
def get_tag_location(_anchors_location, _anchors_distance):
    anchor1 = _anchors_location[anchor1_mac]
    anchor2 = _anchors_location[anchor2_mac]
    anchor3 = _anchors_location[anchor3_mac]
    distance1 = _anchors_distance[anchor1_mac]
    distance2 = _anchors_distance[anchor2_mac]
    distance3 = _anchors_distance[anchor3_mac]
    return trilaterate(anchor1, anchor2, anchor3, distance1, distance2, distance3)


# Back calculate anchors distance based on tag location
def get_back_calc_distance(_tag_location, _anchors_location):
    global anchor1_mac, anchor2_mac, anchor3_mac, anchors_back_calc_distance
    anchor1 = _anchors_location[anchor1_mac]
    anchor2 = _anchors_location[anchor2_mac]
    anchor3 = _anchors_location[anchor3_mac]
    anchors_back_calc_distance[anchor1_mac] = calc_distance(anchor1, _tag_location)
    anchors_back_calc_distance[anchor2_mac] = calc_distance(anchor2, _tag_location)
    anchors_back_calc_distance[anchor3_mac] = calc_distance(anchor3, _tag_location)
    return anchors_back_calc_distance


# Main method to run Indoor Positioning System
def run_ips():
    distance_dict = dict()
    while True:
        try:
            # Open the serial port
            ser = serial.Serial(serial_port, baud_rate)
            print(f"Connected to {serial_port} at {baud_rate} baud")

            while True:
                try:
                    # Read a line from the serial port (ending with '\n')
                    data = ser.readline().decode('utf-8').strip()
                    # print(f"Received: {data}")
                    if data:
                        # data = data.replace("'",'"')
                        # print(f"data: {data}")
                        result = json.loads(data)

                        if result['quality'] in ['ok', 'poor']:
                            current_time = datetime.now()
                            result['addr'] = result['addr'].replace(" (random)", "")
                            distance = eval(result['mcpd_best'])
                            distance = (round((distance + distance_offsets[result['addr']]) * distance_correction_factors[result['addr']], 2)) # Rectified

                            # Distance smoothing
                            device_distance_list = distance_dict.get(result['addr'])
                            if device_distance_list:
                                device_distance_list.append(distance)
                            else:
                                device_distance_list = [distance]

                            if len(device_distance_list) > max_count:
                                device_distance_list = device_distance_list[len(device_distance_list) - max_count : ]
                            distance_dict.update({result['addr']: device_distance_list})

                            smooth_distance = round(sum(device_distance_list) / len(device_distance_list), 2)
                            anchors_distance[result['addr']] = smooth_distance
                            anchors_distance_update_time[result['addr']] = current_time

                            print("\n\n\n######### Received")
                            print(f"distance: {distance}    |   smooth: {smooth_distance}   | Result: {result}")

                            _tag_location = get_tag_location(anchors_location, anchors_distance)
                            print("_tag_loaction: ", _tag_location)
                            print("anchors_location: ", anchors_location)
                            # print(json.dumps(anchors_location))

                            anchors_back_calc_distance = get_back_calc_distance(_tag_location, anchors_location)
                            print("anchors_distance: ", anchors_distance)
                            print("anchors_back_calc_distance: ", anchors_back_calc_distance)
                            print("current_time: ", current_time)
                            print("anchors_distance_update_time: ", anchors_distance_update_time)

                            total_distance_abs_deviation = sum([
                                abs(anchors_back_calc_distance[anchor1_mac] - anchors_distance[anchor1_mac]),
                                abs(anchors_back_calc_distance[anchor2_mac] - anchors_distance[anchor2_mac]),
                                abs(anchors_back_calc_distance[anchor3_mac] - anchors_distance[anchor3_mac])
                            ])
                            total_distance_deviation = abs(sum([
                                (anchors_back_calc_distance[anchor1_mac] - anchors_distance[anchor1_mac]),
                                (anchors_back_calc_distance[anchor2_mac] - anchors_distance[anchor2_mac]),
                                (anchors_back_calc_distance[anchor3_mac] - anchors_distance[anchor3_mac])
                            ]))

                            max_distance_abs_deviation = max([
                                abs(anchors_back_calc_distance[anchor1_mac] - anchors_distance[anchor1_mac]),
                                abs(anchors_back_calc_distance[anchor2_mac] - anchors_distance[anchor2_mac]),
                                abs(anchors_back_calc_distance[anchor3_mac] - anchors_distance[anchor3_mac])
                            ])
                            print("total_distance_deviation: ", total_distance_deviation)
                            print("total_distance_abs_deviation: ", total_distance_abs_deviation)
                            print("max_distance_abs_deviation: ", max_distance_abs_deviation)

                            anchors_distance_update_lag = {
                                anchor1_mac : current_time - anchors_distance_update_time[anchor1_mac],
                                anchor2_mac : current_time - anchors_distance_update_time[anchor2_mac],
                                anchor3_mac : current_time - anchors_distance_update_time[anchor3_mac],
                            }
                            print("anchors_distance_update_lag: ", anchors_distance_update_lag)

                            total_update_time_lag = sum([
                                anchors_distance_update_lag[anchor1_mac].seconds,
                                anchors_distance_update_lag[anchor2_mac].seconds,
                                anchors_distance_update_lag[anchor3_mac].seconds,
                            ])
                            print("total_update_time_lag: ", total_update_time_lag)
                            max_update_time_lag = max([
                                anchors_distance_update_lag[anchor1_mac].seconds,
                                anchors_distance_update_lag[anchor2_mac].seconds,
                                anchors_distance_update_lag[anchor3_mac].seconds,
                            ])
                            print("max_update_time_lag: ", max_update_time_lag)

                            distance_flag = False
                            time_flag = False

                            if max_update_time_lag <= 5:
                                time_flag = True
                                print("(valid time) _tag_loaction: ", _tag_location)

                            if max_distance_abs_deviation <= 8:
                                distance_flag = True
                                print("(valid distance) _tag_loaction: ", _tag_location)

                            if distance_flag and time_flag:
                                tags_location[tag1_mac] = _tag_location

                            print("tags_location: ", tags_location)
                            # print(json.dumps(tags_location))
                            # print(json.dumps(room_location))

                except serial.SerialException as e:
                    print(f"SerialException: {e}")
                    if ser.is_open:
                        ser.close()
                    time.sleep(1)
                    break

                except Exception as e:
                    print(f"Error: {e}")

        except Exception as e:
            print(f"Final Error: {e}")
            time.sleep(2)


if __name__ == "__main__":
    # Run Flask app in a separate thread
    t = run_app_thread()

    # Run Indoor Positioning System
    run_ips()
