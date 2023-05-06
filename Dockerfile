FROM python:3.11.1

# Set working directory
COPY ./src /src
WORKDIR /src

# Copy and install requirements
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

EXPOSE 8000

# Copy the application code
#COPY ./fastapi /code/fastapi

# Set the command to start the application
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]