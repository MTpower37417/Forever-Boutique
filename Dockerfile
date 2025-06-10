# Use Python 3.11 as Base Image
FROM python:3.11

# Set Timezone to UTC
ENV TZ=UTC

# Set Environment Variables
ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV STORE_NAME=${STORE_NAME}
ENV STORE_LOCATION=${STORE_LOCATION}
ENV STORE_PHONE=${STORE_PHONE}
ENV STORE_EMAIL=${STORE_EMAIL}
ENV STORE_WEBSITE=${STORE_WEBSITE}

# Set Working Directory
WORKDIR /app

# Copy Project Files
COPY . .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create Required Directories
RUN mkdir -p data logs customer_data

# Set Permissions
RUN chmod -R 755 /app

# Run Bot
CMD ["python", "demo_app.py"] 