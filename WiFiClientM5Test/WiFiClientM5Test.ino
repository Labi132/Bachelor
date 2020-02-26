#include <WiFi.h>
#include <M5Stack.h>

const char* ssid     = "WIN-GCII0CKRUO7 0159";
const char* password = "Q5-9k195";

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
    M5.Lcd.drawJpgFile(SD, "/drag.jpg", 0, 0, 320, 240);
}

String mode[5] = {"HIGHLIGHT", "DRAG", "GROUP", "PAN", "ZOOM"};
int current_mode = 1;
bool mode_changed = false;

void loop()
{
        M5.BtnA.read();
        M5.BtnC.read();

        //Serial.println(M5.BtnA.read());
        if (M5.BtnA.wasReleased()){
            if(current_mode == 0){
                current_mode = 4;
                mode_changed = true;
            }
            else{
                current_mode-=1;
                mode_changed = true;
            }
        }
        if (M5.BtnC.wasReleased()){
            if(current_mode == 4){
                current_mode = 0;
                mode_changed = true;
            }
            else{
                current_mode+=1;
                mode_changed = true;
            }
        }
        


    // Use WiFiClient class to create TCP connections
    WiFiClient client;
    const int httpPort = 3030;
    if (!client.connect(host, httpPort)) {
        Serial.println("connection failed");
        return;
    }

    if (mode_changed == true){

            switch(current_mode){
          case 0: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/highlight.jpg", 0, 0, 320, 240); break;
          case 1: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/drag.jpg", 0, 0, 320, 240); break;
          case 2: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/group.jpg", 0, 0, 320, 240); break;
          case 3: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/pan.jpg", 0, 0, 320, 240); break;
          case 4: M5.Lcd.clear(); M5.Lcd.drawJpgFile(SD, "/zoom.jpg", 0, 0, 320, 240); break;
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
    }    
}
