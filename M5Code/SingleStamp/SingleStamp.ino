#include <WiFi.h>
#include <M5Stack.h>

const char* ssid     = "sensor.uni-regensburg.de";
const char* password = "iot2019tb";

const char* host = "132.199.132.227";

void setup()
{
    delay(5000);
    Serial.begin(115200);
    delay(10);
    M5.begin(true, true, true);

    // We start by connecting to a WiFi network

    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    
    
    M5.Lcd.setBrightness(255);
<<<<<<< HEAD:M5Code/SingleTangibleMouse/SingleTangibleMouse.ino
    M5.Lcd.drawJpgFile(SD, "/drag.jpg", 0, 0, 320, 240);
}

String mode[5] = {"HIGHLIGHT", "DRAG", "GROUP", "PAN", "ZOOM"};
int current_mode = 1;
=======
    M5.Lcd.setTextWrap(true, true);
    M5.Lcd.setTextSize(3);
    M5.Lcd.setTextDatum(MC_DATUM);
    M5.Lcd.drawString("Stadt/City", 160, 120, 2);
}

String mode[6] = {"CITY", "FOOD", "PET", "SCREENSHOT", "VACATION", "ENTER"};
int current_mode = 0;
>>>>>>> SingleTangibleStamp:M5Code/SingleStamp/SingleStamp.ino
bool mode_changed = false;

void loop()
{
        M5.BtnA.read();
        M5.BtnC.read();

        //Serial.println(M5.BtnA.read());
        if (M5.BtnA.wasReleased()){
            if(current_mode == 0){
<<<<<<< HEAD:M5Code/SingleTangibleMouse/SingleTangibleMouse.ino
                current_mode = 4;
=======
                current_mode = 5;
>>>>>>> SingleTangibleStamp:M5Code/SingleStamp/SingleStamp.ino
                mode_changed = true;
            }
            else{
                current_mode-=1;
                mode_changed = true;
            }
        }
        if (M5.BtnC.wasReleased()){
<<<<<<< HEAD:M5Code/SingleTangibleMouse/SingleTangibleMouse.ino
            if(current_mode == 4){
=======
            if(current_mode == 5){
>>>>>>> SingleTangibleStamp:M5Code/SingleStamp/SingleStamp.ino
                current_mode = 0;
                mode_changed = true;
            }
            else{
                current_mode+=1;
                mode_changed = true;
            }
        }
<<<<<<< HEAD:M5Code/SingleTangibleMouse/SingleTangibleMouse.ino
        
=======
>>>>>>> SingleTangibleStamp:M5Code/SingleStamp/SingleStamp.ino


    // Use WiFiClient class to create TCP connections
    WiFiClient client;
    const int httpPort = 3030;
    if (!client.connect(host, httpPort)) {
        Serial.println("connection failed");
        return;
    }

    if (mode_changed == true){

<<<<<<< HEAD:M5Code/SingleTangibleMouse/SingleTangibleMouse.ino
            switch(current_mode){
          case 0: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/highlight.jpg", 0, 0, 320, 240); break;
          case 1: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/drag.jpg", 0, 0, 320, 240); break;
          case 2: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/group.jpg", 0, 0, 320, 240); break;
          case 3: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/pan.jpg", 0, 0, 320, 240); break;
          case 4: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/zoom.jpg", 0, 0, 320, 240); break;
=======
      switch(current_mode){
          case 0: M5.Lcd.clear(); M5.Lcd.drawString("Stadt/City", 160, 120, 2); break;
          case 1: M5.Lcd.clear(); M5.Lcd.drawString("Essen/Food", 160, 120, 2); break;
          case 2: M5.Lcd.clear(); M5.Lcd.drawString("Haustier/Pet", 160, 120, 2); break;
          case 3: M5.Lcd.clear(); M5.Lcd.drawString("Screenshot", 160, 120, 2); break;
          case 4: M5.Lcd.clear(); M5.Lcd.drawString("Urlaub/Vacation", 160, 120, 2); break;
          case 5: M5.Lcd.clear(); M5.Lcd.drawString("Ordner oeffnen", 160, 120, 2); break;
>>>>>>> SingleTangibleStamp:M5Code/SingleStamp/SingleStamp.ino
          default: break;
        }  
          // We now create a URI for the request
    String url = "/log/";
    url += mode[current_mode];
    
    // This will send the request to the server
    client.print(String("GET ") + url + " HTTP/1.1\r\n" +
                 "Host: " + host + "\r\n" +
                 "Connection: close\r\n\r\n");
    mode_changed = false;
<<<<<<< HEAD:M5Code/SingleTangibleMouse/SingleTangibleMouse.ino
=======
    client.stop();             
    /* unsigned long timeout = millis();
    while (client.available() == 0) {
        if (millis() - timeout > 5000) {
            Serial.println(">>> Client Timeout !");
            client.stop();
            return;
         }
       }*/
>>>>>>> SingleTangibleStamp:M5Code/SingleStamp/SingleStamp.ino
    }    
}
