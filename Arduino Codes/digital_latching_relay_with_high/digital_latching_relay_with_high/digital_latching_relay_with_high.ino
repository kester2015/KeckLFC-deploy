int RelayPin = 7;
int RelayPin2 = 8;
int inputPin = 0;



int threshold = 317;//83;
int high_threshold = 741; // added for high

int lastV = 0;
int lastV_high = 1024; // added for high

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

    lastV_high = nowV; // Added for high
    
    Serial.print("Now voltage is reset equal to input，and the voltage is:");
    Serial.println(nowV);
  }
  if (containsStr(cmd, "THRESHOLD")) {
    threshold = cmd.substring(9).toInt();
    Serial.print("Threshold is set to ");
    Serial.println(threshold);
  }
  
  // ------Added for high-----
  if (containsStr(cmd, "HIGH")) {
    high_threshold = cmd.substring(9).toInt();
    Serial.print("High Threshold is set to ");
    Serial.println(threshold);
  }
  // ------Added for high FINISHED
  
  if (containsStr(cmd, "GET")) {
    Serial.print("Now voltage is ");
    Serial.println(nowV);
    
    Serial.print("Now voltage to judge (low) is ");
    Serial.println(lastV);
    Serial.print("Now voltage to judge (high) is "); // Added for high
    Serial.println(lastV_high); // Added for high
    
    Serial.print("Low Threshold is ");
    Serial.println(threshold);
    Serial.print("High Threshold is "); // Added for high
    Serial.println(high_threshold); // Added for high
  }
  if (containsStr(cmd, "HELP")) {
    Serial.println("RESET: reset the voltage to input voltage");
    Serial.println("THRESHOLD: set the low threshold voltage");
    Serial.println("HIGH: set the high threshold voltage"); // Added for high
    Serial.println("GET: get the voltage and threshold");
    Serial.println("HELP: get help");
  }
}

void loop() {
  // update voltage only when voltage is decreasing or increasing
  nowV = analogRead(inputPin);
  
  if (nowV < lastV) {
    lastV = nowV; // update record low V
  }
  
  // ------Added for high------
  if (nowV > lastV_high) {
    lastV_high = nowV;
  }
  // ------Added for high FINISHED------

  if (lastV<threshold or lastV_high>high_threshold){ // Added for high, another judge 
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
