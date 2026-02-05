import csv
from config import Config
from termcolor import colored
from sudreg_api import SudregApiClient
from db import Company, Database

class SudregService:
    sudreg_api: SudregApiClient
    db: Database
    config: Config
    
    def __init__(self, sudreg_api: SudregApiClient, db: Database, config: Config):
        self.sudreg_api = sudreg_api
        self.db = db
        self.config = config

    def fetch_all_companies(self) -> list[Company]:
        offset = 0
        status = self.db.get_fetch_job_status()
        preserve_db = False

        if status and status.get('offset', 0) > 0:
            choice = input(f"Do you want to continue from offset {status.get('offset', 0)}? [Y/n] ") or "y"
            if choice.lower() == "y":
                offset = status.get('offset', 0)
                preserve_db = True
            else:
                self.db.clear(fetch_job_status=True)
                offset = 0
    
        if not preserve_db:
            self.db.clear(companies=True)

        while True:
            companies = self.sudreg_api.get_company_list(offset)
            if len(companies) == 0:
                break

            filtered_companies = [c for c in companies if self.config.company_filter and c['ime'].lower().find(self.config.company_filter.lower()) > -1]
            for company in filtered_companies:
                self.db.add_company(Company(**company))

            offset += len(companies)
            self.set_fetch_job_status(offset)
            self.save_db()
            self.print_fetch_all_job_status(len(companies), self.db.count(), offset)

        return self.db.get_all_companies()

    def fetch_company_details(self, companies: list[Company], store_details_locally: bool = True):
        processed_count = 0

        print(f"Fetching company details for {colored(str(len(companies)), 'yellow')} companies")
        print()
        choice = input("Continue? [y/N] ") or "n"
        if choice.lower() != "y":
            return

        for c in companies:
            try:
                details = self.sudreg_api.get_company_details_by_mbs(c.mbs)
                c.inject_details(details)
                processed_count += 1
                print(colored(c.oib, 'green'), c.ime)

                if processed_count % 5 == 0:
                    self.save_db()
                    self.print_fetch_company_details_job_status(processed_count, len(companies) - processed_count)

                if store_details_locally:
                    self.store_company_details_locally(c.mbs, details)

            except Exception as e:
                print(f"Error fetching company details for {colored(c.mbs, 'yellow')} {colored(c.ime, 'green')}: {e}")
                continue

    def store_company_details_locally(self, filename: str, details: dict):
        with open(f'data/details/{filename}.json', 'w') as f:
            f.write(details)

    def print_fetch_all_job_status(self, batch_count: int, total_count: int, offset: int):
        msg = f"Fetched {colored(str(batch_count), 'yellow')} companies. Total companies: {colored(str(total_count), 'yellow')}, current offset: {colored(str(offset), 'yellow')}."
        print(msg)

    def print_fetch_company_details_job_status(self, fetched_count: int, remaining_count: int):
        msg = f"Fetched {colored(str(fetched_count), 'yellow')} companies. Remaining: {colored(str(remaining_count), 'yellow')}."
        print(msg)

    def save_db(self):
        self.db.save_to_file()

    def set_fetch_job_status(self, offset: int | None = None):
        status = self.db.get_fetch_job_status()
        if offset:
            status['offset'] = offset
        self.db.set_fetch_job_status(status)

    def export_to_csv(self, file_path: str):
        companies = self.db.get_all_companies()
        with open(file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['MBS', 'Ime', 'OIB', 'DJELATNOST_SIFRA', 'DJELATNOST_NAZIV', 'ZUPANIJA', 'ADRESA', 'NASELJE', 'EMAIL_ADRESE', 'TELEFONSKI_BROJEVI', 'OSTALO'])
            for company in companies:
                writer.writerow([company.mbs, company.ime, company.oib, company.djelatnost_sifra, company.djelatnost_naziv, company.zupanija, company.adresa, company.naselje, company.email_adrese, company.telefonski_brojevi, company.ostalo])