# bankRPC — Distributed Banking

A distributed banking application built using gRPC and Python, with Redis for data persistence. This system includes CORE banking operations such as account creation, deposits, withdrawals, and interest calculations, along with data consistency and concurrent transaction handling.

## Demo

- Deployed with Docker and AWS EC2.
- To view the web interface demo, click [here](http://ec2-3-144-116-12.us-east-2.compute.amazonaws.com:8501/).

## Features

- Account creation (savings/checkings)
- Balance retrieval
- Deposit and withdrawal processing
- Interest calculations
- Concurrent transaction handling with Redis
- User-friendly Streamlit web interface
- Robust error handling

## Prerequisites

- Python 3.7+
- Redis server installation required

### Installing Redis

#### Ubuntu/Debian:

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

#### macOS (using Homebrew):

```bash
brew install redis
redis-server
```

#### Windows:

Download and install Redis from [Redis Windows Downloads](https://github.com/microsoftarchive/redis/releases)

## Dependency Installation

Install the Python dependencies:

```bash
pip install grpcio grpcio-tools redis streamlit
```

## System Deployment

### 1. Start Redis Server

Ensure Redis server is running on localhost:6379 (default)

```bash
redis-server
```

### 2. Start gRPC Server

```bash
python server.py
```

The server will start on port 50051.

### 3. Run Client Application

There are two methods to run the client:

#### Option 1: Command Line Client

```bash
python client.py
```

#### Option 2: Web Interface Client (via Streamlit)

```bash
streamlit run client_ui.py
```

The web interface will be accessible at `http://localhost:8501`

## Project Structure

- `bank.proto` - Protocol Buffer definition
- `bank_pb2.py` - Generated Protocol Buffer code
- `bank_pb2_grpc.py` - Generated gRPC code
- `server.py` - gRPC server code
- `client.py` - Command-line client code
- `client_ui.py` - Web interface client code

## Error Handling

- Account not found
- Insufficient funds
- Invalid transaction amounts
- Invalid interest rates
- Concurrent transaction conflicts

## Testing

The basic functionality of the system can be tested using the code found in `client.py`. Run the client script directly to execute the tests:

```bash
python client.py
```

## Reset Database

To clear all data and reset the Redis database:

```bash
redis-cli FLUSHALL
```
