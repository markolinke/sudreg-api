from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    api_env: str
    client_id: str
    client_secret: str
    api_url: str
    db_file_path: str
    company_filter: str
    company_filter_out: str
    
    def __init__(self):
        self.api_env = os.getenv("api_env")
        self.client_id = os.getenv(f"{self.api_env}_client_id")
        self.client_secret = os.getenv(f"{self.api_env}_client_secret")
        self.api_url = os.getenv(f"{self.api_env}_api_url")
        self.db_file_path = os.getenv("db_file_path")
        self.company_filter = os.getenv("company_filter")
        self.company_filter_out = os.getenv("company_filter_out")