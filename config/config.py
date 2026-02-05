from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    api_env: str
    client_id: str
    client_secret: str
    api_url: str
    
    def __init__(self):
        self.api_env = os.getenv("api_env")
        self.client_id = os.getenv(f"{self.api_env}_client_id")
        self.client_secret = os.getenv(f"{self.api_env}_client_secret")
        self.api_url = os.getenv(f"{self.api_env}_api_url")
