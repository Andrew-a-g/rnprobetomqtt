# A python script to poll reticulum destinations at regular intervals to report signal data to MQTT.
# https://github.com/Andrew-a-g/rnprobetomqtt
# 

import subprocess
import json
import paho.mqtt.client as mqtt
import socket
import re
import time

# MQTT Configuration
MQTT_BROKER = "mqtt_server"
MQTT_PORT = 1883
MQTT_TOPIC = "reticulum/data"
MQTT_USERNAME = "user"
MQTT_PASSWORD = "password"

# Load destinations from a text file
DESTINATIONS_FILE = "rnprobe-destinations"

# Polling interval (in seconds)
POLL_INTERVAL = 3600  # Default: 60 minutes

def parse_rnprobe_output(output):
    """Parse rnprobe output and extract relevant data."""
    data = {
        "source": socket.gethostname(),
        "destination": None,
        "latency": None,
        "hops": None,
        "RSSI": None,
        "SNR": None,
        "link_quality": None,
        "sent": None,
        "received": None,
        "packet_loss": None
    }

    # Parse destination
    dest_match = re.search(r"to <(.*?)>", output)
    if dest_match:
        data["destination"] = dest_match.group(1)

    # Parse latency
    latency_match = re.search(r"Round-trip time is ([\d\.]+) seconds", output)
    if latency_match:
        data["latency"] = float(latency_match.group(1))

    # Parse hops
    hops_match = re.search(r"over (\d+) hop", output)
    if hops_match:
        data["hops"] = int(hops_match.group(1))

    # Parse RSSI
    rssi_match = re.search(r"\[RSSI (-?\d+) dBm\]", output)
    if rssi_match:
        data["RSSI"] = int(rssi_match.group(1))

    # Parse SNR
    snr_match = re.search(r"\[SNR ([\d\.]+) dB\]", output)
    if snr_match:
        data["SNR"] = float(snr_match.group(1))

    # Parse link quality
    link_quality_match = re.search(r"\[Link Quality ([\d\.]+)%\]", output)
    if link_quality_match:
        data["link_quality"] = float(link_quality_match.group(1))

    # Parse sent, received, and packet loss
    sent_match = re.search(r"Sent (\d+), received (\d+), packet loss ([\d\.]+)%", output)
    if sent_match:
        data["sent"] = int(sent_match.group(1))
        data["received"] = int(sent_match.group(2))
        data["packet_loss"] = float(sent_match.group(3))

    return data

def run_rnprobe(destination):
    """Run rnprobe against a destination and return the output."""
    try:
        result = subprocess.run(["rnprobe", "rnstransport.probe", destination], capture_output=True, text=True, check=True)
        print(f"Raw rnprobe output for {destination}:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running rnprobe for {destination}: {e.stderr}")
        return None

def connect_mqtt():
    """Connect to the MQTT broker and handle errors."""
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        return client
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        return None

def main():
    while True:
        client = connect_mqtt()

        if client is None:
            print("Retrying MQTT connection in 10 seconds...")
            time.sleep(10)
            continue

        # Load destinations
        with open(DESTINATIONS_FILE, "r") as file:
            destinations = [line.strip() for line in file if line.strip()]

        for destination in destinations:
            print(f"Probing {destination}...")
            output = run_rnprobe(destination)
            if output:
                data = parse_rnprobe_output(output)
                print(f"Publishing data: {data}")
                try:
                    client.publish(MQTT_TOPIC, json.dumps(data))
                except Exception as e:
                    print(f"Error publishing to MQTT: {e}")

        print(f"Waiting {POLL_INTERVAL} seconds before next poll...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
