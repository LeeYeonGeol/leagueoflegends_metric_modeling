# Build FastAPI
FROM python:3.11.1

# Set working directory
COPY ./src /src
WORKDIR /src

# Copy and install requirements
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt