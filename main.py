import scraper_fort_worth
from pprint import pprint

CHROME_PATH = r'C:\Users\ethan\OneDrive\Documents\freelance\chromedriver.exe'
URL = 'https://accela.fortworthtexas.gov/CitizenAccess/Cap/CapHome.aspx?module=Development&TabName' \
      '=Development&TabList=Home%7C0%7CDevelopment%7C1%7CFire%7C2%7CGasWell%7C3%7CPlanning%7C4%7C' \
      'Licenses%7C5%7CStreetUse%7C6%7CInfrastructure%7C7%7CCurrentTabIndex%7C1'


def main():
    permits = scraper_fort_worth.scraper_fort_worth(CHROME_PATH, URL)
    pprint(permits)


if __name__ == "__main__":
    main()
