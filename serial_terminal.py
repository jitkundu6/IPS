import serial   # pip install pyserial

# Define the serial port device (e.g., '/dev/ttyUSB0' or '/dev/ttyS0')
serial_port = '/dev/ttyACM0'  # Replace with your device's path
# serial_port = '/dev/ttyACM1'  # Replace with your device's path
# serial_port = '/dev/ttyACM2'  # Replace with your device's path
baud_rate = 115200  # Set the baud rate to match your device configuration


def serial_data_update(serial_port, baud_rate):
    try:
        # Open the serial port
        ser = serial.Serial(serial_port, baud_rate)
        print(f"Connected to {serial_port} at {baud_rate} baud")

        while True:
            try:
                # Read a line from the serial port (ending with '\n')
                data = ser.readline().decode('utf-8').strip()
                print(f"Received: {data}")
            except Exception as e:
                print(f"Error: {e}")

    except serial.SerialException as e:
        print(f"Error: {e}")

    finally:
        # Close the serial port when done
        if ser.is_open:
            ser.close()

serial_data_update(serial_port, baud_rate)