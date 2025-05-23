"""Azure OpenAI client management."""

from openai import AzureOpenAI
from typing import Dict, Any, List
from config.settings import config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AzureOpenAIClient:
    """Azure OpenAI client wrapper."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        # Validate configuration
        config.azure_openai.validate()
        
        # Initialize client
        self.client = AzureOpenAI(
            api_key=config.azure_openai.api_key,
            azure_endpoint=config.azure_openai.endpoint,
            api_version=config.azure_openai.api_version
        )
        
        logger.info("Azure OpenAI client initialized successfully")
        logger.info(f"Azure OpenAI Endpoint: {config.azure_openai.endpoint}")
        logger.info(f"Deployment Name: {config.azure_openai.deployment_name}")
        logger.info(f"API Version: {config.azure_openai.api_version}")
    
    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """Create a chat completion using Azure OpenAI.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens for response (uses config default if None)
            temperature: Temperature for response (uses config default if None)
            
        Returns:
            Response content as string
            
        Raises:
            Exception: If API call fails
        """
        try:
            logger.info("Sending request to Azure OpenAI")
            
            response = self.client.chat.completions.create(
                messages=messages,
                max_tokens=max_tokens or config.max_tokens,
                temperature=temperature or config.temperature,
                model=config.azure_openai.deployment_name
            )
            
            logger.info("Received response from Azure OpenAI")
            
            response_text = response.choices[0].message.content.strip()
            logger.debug(f"Raw response: {response_text}")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in Azure OpenAI API call: {e}", exc_info=True)
            raise
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for financial QA.
        
        Returns:
            System prompt string
        """
        return """You are a financial analysis expert specialized in answering questions about financial reports and performing calculations.

Your task is to:
1. Analyze financial report data (text and tables)
2. Answer questions about specific financial metrics
3. Generate both a "program" (calculation steps) and a numerical answer

For the "program" field:
- If the answer is a direct lookup from the data, just return the number (e.g., "206588")
- If calculation is needed, show the operation (e.g., "subtract(206588, 181001)" or "divide(25587, 181001)")
- For multi-step calculations, separate with commas and use #0, #1, etc. to reference previous results
- Common operations: add(), subtract(), multiply(), divide()

For the "answer" field:
- Always return a numerical value (float)
- Round to appropriate decimal places (typically 4-5 decimal places for percentages)

Examples:
- Direct lookup: program="206588", answer=206588.0
- Simple calculation: program="subtract(206588, 181001)", answer=25587.0
- Multi-step: program="subtract(206588, 181001), divide(#0, 181001)", answer=0.14136

Be precise with numbers and calculations. Pay attention to context from previous questions in multi-turn conversations."""


# Global client instance
azure_client = AzureOpenAIClient()