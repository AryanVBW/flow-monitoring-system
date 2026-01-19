/*
 * Simple Liquid Flow Monitor - Fixed Version
 * Arduino Uno + SEN-HZ21WA Water Flow Sensor
 * 
 * This version removes the problematic testConnection loop
 * and starts flow monitoring immediately.
 */

// Pin definitions
const int FLOW_SENSOR_PIN = 2;    // Digital pin for flow sensor (interrupt capable)
const int LED_PIN = 13;           // Built-in LED for status indication

// Flow sensor specifications for SEN-HZ21WA
const float CALIBRATION_FACTOR = 7.5; // 7.5 Hz per L/min
const int SAMPLE_SIZE = 3;             // Buffer size for moving average
const unsigned long MEASUREMENT_INTERVAL = 1000; // 1 second intervals

// Global variables
volatile unsigned long pulseCount = 0;
volatile unsigned long lastPulseMillis = 0;
unsigned long lastMeasurementTime = 0;
float flowRateBuffer[SAMPLE_SIZE];
int bufferIndex = 0;
bool bufferFilled = false;
const unsigned long DEBOUNCE_TIME = 5; // 5ms debounce

// Additional variables
volatile bool newPulseDetected = false;
unsigned long totalPulseCount = 0;
bool sensorConnected = false;
unsigned long lastPulseTime = 0;
const unsigned long CONNECTION_TIMEOUT = 5000;

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
  
  // Simple startup message - NO LOOPS!
  Serial.println("=== Liquid Flow Monitor - Ready ===");
  Serial.println("CSV Format: Time(ms),FlowRate(L/min),TotalVolume(L),Status,CurrentPulses,TotalPulses");
  Serial.flush();
  
  // Quick LED blink to show ready
  digitalWrite(LED_PIN, HIGH);
  delay(200);
  digitalWrite(LED_PIN, LOW);
  
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
  
  // Blink LED to show system is alive (only if no pulse activity)
  static unsigned long lastBlink = 0;
  if (currentTime - lastBlink > 3000 && !newPulseDetected) {
    if (currentTime - lastPulseTime > 2000) { // Only blink if no recent pulses
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
    }
    lastBlink = currentTime;
  }
  
  // Small delay to prevent overwhelming the serial output
  delay(10);
}

// Interrupt service routine for pulse counting
void pulseCounter() {
  unsigned long currentMillis = millis();
  
  // Debounce: ignore pulses that come too quickly
  if (currentMillis - lastPulseMillis >= DEBOUNCE_TIME) {
    pulseCount++;
    totalPulseCount++;
    lastPulseTime = currentMillis;
    lastPulseMillis = currentMillis;
    sensorConnected = true;
    newPulseDetected = true;
    
    // Blink LED briefly to show pulse detected
    digitalWrite(LED_PIN, HIGH);
  }
}

// Calculate flow rate and display results
void calculateAndDisplayFlow(unsigned long currentTime) {
  // Turn off LED from pulse indication
  if (newPulseDetected) {
    delay(50); // Keep LED on briefly
    digitalWrite(LED_PIN, LOW);
    newPulseDetected = false;
  }
  
  // Disable interrupts while reading pulse count
  noInterrupts();
  unsigned long currentPulseCount = pulseCount;
  pulseCount = 0;
  interrupts();
  
  // Calculate flow rate in L/min
  float flowRate = (float(currentPulseCount) * 60.0) / CALIBRATION_FACTOR;
  
  // Apply moving average filter
  flowRateBuffer[bufferIndex] = flowRate;
  bufferIndex = (bufferIndex + 1) % SAMPLE_SIZE;
  if (bufferIndex == 0) bufferFilled = true;
  
  // Calculate averaged flow rate
  float averagedFlowRate = calculateMovingAverage();
  
  // Calculate total volume
  static float totalVolume = 0.0;
  if (averagedFlowRate > 0.001) {
    totalVolume += (averagedFlowRate * MEASUREMENT_INTERVAL) / 60000.0;
  }
  
  // Determine system status
  String status = getSensorStatus();
  
  // Output CSV data
  Serial.print(currentTime);
  Serial.print(",");
  Serial.print(averagedFlowRate, 4);
  Serial.print(",");
  Serial.print(totalVolume, 5);
  Serial.print(",");
  Serial.print(status);
  Serial.print(",");
  Serial.print(currentPulseCount);
  Serial.print(",");
  Serial.println(totalPulseCount);
}

// Calculate moving average
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