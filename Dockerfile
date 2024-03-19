FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy the Streamlit application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port where Streamlit will run
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]
