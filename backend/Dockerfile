# Start with a Python 3.11 base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code and config into the container
COPY ./app /app/app
COPY alembic.ini /app/alembic.ini
COPY content /app/content

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using uvicorn
# --host 0.0.0.0 makes the app accessible from outside the container
# --reload is for development, auto-reloads on code changes
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
