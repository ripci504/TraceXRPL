# TraceXRPL - proof of concept product authentication 

A proof of concept application that allows products to be linked to NFTs on the XRPL, immutably update and record production status, and verify authenticity of products. This is actively being worked on and in extremely early stages.

To view our technical design and a more indepth overview of the project, visit the [White Paper](./docs/whitepaper.md)

## Testing

The Flask webserver uses Celery and Redis for task management. The steps to localy run the project are below.

1. Install Docker on your machine. You can download the desktop version [here](https://www.docker.com/products/docker-desktop).
2. Download the project source code
3. Open a terminal in the root of the project
4. Run `docker compose -f "TraceXRPL\docker-compose.yml" up -d --build` (compose the docker-compose.yml file)
5. The server will be hosted at http://localhost:5000/ or http://127.0.0.1:5000/