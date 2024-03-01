
int outputPin = 3;
int inputPin = 3;

int lastV = 0;
int nowV = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(outputPin, OUTPUT);
}

// judge if serial command contains RESET
bool containsReset(String str) {
  if (str.indexOf("RESET") != -1) {
    return true;
  }
  return false;
}

void loop() {
  // put your main code here, to run repeatedly:
  
  // update voltage only when voltage is decreasing or increasing
  nowV = analogRead(inputPin);
  if (nowV > lastV) { // >: update when increase; <: update when decrease
    analogWrite(outputPin, nowV);
    lastV = nowV;
  }

  // Read reset command froom Serial
  if (Serial.available() > 0) {
    String reset = Serial.readStringUntil('\n');
    if (containsReset(reset)) {
      analogWrite(outputPin, 0);
      lastV = nowV;
      Serial.println("Now voltage is reset equal to input.");
    }
  }
}
