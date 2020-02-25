#include <M5Stack.h>

void setup()
{
    delay(5000);
    M5.begin(true, true, true);
    M5.Lcd.setBrightness(255);
    M5.Lcd.clear(BLACK);
    M5.Lcd.setTextSize(2);
    M5.Lcd.drawString("STRING GOES HERE", (int)(M5.Lcd.width()/2), (int)(M5.Lcd.height()/2), 2);
}
