import json
from config import Config
from sudreg_api import SudregApiClient
from termcolor import colored

class CompanyLoop:
    config: Config
    sudreg_api: SudregApiClient

    def __init__(self, config: Config):
        self.config = config
        self.sudreg_api = SudregApiClient(config)
        self.sudreg_api.authenticate()

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
            details = self.sudreg_api.get_company_details(oib)
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

    def loop_all_companies(self):
        offset = 0

        while True:
            companies = self.sudreg_api.get_company_list(offset)
            if len(companies) == 0:
                break

            for company in companies:
                if str(company['ime']).lower().find('za graditeljstvo') > 1:
                    print(colored(company['mbs'], 'yellow'), colored(company['ime'], 'green'))

            offset += len(companies)
        return

    def main_loop_menu(self):
        menu = {
            "1": "Loop all companies",
            "2": "Get company details",
            "9": "Exit",
        }
        self.print_table(menu)
        return input("Tvoj odabir: ") or ""

    def start_main_loop(self):
        print("\033[2J\033[H")
        print("Welcome to the company loop")
        print("--------------------------------")
        print()
        while True:
            choice = self.main_loop_menu()
            if choice == "1":
                self.loop_all_companies()
            elif choice == "2":
                self.company_details()
            elif choice == "9":
                break
            else:
                print("Invalid choice")
