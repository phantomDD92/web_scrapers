from playwright.sync_api import sync_playwright

MAIN_URL = "https://www.google.com/imghp?hl=en&ogbl"
SEARCH_URL_PREFIX = "https://www.google.com/search"
KEYWORDS = [
    "Nature",
    "Animals",
    "Flowers",
    "Landscape",
    "Beach",
    "Sunset",
    "Mountains",
    "Sky",
    "City",
    "Food",
    "Fashion",
    "Cars",
    "Technology",
    "Abstract",
    "Art",
    "Travel",
    "Friendship",
    "Family",
    "Pets",
    "Wildlife",
    "Architect",
    "Architecture",
    "Space",
    "Ocean",
    "Forest",
    "Music",
    "Sports",
    "Fitness",
    "Yoga",
    "Dance",
    "Party",
    "Celebration",
    "Happiness",
    "Sadness",
    "Joy",
    "Peace",
    "War",
    "Money",
    "Wealth",
    "Success",
    "Failure",
    "Dream",
    "Reality",
    "Fantasy",
    "Hourglass",
    "Day",
    "Night",
    "Morning",
    "Afternoon",
    "Evening",
    "Sunrise",
    "Sunset",
]

class GImagePageDownloader():
    def __init__(self):
        pass

    def screenshot(self, fname):
        screenshot = self.page.screenshot()
        with open(f'./tmp/{fname}.png', 'wb') as f:
            f.write(screenshot)

    def html(self, fname):
        content = self.page.content()
        with open(f'./tmp/{fname}.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
    def handle_route(self, route, request):
        route.continue_()
        count = len(SEARCH_URL_PREFIX)
        if request.url[:count] == SEARCH_URL_PREFIX:
            with open(f'./tmp/request.log', 'a', encoding='utf-8') as f:
                print(f'{request.url}', file=f)
            phrase = request.url.split("?")[1]
            search = phrase.split("&")[0]
            keyword = search.split("=")[1]
            with open(f'./tmp/{keyword}_org.html', 'w', encoding='utf-8') as f:
                f.write(request.response().text())

    def search(self, keyword):
        print("### ", keyword)
        self.page.locator("#APjFqb").press_sequentially(keyword)
        self.page.locator("#APjFqb").press("Enter")
        self.page.wait_for_timeout(3000)
        self.page.wait_for_load_state('load')
        self.screenshot(keyword)
        self.html(keyword)
        self.page.go_back()

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True
        )
        self.context = self.browser.new_context()
        # self.context.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
        self.context.route("**/*", self.handle_route)
        self.page = self.context.new_page()
        print("Go to main page")
        self.page.goto(MAIN_URL, timeout=100000, wait_until='load')
        self.page.get_by_role("button", name="Reject all").click()
        for keyword in KEYWORDS:
            self.search(keyword)
            # break
        self.context.close()
        self.browser.close()

def main():
    scraper = GImagePageDownloader()
    scraper.start()

if __name__ == "__main__":
    main()