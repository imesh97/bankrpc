#!/bin/bash

# Start gRPC server
python server.py &

# Start Streamlit web interface
streamlit run client_ui.py --server.port 8501 --server.address 0.0.0.0