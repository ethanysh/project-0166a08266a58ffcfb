import scraper_pittsburgh
from pprint import pprint

CHROME_PATH = r'C:\Users\ethan\OneDrive\Documents\freelance\chromedriver.exe'


def main():
    objects = scraper_pittsburgh.scraper_pittsburgh(CHROME_PATH)
    pprint(objects)


if __name__ == "__main__":
    main()
