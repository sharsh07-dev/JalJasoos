# JalJasoos

JalJasoos is a distributed IoT + AI water pipeline monitoring and automation platform for residential societies. 
It uses Edge ML (Physics-Informed Neural Networks) and an offline-first architecture to detect and isolate leaks in real-time.

## Architecture

*   **Edge:** Raspberry Pi running an Edge Gateway, Mosquitto MQTT broker, and local PostgreSQL database. Communicates with ESP32 sensors over MQTT.
*   **Cloud:** FastAPI backend and Next.js frontend, backed by PostgreSQL.
*   **AI:** Physics-Informed Neural Network (PINN) combined with sensor fusion context logic running locally on the Edge Gateway.

## Prerequisites

*   Docker & Docker Compose
*   Node.js 18+ (for frontend development)
*   Python 3.10+ (for API/Edge/Simulator development)

## Getting Started

1.  Copy the environment variables template:
    ```bash
    cp .env.example .env
    ```

2.  Start the core infrastructure (PostgreSQL Cloud, PostgreSQL Edge, and Mosquitto):
    ```bash
    docker compose up -d
    ```

3.  (More setup steps to follow as services are built out)

## Monorepo Structure

*   `apps/api`: Cloud FastAPI Backend
*   `apps/edge-gateway`: Python Raspberry Pi Service
*   `apps/web`: Next.js Dashboard
*   `apps/simulator`: Python mock ESP32 telemetry generator
*   `ml/`: PyTorch models and training logic
*   `packages/`: Shared types and MQTT JSON schemas
*   `infrastructure/`: Docker configuration, Mosquitto config, and database migrations
