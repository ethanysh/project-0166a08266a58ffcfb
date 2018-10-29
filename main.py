import scraper_cleveland
from pprint import pprint

CHROME_PATH = r'C:\Users\ethan\OneDrive\Documents\freelance\chromedriver.exe'
URL='https://ca.permitcleveland.org/public/welcome.aspx'


def main():
    permits = scraper_cleveland.scraper_cleveland(CHROME_PATH, URL, 4)
    pprint(permits)


if __name__ == "__main__":
    main()
