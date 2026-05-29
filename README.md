# Docker Dice Casino - Complete Docker Learning Guide

A fun dice game that teaches you everything about Docker! Play, learn, and master containerization.

## 🎯 What is Docker?

**Docker** is like a magical shipping container for your software. Just like how shipping containers standardize how goods are transported worldwide, Docker standardizes how software is packaged and run anywhere.

## 📦 Core Concepts Explained

### 1. **Docker Image** - The Blueprint
**What it is**: A lightweight, standalone, executable package that includes everything needed to run software: code, runtime, system tools, libraries, settings.

**Think of it as**: A cake recipe or a frozen pizza


**Image Tags**: Labels that identify different versions of an image
```bash
python:3.9-slim     # Tag format: name:version-variant
python:3.9          # Specific version
python:latest       # Most recent version
python:3.9-alpine   # Smaller size version

# Tags help you choose:
# - Which version (3.9, 3.10, 3.11)
# - Which size (slim, alpine, bullseye)
# - Which features (full vs minimal)
```

### 2. **Docker Container** - The Running Instance
**What it is**: A running instance of an image. It's like a virtual computer for your app.


**Key properties**:
- Isolated from other containers
- Has its own filesystem, network, processes
- Can be started, stopped, moved, deleted


### Image Commands:
```bash
# List images on your computer
docker images

# Build an image with a tag
docker build -t myapp:1.0 .

# Download an image without running
docker pull python:3.9

# Remove an image
docker rmi myapp:1.0

# See image layers
docker history myapp:latest
```

### Container Commands:
```bash
# Run container (create + start)
docker run -d --name mycontainer myapp

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop container
docker stop mycontainer

# Start stopped container
docker start mycontainer

# Remove container
docker rm mycontainer

# Execute command inside running container
docker exec -it mycontainer bash

# View container logs
docker logs mycontainer
```

### Docker Compose (Multiple Containers):
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (delete data)
docker compose down -v

# View logs from all services
docker compose logs -f

# Scale a service to 5 instances
docker compose up -d --scale dice-casino=5
```


# Clean up unused resources
docker system prune -a
docker volume prune
```
