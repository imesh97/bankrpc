FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bank.proto .
RUN python -m grpc_tools.protoc \
    --proto_path=. \
    --python_out=. \
    --grpc_python_out=. \
    bank.proto

COPY server.py .
COPY client.py .
COPY client_ui.py .


COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 50051 8501
ENTRYPOINT ["./docker-entrypoint.sh"]