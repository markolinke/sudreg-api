import base64
import logging
import requests

from config import Config

requests.packages.urllib3.disable_warnings()

class SudregApiClient:
    config: Config
    auth_token: str

    def __init__(self, config: Config):
        self.config = config

    def authenticate(self):
        auth_str = f"{self.config.client_id}:{self.config.client_secret}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(
            f"{self.config.api_url}/api/oauth/token", 
            headers=headers, 
            data=data,
            verify=False
        )
        
        if response.status_code in (200, 201):
            token_data = response.json()
            self.auth_token = token_data["access_token"]
        else:
            logging.error("Greška %s: %s", response.status_code, response.text)
            raise Exception(f"Greška {response.status_code}: {response.text}")

    def get_response(self, endpoint: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json"
        }

        response = requests.get(
            f"{self.config.api_url}/{endpoint}", 
            headers=headers, 
            verify=False)

        if response.status_code in (200, 201):
            return response.json()
        else:
            logging.error("Greška %s: %s", response.status_code, response.text)
            raise Exception(f"Greška {response.status_code}: {response.text}")

    def get_company_list(self, offset: int | None = None) -> list:
        endpoint = "api/javni/tvrtke"
        if offset is not None:
            endpoint += f"?offset={offset}"

        response = self.get_response(endpoint)
        return response

    def get_company_details_by_oib(self, oib: str) -> dict:
        endpoint = f"api/javni/detalji_subjekta?tip_identifikatora=OIB&identifikator={oib}&expand_relations=true"
        return self.get_response(endpoint)

    def get_company_details_by_mbs(self, mbs: str) -> dict:
        endpoint = f"api/javni/detalji_subjekta?tip_identifikatora=MBS&identifikator={mbs}&expand_relations=true"
        return self.get_response(endpoint)