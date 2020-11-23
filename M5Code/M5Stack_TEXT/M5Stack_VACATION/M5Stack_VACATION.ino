#include <M5Stack.h>

void setup()
{
    delay(5000);
    M5.begin(true, true, true);
    M5.Lcd.setBrightness(255);
    M5.Lcd.setTextWrap(true, true);
    M5.Lcd.setTextSize(3);
    M5.Lcd.setTextDatum(MC_DATUM);
    M5.Lcd.drawString("Urlaub/Vacation", 160, 120, 2);
}

void loop(){}
