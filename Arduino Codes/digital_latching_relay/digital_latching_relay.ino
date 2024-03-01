int RelayPin = 7;
int RelayPin2 = 8;
int inputPin = 0;


int threshold = 83;
int lastV = 0;
int nowV = 0;


void setup() {
	// Set RelayPin as an output pin
  Serial.begin(9600);
	pinMode(RelayPin, OUTPUT);
  pinMode(RelayPin2, OUTPUT);

}

// judge if serial command contains Str
bool containsStr(String cmd, String str) {
  // Case insensitive
  cmd.toUpperCase();
  str.toUpperCase();
  if (cmd.indexOf(str) != -1) {
    return true;
  }
  return false;
}

void responseSerial(String cmd) {
  if (containsStr(cmd, "RESET")) {
    lastV = nowV;
    Serial.print("Now voltage is reset equal to input，and the voltage is:");
    Serial.println(lastV);
  }
  if (containsStr(cmd, "THRESHOLD")) {
    threshold = cmd.substring(9).toInt();
    Serial.print("Threshold is set to ");
    Serial.println(threshold);
  }
  if (containsStr(cmd, "GET")) {
    Serial.print("Now voltage is ");
    Serial.println(nowV);
    Serial.print("Now voltage to judge is ");
    Serial.println(lastV);
    Serial.print("Threshold is ");
    Serial.println(threshold);
  }
  if (containsStr(cmd, "HELP")) {
    Serial.println("RESET: reset the voltage to input voltage");
    Serial.println("THRESHOLD: set the threshold voltage");
    Serial.println("GET: get the voltage and threshold");
    Serial.println("HELP: get help");
  }
}

void loop() {
  // update voltage only when voltage is decreasing or increasing
  nowV = analogRead(inputPin);
  
  if (nowV < lastV) {
    lastV = nowV;
  }

  if (lastV<threshold){
    digitalWrite(RelayPin,HIGH);
    digitalWrite(RelayPin2, HIGH);
  }else{
    digitalWrite(RelayPin,LOW);
    digitalWrite(RelayPin2, LOW);
  }

  // Read reset command froom Serial
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    responseSerial(cmd);
  }
}
