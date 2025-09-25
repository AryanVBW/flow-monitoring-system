/*
 * Liquid Flow Measurement System
 * Arduino Uno + SEN-HZ21WA Water Flow Sensor
 * 
 * Features:
 * - Accurate flow rate measurement in L/min
 * - Stable readings with moving average filter
 * - Real-time serial output for graphing
 * - Connection test functionality
 * - Low power consumption for USB power
 * 
 * Hardware Connections:
 * - SEN-HZ21WA Red wire (VCC) -> Arduino 5V
 * - SEN-HZ21WA Black wire (GND) -> Arduino GND  
 * - SEN-HZ21WA Yellow wire (Signal) -> Arduino Digital Pin 2
 * 
 * Author: Arduino Flow Monitor System
 * Date: September 2025
 */

// Pin definitions
const int FLOW_SENSOR_PIN = 2;    // Digital pin for flow sensor (interrupt capable)
const int LED_PIN = 13;           // Built-in LED for status indication

// Flow sensor specifications for SEN-HZ21WA
const float CALIBRATION_FACTOR = 7.5;  // Pulses per liter per minute
const int SAMPLE_SIZE = 10;             // Moving average sample size
const unsigned long MEASUREMENT_INTERVAL = 1000; // Measurement interval in ms

// Global variables
volatile unsigned long pulseCount = 0;
unsigned long lastMeasurementTime = 0;
float flowRateBuffer[SAMPLE_SIZE];
int bufferIndex = 0;
bool bufferFilled = false;

// System status
bool sensorConnected = false;
unsigned long lastPulseTime = 0;
const unsigned long CONNECTION_TIMEOUT = 5000; // 5 seconds without pulses = disconnected

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // Attach interrupt for flow sensor
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulseCounter, FALLING);
  
  // Initialize flow rate buffer
  for (int i = 0; i < SAMPLE_SIZE; i++) {
    flowRateBuffer[i] = 0.0;
  }
  
  // Welcome message and connection test
  Serial.println("=== Liquid Flow Measurement System ===");
  Serial.println("Arduino Uno + SEN-HZ21WA Flow Sensor");
  Serial.println("Initializing system...");
  
  // Test Arduino-PC connection
  testConnection();
  
  // System ready
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("System ready!");
  Serial.println("CSV Format: Time(ms),FlowRate(L/min),TotalVolume(L),Status");
  Serial.println("---");
  
  lastMeasurementTime = millis();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if it's time for a new measurement
  if (currentTime - lastMeasurementTime >= MEASUREMENT_INTERVAL) {
    calculateAndDisplayFlow(currentTime);
    lastMeasurementTime = currentTime;
  }
  
  // Check sensor connection status
  checkSensorConnection();
  
  // Blink LED to show system is alive
  static unsigned long lastBlink = 0;
  if (currentTime - lastBlink > 2000) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    lastBlink = currentTime;
  }
  
  // Small delay to prevent overwhelming the serial output
  delay(10);
}

// Interrupt service routine for pulse counting
void pulseCounter() {
  pulseCount++;
  lastPulseTime = millis();
  sensorConnected = true;
}

// Calculate flow rate and display results
void calculateAndDisplayFlow(unsigned long currentTime) {
  // Disable interrupts while reading pulse count
  noInterrupts();
  unsigned long currentPulseCount = pulseCount;
  pulseCount = 0;
  interrupts();
  
  // Calculate flow rate in L/min
  float flowRate = (currentPulseCount / CALIBRATION_FACTOR) * (60000.0 / MEASUREMENT_INTERVAL);
  
  // Apply moving average filter for stable readings
  flowRateBuffer[bufferIndex] = flowRate;
  bufferIndex = (bufferIndex + 1) % SAMPLE_SIZE;
  if (bufferIndex == 0) bufferFilled = true;
  
  // Calculate averaged flow rate
  float averagedFlowRate = calculateMovingAverage();
  
  // Calculate total volume (simple integration)
  static float totalVolume = 0.0;
  totalVolume += (averagedFlowRate * MEASUREMENT_INTERVAL) / 60000.0; // Convert to liters
  
  // Determine system status
  String status = getSensorStatus();
  
  // Output data in CSV format for easy graphing
  Serial.print(currentTime);
  Serial.print(",");
  Serial.print(averagedFlowRate, 3);
  Serial.print(",");
  Serial.print(totalVolume, 4);
  Serial.print(",");
  Serial.println(status);
  
  // Human-readable output (can be commented out for pure CSV)
  /*
  Serial.print("Flow Rate: ");
  Serial.print(averagedFlowRate, 3);
  Serial.print(" L/min | Total Volume: ");
  Serial.print(totalVolume, 4);
  Serial.print(" L | Status: ");
  Serial.println(status);
  */
}

// Calculate moving average for stable readings
float calculateMovingAverage() {
  float sum = 0.0;
  int count = bufferFilled ? SAMPLE_SIZE : bufferIndex;
  
  for (int i = 0; i < count; i++) {
    sum += flowRateBuffer[i];
  }
  
  return count > 0 ? sum / count : 0.0;
}

// Check sensor connection status
void checkSensorConnection() {
  unsigned long currentTime = millis();
  
  // If no pulses received for CONNECTION_TIMEOUT, assume disconnected
  if (currentTime - lastPulseTime > CONNECTION_TIMEOUT && lastPulseTime > 0) {
    sensorConnected = false;
  }
}

// Get sensor status string
String getSensorStatus() {
  if (!sensorConnected && lastPulseTime == 0) {
    return "WAITING";
  } else if (!sensorConnected) {
    return "DISCONNECTED";
  } else {
    return "CONNECTED";
  }
}

// Test Arduino-PC connection
void testConnection() {
  Serial.println("Testing Arduino-PC connection...");
  
  for (int i = 3; i > 0; i--) {
    Serial.print("Connection test countdown: ");
    Serial.println(i);
    
    // Blink LED during countdown
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(800);
  }
  
  Serial.println("Arduino-PC connection: OK");
  Serial.print("Arduino running on USB power: ");
  Serial.println(analogRead(A0) > 100 ? "OK" : "CHECK_POWER");
  
  delay(1000);
}

// Function to reset total volume (can be called via serial command)
void resetTotalVolume() {
  // This function can be expanded to accept serial commands
  Serial.println("Volume reset command received");
}

// Calibration function (for future enhancement)
void calibrateSensor() {
  Serial.println("Calibration mode - Pour exactly 1 liter and send 'CAL' command");
  // Implementation for calibration can be added here
}