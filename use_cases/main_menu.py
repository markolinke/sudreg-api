import json
from config import Config
from api_clients import SudregApiClient
from termcolor import colored
from services import SudregService
from db import Database

class CompanyLoop:
    config: Config
    sudreg_api: SudregApiClient
    sudreg_service: SudregService
    db: Database

    def __init__(self, config: Config):
        self.config = config
        self.sudreg_api = SudregApiClient(config)
        self.sudreg_api.authenticate()
        self.db = Database(self.config.db_file_path)
        self.sudreg_service = SudregService(self.sudreg_api, self.db, self.config)

    def print_table(self, data: dict, title_length: int = 20, header: bool = False):
        if header:
            print('-' * 80)
        for key, value in data.items():
            title = key.ljust(title_length, ' ')
            print(f"{colored(title, 'green')} {value}")
        print()

    def print_company_intro(self, details: dict):

        info = {
            "Ime": details['tvrtka']['ime'],
            "Naselje": details.get('sjediste', {}).get('naziv_naselja', 'N/A'),
            "Ulica": details.get('sjediste', {}).get('ulica', 'N/A'),
            "Email": ', '.join([e['adresa'] for e in details.get('email_adrese', [])]),
            "Postupak": details.get('postupak', {}).get('postupak', {}).get('znacenje', 'N/A'),
        }

        self.print_table(info, header=True)

    def print_company_details(self, details: dict):
        print(json.dumps(details, indent=2))

    def company_loop_menu(self, company_name: str) -> str:
        menu = {
            "A": f"Printaj sve detalje za {colored(company_name, 'yellow')}",
            "OIB": "Upisi drugi OIB",
            "<RETURN>": "Izadji van iz petlje",
        }
        self.print_table(menu)
        return input("Tvoj odabir: ") or ""

    def company_details(self):
        oib = input("Enter OIB or 'ALL' (empty to exit) [99336354871]: ") or "99336354871"

        while oib.strip() != "":
            details = self.sudreg_api.get_company_details_by_oib(oib)
            self.print_company_intro(details)

            # print details in json format, properly formatted
            choice = self.company_loop_menu(details['tvrtka']['ime'])
            if choice == "":
                return
            elif choice.lower() == "a":
                self.print_company_details(details)
            elif len(choice) > 9:
                oib = choice
            else:
                print("Invalid choice")
                return

    def main_loop_menu(self):
        menu = {
            "fa": "Fetch all companies from Sudreg",
            "fd": "Fetch company details from Sudreg",
            "oib": "Get single company details by OIB",
            "csv": "Export companies to CSV",
            "cw": "Get company details from CompanyWall",
            "q": "Exit",
        }
        self.print_table(menu)
        return input("Tvoj odabir: ") or ""

    def fetch_all_companies_from_sudreg(self):
        if self.db.is_dirty:
            self.db.save_to_file()
        
        if self.db.count() != 0:
            print(f"There are {self.db.count()} companies in the database")
            choice = input("Do you want to continue? [y/N] ") or "n"

            if choice.lower() == "n":
                return

        self.sudreg_service.fetch_all_companies()

    def fetch_company_details_from_sudreg(self):
        all = self.db.get_all_companies()
        self.sudreg_service.fetch_company_details(all)

    def export_companies_to_csv(self):
        file_path = input("Enter the path to the CSV file: ")
        self.sudreg_service.export_to_csv(file_path)

    def get_company_details_from_companywall(self):
        self.sudreg_service.get_company_details_from_companywall()

    def start_main_loop(self):
        print("\033[2J\033[H")
        print("Welcome to the company loop")
        print("--------------------------------")
        print()
        while True:
            choice = self.main_loop_menu()
            if choice == "fa":
                self.fetch_all_companies_from_sudreg()
            elif choice == "fd":
                self.fetch_company_details_from_sudreg()
            elif choice == "oib":
                self.company_details()
            elif choice == "csv":
                self.export_companies_to_csv()
            elif choice == "cw":
                self.get_company_details_from_companywall()
            elif choice == "q":
                break
            else:
                print("Invalid choice")
