import sys  # Import the sys module for interacting with the interpreter
import serial  # Import the serial module for communicating with the Arduino
import numpy as np  # Import the numpy module for numerical computations
import pyqtgraph as pg  # Import the pyqtgraph module for plotting real-time data
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit  # Import necessary classes from PyQt5 module
# PD signal -> A0 in Aduino
class MotorControlApp(QWidget):
    def __init__(self):
        super().__init__()

        # Define constants for motor control
        self.steps_per_revolution = 3200
        self.n_prism = 1.521
        self.prism_theta_rad = np.radians(45)

        # Set up the user interface
        self.init_ui()

        # Initialize serial connection
        self.ser = serial.Serial('COM3', 115200)  # Change 'COM3' to your Arduino's serial port

        # Initialize data arrays
        self.angle_data = []
        self.sensor_value_data = []

    def init_ui(self):
        # Set up the main window and layout
        self.setWindowTitle('Motor Control')
        self.layout = QVBoxLayout()

         # Create and add labels to the layout
        self.status_label = QLabel('Stopped')
        self.layout.addWidget(self.status_label)

        self.angle_label = QLabel('')
        self.layout.addWidget(self.angle_label)

        self.n_mode_label = QLabel('')
        self.layout.addWidget(self.n_mode_label)

        self.desired_angle_label = QLabel('Desired Angle (degrees):')
        self.desired_angle_input = QLineEdit()

        self.sensor_value_label = QLabel('')
        self.layout.addWidget(self.sensor_value_label)

        # Create and add a layout for the desired angle input field
        self.desired_angle_layout = QHBoxLayout()
        self.desired_angle_layout.addWidget(self.desired_angle_label)
        self.desired_angle_layout.addWidget(self.desired_angle_input)
        self.layout.addLayout(self.desired_angle_layout)

        # Create and add a button to move the motor to the desired angle
        self.move_button = QPushButton('Move to Desired Angle')
        self.move_button.clicked.connect(self.move_motor)
        self.layout.addWidget(self.move_button)

        # Add the plot widget to the layout
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle('Real-time Plot of Angle vs Sensor Value')
        self.plot_widget.setLabel('left', 'Sensor Value')
        self.plot_widget.setLabel('bottom', 'Angle (degrees)')
        self.layout.addWidget(self.plot_widget)


        # Create and add a button to reset the graph
        self.reset_button = QPushButton('Reset Graph')
        self.reset_button.clicked.connect(self.reset_graph)
        self.layout.addWidget(self.reset_button)
        # Set the layout for the main window
        self.setLayout(self.layout)

    def move_motor(self):
        # Set the status label to 'Working'
        self.status_label.setText('Working')
        # Get the desired angle from the input field and calculate the motor position
        desired_angle = float(self.desired_angle_input.text())
        motor_position = int(desired_angle * self.steps_per_revolution / 360)  # Calculate the motor position
        # Clear the plot and plot the initial data
        self.plot_widget.clear()
        self.plot_widget.plot(self.angle_data, self.sensor_value_data)

        # Calculate angle, n_mode, and sensorValue for each step until the motor reaches the desired angle
        sensor_value = 0  # Set an initial value for sensor_value
        for i in range(1, motor_position + 1):
             # Send the command to move the motor and wait for a response with the current position
            self.ser.write(f'a{i}\n'.encode())

            while True:
                response = self.ser.readline().decode().strip()
                if response.startswith('current_position='):
                    updated_position = int(response.split('=')[1])
                    break

            angle = updated_position * 360 / self.steps_per_revolution
            angle_rad = np.radians(angle)
            n_mode = self.n_prism * np.sin(self.prism_theta_rad + np.arcsin(np.sin(angle_rad / self.n_prism)))
            self.angle_label.setText(f'Current Angle: {angle:.3f} degrees')
            self.n_mode_label.setText(f'n_mode: {n_mode:.4f}')
            sensor_value = self.update_sensor_value()

            # Update the data arrays and plot the graph
            self.angle_data.append(angle)
            self.sensor_value_data.append(sensor_value)
            self.plot_widget.plot(self.angle_data, self.sensor_value_data, clear=True)
            # Print the current angle, n_mode, and sensor value to the console
            print(f"{angle:.3f}, {n_mode:.4f}, {sensor_value:.2f}")

        # Update the angle label to reflect the current position of the motor
        updated_position = motor_position
        angle = updated_position * 360 / self.steps_per_revolution
        angle_rad = np.radians(angle)
        n_mode = self.n_prism * np.sin(self.prism_theta_rad + np.arcsin(np.sin(angle_rad / self.n_prism)))
        self.angle_label.setText(f'Current Angle: {angle:.2f} degrees')
        self.status_label.setText('Stopped')
        # Print the current angle, n_mode, and sensor value to the console
        print(f"{angle:.3f}, {n_mode:.4f}, {sensor_value:.2f}")

    def update_sensor_value(self):
         # Send the command to get the sensor value and wait for a response
        self.ser.write(b'r')

        while True:
            response = self.ser.readline().decode().strip()
            if response.startswith('sensor_value='):
                sensor_value = int(response.split('=')[1])
                break
        # Update the sensor value label and return the sensor value
        self.sensor_value_label.setText(f'Sensor Value: {sensor_value}')
        return sensor_value
    
    def reset_graph(self):
        self.angle_data = []
        self.sensor_value_data = []
        self.plot_widget.clear()

if __name__ == '__main__':
    # Create and show the main application window
    app = QApplication(sys.argv)
    motor_control_app = MotorControlApp()
    motor_control_app.show()
    # Start the event loop and exit when the application is closed
    sys.exit(app.exec_())
