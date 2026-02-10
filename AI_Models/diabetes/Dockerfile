# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY diabetes_requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r diabetes_requirements.txt

# Copy the API code and model files
COPY diabetes_api.py .
COPY diabetes_xgboost_model.pkl .
COPY diabetes_feature_info.pkl .
COPY diabetes_label_encoders.pkl .

# Expose port 5003
EXPOSE 5003

# Run the API
CMD ["python", "diabetes_api.py"]