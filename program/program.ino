#define BUTTON_PIN 5
#define ACTIVE_STATE HIGH
#define FILTER_LIMIT 10
#define LOOP_PAUSE 10
#define MSG_PRESS "PUSH"

// the setup routine runs once when you press reset:
void setup() {
  Serial.begin(9600);
  pinMode(BUTTON_PIN, INPUT);
}

// the loop routine runs over and over again forever:
void loop() {
  static int filter_sum = 0;
  static int state = 0;

  switch (state) {
  case 0: // button release .. wait press
    if (digitalRead(BUTTON_PIN)==ACTIVE_STATE) {
      filter_sum++;
      if (filter_sum>=FILTER_LIMIT) {
        Serial.println(MSG_PRESS);
        filter_sum=0;
        state++;
      }
    }
    else filter_sum=0;
    break;
  case 1: // button pressed .. wait release
    if (digitalRead(BUTTON_PIN)!=ACTIVE_STATE) {
      filter_sum++;
      if (filter_sum>=FILTER_LIMIT) {
        filter_sum=0;
        state--;
      }
    }
    else filter_sum=0;
    break;
  }

  delay(LOOP_PAUSE);
}
