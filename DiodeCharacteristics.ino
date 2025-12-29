#define DRIVE 3       // PWM output
#define VD A0         // Node A
#define VC A1         // Node B

const float Vref = 5.0;
const float Rshunt = 47.0;   // increased for better ADC resolution
const int SAMPLES = 200;

int currentDrive = 0;

void setup(){
  Serial.begin(9600);
  delay(10000);
  pinMode(DRIVE, OUTPUT);
  Serial.println("Vled(V),Current(mA)");
}

int readAvg(int pin){
  long sum = 0;
  for(int i=0;i<SAMPLES;i++){
    sum += analogRead(pin);
    delay(2);
  }
  return sum / SAMPLES;
}

void loop(){
  currentDrive++;
  if(currentDrive > 255){
    currentDrive = 0;
    delay(1000);
  }

  analogWrite(DRIVE, currentDrive);
  delay(100);  // allow capacitor to settle

  int rawVd = readAvg(VD);
  int rawVc = readAvg(VC);

  float Vd = rawVd * (Vref / 1023.0);
  float Vc = rawVc * (Vref / 1023.0);

  float Vled = Vd - Vc;                  // LED forward voltage
  float current_mA = (Vc / Rshunt) * 1000.0;

  Serial.print(Vled, 3); Serial.print(",");
  Serial.println(current_mA, 3);
}
