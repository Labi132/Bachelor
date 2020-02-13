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
    Serial.begin(115200);
    delay(10);
    M5.begin()

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
    
    M5.Lcd.setBrightness(200);
}

String mode[5] = {"highlight", "drag", "group", "pan", "zoom"};
int current_mode = 0;
bool a_pressed;
bool c_pressed;

void set_diplay(){
     M5.Lcd.drawJpgFile(SD, "/p" + (String) current_mode + ".jpg");
}

void loop()
{
    a_pressed = M5.BtnA.read();
    c_pressed = M5.BtnC.read();
    unsigned long button_timeout = millis();
    if (millis()-button_timeout > 1000){
        if (a_pressed == true){
            if(current_mode == 0){
                current_mode == 4;
                //change image to X
            }
            else{
                current_mode-=1;
                //change image to X
            }
        }
        if (c_pressed == true){
            if(current_mode == 4){
                current_mode == 0;
                //change image to X
            }
            else{
                current_mode+=1;
                //change image to X
            }
        }
    }
    
    // delay(5000);

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
    url += mode;

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
}
