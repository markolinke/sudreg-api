import requests
from bs4 import BeautifulSoup
import re

from config import Config
from db import Database

class CompanyWallApiClient:
    config: Config
    db: Database
    base_url: str

    def __init__(self, config: Config, db: Database):
        self.config = config
        self.db = db
        self.base_url = "https://www.companywall.hr"

    def search_company(self, oib: str):
        search_url = f"{self.base_url}/pretraga?query={oib}"
        response = requests.get(search_url)
        return response.text

    def extract_company_data(self, oib: str):
        # Step 1: Search for the company profile URL on CompanyWall
        search_url = f"https://www.companywall.hr/pretraga?query={oib}"
        response = requests.get(search_url)
        if response.status_code != 200:
            return {"error": "Search page not accessible"}

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first link to a company profile (assuming it's the top result)
        profile_link = None
        for a in soup.find_all('a', href=True):
            if '/tvrtka/' in a['href']:
                profile_link = "https://www.companywall.hr" + a['href']
                break
        
        if not profile_link:
            return {"error": "No profile link found for OIB"}

        # Step 2: Fetch the profile page
        profile_response = requests.get(profile_link)
        if profile_response.status_code != 200:
            return {"error": "Profile page not accessible"}

        profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # Extract company name (usually in <h1> or similar)
        name = profile_soup.find('h1').text.strip() if profile_soup.find('h1') else "N/A"
        
        # Find the financial summary table
        table = profile_soup.find('table')  # Assuming the first table is the financial one
        data = {
            "name": name,
            "revenues": {},
            "employees": {},
            "ratings": "N/A"
        }
        
        if table:
            rows = table.find_all('tr')
            years = []
            for th in rows[0].find_all('th'):  # Get years from header
                year = th.text.strip()
                if re.match(r'\d{4}', year):
                    years.append(year)
            
            # Last three years (assuming sorted ascending)
            last_three_years = sorted(years, reverse=True)[:3]
            
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) > 0:
                    label = cells[0].text.strip()
                    if label == 'Ukupni prihodi':
                        for i, year in enumerate(years, start=1):
                            if year in last_three_years:
                                data["revenues"][year] = cells[i].text.strip()
                    elif label == 'Broj zaposlenih':
                        for i, year in enumerate(years, start=1):
                            if year in last_three_years:
                                data["employees"][year] = cells[i].text.strip()
        
        # Extract ratings if available (look for text containing 'Bonitetna ocjena')
        ratings_section = profile_soup.find(string=re.compile('Bonitetna ocjena', re.I))
        if ratings_section:
            # Assuming it's near a span or div with the rating
            rating = ratings_section.find_next(string=True).strip()
            data["ratings"] = rating
        
        return data
