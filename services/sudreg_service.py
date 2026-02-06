import os
import csv
import json
import time
from config import Config
from termcolor import colored
from api_clients import SudregApiClient, CompanyWallApiClient
from db import Company, Database

class SudregService:
    COMPANY_DETAILS_DIR = "data/details"
    COMPANYWALL_DETAILS_DIR = "data/companywall"

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

        if status and status.get('offset', 0) > 0:
            choice = input(f"Do you want to continue from offset {status.get('offset', 0)}? [Y/n] ") or "y"
            if choice.lower() == "y":
                offset = status.get('offset', 0)
    
        while True:
            try:
                companies = self.sudreg_api.get_company_list(offset)
            except Exception as e:
                if "Vaš zahtjev nije vratio ni jedan redak" in str(e):
                    break
                raise e

            if len(companies) == 0:
                break

            filtered_companies = [c for c in companies if self.config.company_filter and c['ime'].lower().find(self.config.company_filter.lower()) > -1]
            filtered_companies = [c for c in filtered_companies if not c['ime'].lower().find(self.config.company_filter_out.lower()) > -1]
            for company in filtered_companies:
                self.db.add_company(Company(**company))

            offset += len(companies)
            self.set_fetch_job_status(offset)
            self.save_db()
            self.print_fetch_all_job_status(len(companies), self.db.count(), offset)

        return self.db.get_all_companies()

    def fetch_all_companies_from_sudreg(self):
        offset = 0
        all: dict[str, str] = {}

        while True:
            try:
                companies = self.sudreg_api.get_company_list(offset)
            except Exception as e:
                print(f"Error fetching companies: {e}")
                break

            all.update({c['mbs']: c['ime'] for c in companies})

            print(f"Exported: {colored(len(all), 'yellow')} companies")
            offset += len(companies)
            if len(companies) < 1000:
                break

        return all

    def export_all_companies_to_csv(self, file_path: str):
        all_companies = self.fetch_all_companies_from_sudreg()

        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['MBS', 'Ime'])
            for mbs, ime in all_companies.items():
                writer.writerow([mbs, ime])

    def fetch_company_details(self, companies: list[Company]):
        processed_count = 0

        print(f"Fetching company details for {colored(str(len(companies)), 'yellow')} companies")
        print()

        choice = input("Continue? [y/N] ") or "n"
        if choice.lower() != "y":
            return

        for c in companies:
            details_filename = f"data/details/{c.mbs}.json"
            if os.path.exists(details_filename):
                continue

            try:
                details = self.sudreg_api.get_company_details_by_mbs(c.mbs)
                c.inject_from_sudreg_object(details)
                processed_count += 1

                self.store_company_details_locally(c.mbs, details)
                print(colored(c.oib, 'green'), c.ime)
                if processed_count % 5 == 0:
                    self.save_db()
                    self.print_fetch_company_details_job_status(processed_count, len(companies) - processed_count)

            except Exception as e:
                print(f"Error fetching company details for {colored(c.mbs, 'yellow')} {colored(c.ime, 'green')}: {e}")
                continue

    def store_company_details_locally(self, mbs: str, details: dict):
        filename = self.get_company_details_filename(mbs)
        with open(filename, 'w') as f:
            json.dump(details, f, indent=2)

    def store_companywall_details_locally(self, mbs: str, details: dict):
        filename = self.get_companywall_details_filename(mbs)
        with open(filename, 'w') as f:
            json.dump(details, f, indent=2)

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

    def export_to_csv(self, file_path: str, exclude_stecaj: bool = True, exclude_no_email: bool = True):
        companies = self.db.get_all_companies()
        if exclude_stecaj:
            companies = [c for c in companies if c.status != 4 and c.ime.lower().find('stečaj') == -1]
        if exclude_no_email:
            companies = [c for c in companies if c.email_adrese and len(c.email_adrese) > 0]

        with open(file_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['MBS', 'Ime', 'OIB', 'DJELATNOST_SIFRA', 'DJELATNOST_NAZIV', 'ZUPANIJA', 'ADRESA', 'NASELJE', 'EMAIL_ADRESE', 'TELEFONSKI_BROJEVI', 'GFI_COUNT', 'STATUS', 'NAZNAKA_IMENA', 'PRAVNI_OBLIK', 'OSTALO'])
            for company in companies:
                writer.writerow([company.mbs, company.ime, company.oib, company.djelatnost_sifra, company.djelatnost_naziv, company.zupanija, company.adresa, company.naselje, company.email_adrese, company.telefonski_brojevi, company.gfi_count, company.status, company.naznaka_imena, company.pravni_oblik, company.ostalo])

    def get_company_details_from_companywall(self):
        companies = self.db.get_all_companies()
        processed_count = 0
        companywall_api = CompanyWallApiClient(self.config, self.db)

        print(f"Fetching company details for {colored(str(len(companies)), 'yellow')} companies")
        print()
        choice = input("Do you want to continue? [y/N] ") or "n"
        if choice.lower() != "y":
            return

        for company in companies:
            filename = self.get_companywall_details_filename(company.mbs)
            if os.path.exists(filename):
                continue

            details = companywall_api.extract_company_data(company.oib)
            processed_count += 1
            self.store_companywall_details_locally(company.mbs, details)
            print(colored(company.oib, 'green'), company.ime)

            # wait for 1 second
            time.sleep(1)

    def get_company_details_filename(self, mbs: str):
        return f"{self.COMPANY_DETAILS_DIR}/{mbs}.json"

    def get_companywall_details_filename(self, mbs: str):
        return f"{self.COMPANYWALL_DETAILS_DIR}/{mbs}.json"