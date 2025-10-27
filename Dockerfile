# Example Dockerfile for running the tool in a container

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the tool
COPY idrac_iso_tool.py .

# Make it executable
RUN chmod +x idrac_iso_tool.py

# Set entrypoint
ENTRYPOINT ["python3", "idrac_iso_tool.py"]

# Usage:
# docker build -t idrac-iso-tool .
# docker run --rm idrac-iso-tool -H 10.0.0.25 -u root -p calvin -i http://repo.local/ubuntu.iso --insecure
