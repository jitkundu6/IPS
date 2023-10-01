import serial   # pip install pyserial
import json

# Define the serial port device (e.g., '/dev/ttyUSB0' or '/dev/ttyS0')
serial_port = '/dev/ttyACM0'  # Replace with your device's path
# serial_port = '/dev/ttyACM1'  # Replace with your device's path
baud_rate = 115200  # Set the baud rate to match your device configuration


try:
    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate)
    print(f"Connected to {serial_port} at {baud_rate} baud")
    distance_dict = dict()
    max_count = 10
    distance_offset = -0.20
    distance_correction_factor = 0.95

    while True:
        try:
            # Read a line from the serial port (ending with '\n')
            data = ser.readline().decode('utf-8').strip()
            # print(f"Received: {data}")
            if data:
                # data = data.replace("'",'"')
                # print(f"data: {data}")
                result = json.loads(data)

                if result['quality'] in ['ok']:
                    result['addr'] = result['addr'].replace(" (random)", "")
                    distance = eval(result['mcpd_best'])
                    distance = (round((distance + distance_offset) * distance_correction_factor, 2)) # Rectified

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
                    print(f"distance: {distance}    |   smooth: {smooth_distance}   | Result: {result}")

        except Exception as e:
            print(f"Error: {e}")

except serial.SerialException as e:
    print(f"Error: {e}")

finally:
    # Close the serial port when done
    if ser.is_open:
        ser.close()
