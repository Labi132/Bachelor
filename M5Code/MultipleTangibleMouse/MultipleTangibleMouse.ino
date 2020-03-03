#include <M5Stack.h>

void setup()
{
    delay(5000);
    M5.begin(true, true, true);
    M5.Lcd.setBrightness(255);
    M5.Lcd.drawJpgFile(SD, "/1.jpg", 0, 0, 320, 240);
}
