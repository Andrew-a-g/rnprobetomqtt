# rnprobetomqtt
A python script to poll endpoints on a reticulum LoRa network and log RSSI, SNR and other stats to MQTT for reporting.

## Requirements
Python
Paho mqtt client...

    `pip3 install paho-mqtt`

## Usage
1. Add your LXMF endpoints to the rnprobe-destinations text file, one on each line.  I recommend adding the PI devices if they are used in the network as they are normally always on - meshchat and nomadnet instances can come and go.  The config of rns on a pi (at ~/.reticulum/config) must include the following line to respond to probe requests...

    `respond_to_probes = yes`

2. Edit the script with yout mqtt server data

   ```MQTT_BROKER = "mqtt_server"
    MQTT_PORT = 1883
    MQTT_TOPIC = "reticulum/data"
    MQTT_USERNAME = "user"
    MQTT_PASSWORD = "password"```

3. Change the interval if required or troubleshooting (be mindful of LoRa traffic when doing this)
    ```POLL_INTERVAL = 3600  # Default: 60 minutes```

## Home Assistant
Example home assistant config to collect the data...
``` 
   - name: "RNS Mark Latency"
        state_topic: "reticulum/data"
        value_template: >
        {% if value_json.destination == "6861c4d3679f21e270705adbcd8d3e3f" %}
            {{ value_json.latency }}
        {% endif %}
        unit_of_measurement: "s"
        unique_id: "mark_rnsd_latency"

    - name: "RNS Mark Hops"
        state_topic: "reticulum/data"
        value_template: >
        {% if value_json.destination == "6861c4d3679f21e270705adbcd8d3e3f" %}
            {{ value_json.hops }}
        {% endif %}
        unit_of_measurement: "hops"
        unique_id: "mark_rnsd_hops"

    - name: "RNS Mark RSSI"
        state_topic: "reticulum/data"
        value_template: >
        {% if value_json.destination == "6861c4d3679f21e270705adbcd8d3e3f" %}
            {{ value_json.RSSI }}
        {% endif %}
        unit_of_measurement: "dBm"
        unique_id: "mark_rnsd_rssi"

    - name: "RNS Mark SNR"
        state_topic: "reticulum/data"
        value_template: >
        {% if value_json.destination == "6861c4d3679f21e270705adbcd8d3e3f" %}
            {{ value_json.SNR }}
        {% endif %}
        unit_of_measurement: "dB"
        unique_id: "mark_rnsd_snr"

    - name: "RNS Mark Link Quality"
        state_topic: "reticulum/data"
        value_template: >
        {% if value_json.destination == "6861c4d3679f21e270705adbcd8d3e3f" %}
            {{ value_json.link_quality }}
        {% endif %}
        unit_of_measurement: "%"
        unique_id: "mark_rnsd_link_quality"

    - name: "RNS Mark Packet Loss"
        state_topic: "reticulum/data"
        value_template: >
        {% if value_json.destination == "6861c4d3679f21e270705adbcd8d3e3f" %}
            {{ value_json.packet_loss }}
        {% endif %}
        unit_of_measurement: "%"
        unique_id: "mark_rnsd_packet_loss"
```