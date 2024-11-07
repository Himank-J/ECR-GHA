FROM python:3.8

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Define build arguments
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG S3_BUCKET_NAME
ARG COMMIT_ID

# Set environment variables at runtime
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV S3_BUCKET_NAME=${S3_BUCKET_NAME}
ENV COMMIT_ID=${COMMIT_ID}

# Run the training script
CMD ["python", "main.py"]