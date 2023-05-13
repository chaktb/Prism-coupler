#include <AccelStepper.h>

const int stepsPerRevolution = 3200;
int stepPin = 3;
int dirPin = 2;
long motor_position = 0;
long sensorValue = 0;
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

void setup() {
  Serial.begin(115200);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  stepper.setMaxSpeed(100);
  stepper.setAcceleration(100);
  setMotorToZeroDegrees();
}

void setMotorToZeroDegrees() {
  motor_position = 0;
  stepper.setCurrentPosition(motor_position);
  stepper.runToNewPosition(motor_position);
}

void loop() {
  sensorValue = analogRead(A0);

  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'r') {
      Serial.print("sensor_value=");
      Serial.println(sensorValue);
    } else if (cmd == 'a') {
      motor_position = Serial.parseInt();
      if (Serial.read() == '\n') {
        stepper.runToNewPosition(motor_position);
        delay(100);  // Add a delay to allow the motor to finish moving
        Serial.print("current_position=");
        Serial.println(motor_position);
      }
    } else if (cmd == 'z') {
      setMotorToZeroDegrees();
    }
  }
}
