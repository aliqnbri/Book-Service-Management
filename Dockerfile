# Use the official Python image as a base
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that the application will use
EXPOSE 8000

# Set environment variables for the database
ENV DATABASE_URL=postgres://myuser:mypassword@db:5432/mydb

# Run the command to start the application
CMD ["python", "app.py"]