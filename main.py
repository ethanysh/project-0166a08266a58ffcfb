import scraper_atlanta

URL_TO_SCRAPE = 'https://aca3.accela.com/Atlanta_Ga/Welcome.aspx'
CHROME_PATH = r'C:\Users\ethan\OneDrive\Documents\freelance\chromedriver.exe'


def main():
    permits = scraper_atlanta.scraper_atlanta(CHROME_PATH)
    print(permits)


if __name__ == "__main__":
    main()
