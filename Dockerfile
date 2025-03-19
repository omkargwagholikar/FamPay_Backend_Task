# Use an official Python runtime as a base image
FROM python:3.10.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the project requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Expose the port on which the Django app runs (default: 8000)
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]