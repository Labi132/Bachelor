/*
 *  This sketch sends data via HTTP GET requests to data.sparkfun.com service.
 *
 *  You need to get streamId and privateKey at data.sparkfun.com and paste them
 *  below. Or just customize this script to talk to other HTTP servers.
 *
 */

#include <WiFi.h>
#include <M5Stack.h>

const char* ssid     = "KDG-13ED3";
const char* password = "tYhm3XCQPwQV";

const char* host = "192.168.0.92";

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

    /*WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    */
    
    M5.Lcd.setBrightness(255);
}

String mode[5] = {"drag", "highlight", "group", "pan", "zoom"};
int current_mode = 0;

void loop()
{
        M5.BtnA.read();
        M5.BtnC.read();

        //Serial.println(M5.BtnA.read());
        if (M5.BtnA.wasReleased()){
            if(current_mode == 0){
                current_mode = 4;
            }
            else{
                current_mode-=1;
            }
        }
        if (M5.BtnC.wasReleased()){
            if(current_mode == 4){
                current_mode = 0;
            }
            else{
                current_mode+=1;
            }
        }
        
        switch(current_mode){
          case 0: M5.Lcd.drawJpgFile(SD, "/drag.jpg", 0, 0, 320, 240); break;
          case 1: M5.Lcd.drawJpgFile(SD, "/highlight.jpg", 0, 0, 320, 240); break;
          case 2: M5.Lcd.drawJpgFile(SD, "/group.jpg", 0, 0, 320, 240); break;
          case 3: M5.Lcd.drawJpgFile(SD, "/pan.jpg", 0, 0, 320, 240); break;
          case 4: M5.Lcd.drawJpgFile(SD, "/zoom.jpg", 0, 0, 320, 240); break;
          default: break;
        }

    /*
    Serial.print("connecting to ");
    Serial.println(host);

    // Use WiFiClient class to create TCP connections
    WiFiClient client;
    const int httpPort = 8080;
    if (!client.connect(host, httpPort)) {
        Serial.println("connection failed");
        return;
    }

    // We now create a URI for the request
    String url = "/log/";
    url += mode[current_mode];

    Serial.print("Requesting URL: ");
    Serial.println(url);

    // This will send the request to the server
    client.print(String("GET ") + url + " HTTP/1.1\r\n" +
                 "Host: " + host + "\r\n" +
                 "Connection: close\r\n\r\n");
    unsigned long timeout = millis();
    while (client.available() == 0) {
        if (millis() - timeout > 5000) {
            Serial.println(">>> Client Timeout !");
            client.stop();
            return;
        }
    }

    // Read all the lines of the reply from server and print them to Serial
    while(client.available()) {
        String line = client.readStringUntil('\r');
        Serial.print(line);
    }
    Serial.println();
    Serial.println("closing connection");
    */
}
