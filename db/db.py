import json
import os
from .data_models import Company

class Database:
    companies: dict[str, Company] = {}
    fetch_job_status: dict[str, any] = {}
    file_path: str
    is_dirty: bool = False

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.load_from_file()

    def add_company(self, company: Company):
        if company.mbs in self.companies:
            c = self.companies[company.mbs]
            c.update_with_values(company)
            self.companies[company.mbs] = c
        else:
            self.companies[company.mbs] = company
        self.is_dirty = True

    def get_company_my_mbs(self, mbs: str) -> Company:
        return self.companies.get(mbs)
    
    def get_company_by_oib(self, oib: str) -> Company:
        return next((c for c in self.companies.values() if c.oib == oib), None)

    def get_company_list_by_name(self, name: str) -> list[Company]:
        return [c for c in self.companies.values() if c.ime.lower().find(name.lower()) > -1] if name else []
    
    def save_to_file(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        self.is_dirty = False

    def load_from_file(self):
        self.companies = {}
        self.fetch_job_status = {}

        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                # try load
                try:
                    self.from_dict(json.load(f))
                except json.JSONDecodeError as e:
                    print(f"Error loading companies from file: {e}")
                    self.companies = {}
        self.is_dirty = False

    def to_dict(self) -> dict:
        companies = [d.to_dict() for d in self.companies.values()]

        return {
            "companies": companies,
            "fetch_job_status": self.fetch_job_status
        }

    def from_dict(self, data: dict):
        self.companies = {c['mbs']: Company(**c) for c in data['companies']}
        self.fetch_job_status = data.get('fetch_job_status', {})

    def get_all_companies(self) -> list[Company]:
        return list[Company](self.companies.values())
    
    def count(self) -> int:
        return len(self.companies)

    def clear(self, companies: bool = False, fetch_job_status: bool = False):
        if companies:
            self.companies = {}
        if fetch_job_status:
            self.fetch_job_status = {}
        
        self.is_dirty = True

    def set_fetch_job_status(self, status: dict[str, any]):
        self.fetch_job_status = status
        self.is_dirty = True

    def get_fetch_job_status(self) -> dict[str, any]:
        return self.fetch_job_status
