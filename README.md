# PyBalance: Layer-7 Load Balancer

A lightweight, multi-threaded reverse proxy and load balancer written in Python.

## Features
- **Round-Robin Scheduling:** Distributes incoming HTTP traffic evenly across backend nodes.
- **Concurrency:** Uses `threading` and `select` to handle multiple client connections simultaneously.
- **Zero Dependencies:** Built entirely with the standard Python library (`socket`, `threading`).

## How it works
The Load Balancer listens on a public port (e.g., 8080). When a client connects:
1. It selects a backend server from the pool using the Round-Robin algorithm.
2. It establishes a socket connection to the backend.
3. It bridges the data stream between the client and the backend in real-time.