import scraper_atlanta
from pprint import pprint

URL_TO_SCRAPE = 'https://aca3.accela.com/Atlanta_Ga/Welcome.aspx'
CHROME_PATH = r'C:\Users\ethan\OneDrive\Documents\freelance\chromedriver.exe'


def main():
    permits = scraper_atlanta.scraper_atlanta(CHROME_PATH, URL_TO_SCRAPE, 0)
    pprint(permits)


if __name__ == "__main__":
    main()
