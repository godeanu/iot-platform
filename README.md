# IoT Data Collection and Visualization Platform

## Overview

This project implements an **IoT data collection and visualization platform** using a **microservices architecture**. The system enables collecting, storing, and visualizing numerical data from multiple IoT stations deployed in different locations. These stations transmit sensor data via **MQTT**, which is then ingested, processed, and stored in a **time-series database** for visualization. The platform is built with **Docker Swarm** to ensure scalability, maintainability, and ease of deployment across multiple environments.

## Architecture

The platform follows a modular **microservices-based architecture**, consisting of the following core components:

- **MQTT Broker (Mosquitto)**: Manages message publishing and subscription for IoT devices.
- **Data Generator**: Simulates IoT stations sending real-time sensor data.
- **Data Adaptor**: Subscribes to all MQTT topics, parses received messages, and inserts relevant numerical values into the database.
- **InfluxDB**: Stores IoT data as time-series metrics for efficient retrieval and analysis.
- **Grafana**: Provides interactive dashboards for visualizing stored IoT data.
- **Docker Swarm**: Manages the containerized services and enables seamless deployment.

### Communication & Networking

The platform uses **Docker overlay networks** to manage communication between containers efficiently:

- `mqtt_net`: Connects the MQTT broker with the data generator and adaptor.
- `db_net`: Isolates the database and ensures only the adaptor and visualization layer have access.
- `viz_net`: Connects Grafana to InfluxDB for querying and dashboard visualization.

### Prerequisites

Before running the platform, ensure you create a `.env` file with the necessary environment variables. You can use the provided `.env.example` as a reference:

```bash
cp .env.example .env
```

### Running the Platform

1. Clone this repository:
   ```bash
   git clone https://github.com/godeanu/iot-platform.git
   cd iot-platform
   ```
2. Initialize Docker Swarm (if not already set up):
   ```bash
   docker swarm init
   ```
3. Deploy the system using Docker Swarm:
   ```bash
   ./run.sh
   ```
4. Verify running services:
   ```bash
   docker stack ps scd3
   ```
5. Access **Grafana** via `http://localhost:80/`
   - Default credentials:
     - **Username:** `asistent`
     - **Password:** `grafanaSCD2024`

## Data Flow

The Grafana dashboards are structured to provide clear insights into different aspects of the IoT data. The **UPB IoT Data Dashboard** visualizes station-specific metrics grouped by location, allowing users to analyze environmental conditions in real-time. The **Battery Monitoring Dashboard** aggregates battery levels across multiple devices, offering a historical and real-time view of energy consumption trends. The **Environmental Metrics Dashboard** provides trends for various sensor readings, helping in predictive analysis and anomaly detection.

1. IoT stations, located in different physical locations, publish real-time sensor data to the **MQTT broker**.
2. The **Data Adaptor** subscribes to all MQTT topics, extracts numerical values, and writes them to **InfluxDB**.
3. **Grafana** queries InfluxDB to generate real-time dashboards displaying:
   - **UPB IoT Data Dashboard**: Aggregates IoT station metrics per location.
   - **Battery Monitoring Dashboard**: Tracks battery statistics across multiple devices.
   - **Environmental Metrics Dashboard**: Provides real-time trends of collected environmental data.


## Example MQTT Payloads

These payloads represent sensor data from various IoT stations and are published to the MQTT broker. The **Data Adaptor** processes these messages, extracts relevant numerical values, and stores them in **InfluxDB**. The stored data is then visualized using **Grafana dashboards**, providing insights into environmental conditions, battery levels, and other critical metrics.

Example 1:

```json
{
  "BAT": 99,
  "HUMID": 40,
  "TMP": 25.3,
  "timestamp": "2024-11-26T03:54:20+03:00"
}
```

Example 2:

```json
{
  "Alarm": 0,
  "RSSI": 1500,
  "AQI": 12
}
```

## Debugging & Logs

To monitor logs for debugging:

```bash
docker service logs scd3_adaptor --follow
```

Enable verbose logging by setting:

```bash
export DEBUG_DATA_FLOW=true
```