"""Configuration settings for the Financial QA Predictor."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AzureOpenAIConfig:
    """Azure OpenAI configuration."""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    def validate(self) -> None:
        """Validate that required configuration is present."""
        required_fields = [
            ("api_key", self.api_key),
            ("endpoint", self.endpoint),
            ("deployment_name", self.deployment_name)
        ]
        
        missing = [name for name, value in required_fields if not value]
        if missing:
            raise ValueError(f"Missing required Azure OpenAI configuration: {missing}")


class AppConfig:
    """Application configuration."""
    
    def __init__(self):
        self.azure_openai = AzureOpenAIConfig()
        
        # Paths
        self.data_dir = "data"
        self.input_dir = os.path.join(self.data_dir, "input")
        self.output_dir = os.path.join(self.data_dir, "output")
        self.logs_dir = "logs"
        
        # Default files
        self.default_input_file = os.path.join(self.input_dir, "processed_train.json")
        self.default_output_file = os.path.join(self.output_dir, "predictions.json")
        
        # AI settings
        self.max_tokens = 1000
        self.temperature = 0.1  # Low temperature for consistent numerical results
        
        # Processing settings
        self.batch_size = 10  # For future batch processing
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        dirs = [self.data_dir, self.input_dir, self.output_dir, self.logs_dir]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)


# Global configuration instance
config = AppConfig()