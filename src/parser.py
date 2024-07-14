import pickle
import time
import urllib
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from entities import PostInfo, parse_from_article
from custom_enums import MessageType
from colorama import Fore, Style, init
from tqdm import trange
from settings import settings

from db_creator import create_db
from sqlalchemy.orm import Session, joinedload
from models import ENGINE, PostInfoModel

init(autoreset=True)


class Parser:
    def __init__(
            self,
            login: str,
            password: str,
            username: str,
            headless: bool = True,
            show_progress: bool = False,
            cookies_path: Path | None = None,
    ) -> None:
        self.show_progress: bool = show_progress
        self.login: str = login
        self.password: str = password
        self.username: str = username
        self.headless: bool = headless
        self.cookies_path: Path | None = cookies_path
        self.login_url: str = "https://x.com/i/flow/login"
        self.main_url: str = "https://x.com"

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        self.driver: webdriver.Chrome = webdriver.Chrome(options=options)
        self.log_info("Driver initialized")
        self.log_info("Creating database...")
        try:
            create_db()
            self.log_info("Database created")
        except Exception as ex:
            self.log_info(f"Failed to create database with error{ex}", MessageType.ERROR)

    def log_info(self, message: str, style: MessageType = MessageType.INFO) -> None:
        if self.show_progress:
            match style:
                case MessageType.INFO:
                    print(Fore.GREEN + message + Style.RESET_ALL)
                case MessageType.WARNING:
                    print(Fore.YELLOW + message + Style.RESET_ALL)
                case MessageType.ERROR:
                    print(Fore.RED + message + Style.RESET_ALL)

    def load_cookies(self) -> bool:
        if self.cookies_path is not None and self.cookies_path.exists():
            cookies = pickle.load(self.cookies_path.open("rb"))
            [self.driver.add_cookie(cookie) for cookie in cookies]
            return True
        else:
            self.log_info("No cookies file found")
            return False

    def save_cookies(self, cookies_path: Path) -> None:
        pickle.dump(self.driver.get_cookies(), cookies_path.open("wb"))
        self.log_info("cookies saved")

    def login_on_page(
            self, save_cookies: bool = False, save_cookies_path: Path = None
    ) -> bool:
        if save_cookies_path is None:
            save_cookies_path = self.cookies_path
        self.driver.get(url=self.main_url)

        self.log_info("loading cookies...")

        if not self.load_cookies():
            self.driver.get(url=self.login_url)
            time.sleep(5)
            element = self.driver.find_element(By.NAME, value="text")
            time.sleep(1)
            element.send_keys(self.login + "\n")
            time.sleep(1)
            try:
                element = self.driver.find_element(By.NAME, value="text")
                element.send_keys(self.username + "\n")
                time.sleep(1)
            except Exception as ex:
                raise ex
            element = self.driver.find_element(By.NAME, value="password")
            element.send_keys(self.password + "\n")

            time.sleep(10)

            if save_cookies:
                self.save_cookies(save_cookies_path)

        else:
            self.driver.refresh()
            time.sleep(2)
            if self.login_url in self.driver.current_url:
                self.log_info("cookies are outdated", MessageType.ERROR)
                return False
            self.log_info("cookies loaded")

        self.log_info("logged in")
        return True

    def go_to_search_page(
            self,
            query: str = "",
            query_addition: str = "&src=typed_query&f=live",
            language: str = "en",
            min_retweets: int = 2,
    ) -> None:
        query = urllib.parse.quote(query + f" lang:{language} min_retweets:{min_retweets}") + query_addition
        self.driver.get(url=f"https://x.com/search?q={query}")
        time.sleep(5)

    def parse_page(self) -> list[PostInfo]:
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        articles = soup.find_all('article')
        dirty_data = [parse_from_article(BeautifulSoup(str(article), "html.parser")) for article in articles]
        return [data for data in dirty_data if data is not None]

    def scroll_page(self, times: int = 1) -> None:
        for _ in range(times):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

    def parse_page_with_scroll(self, iterations: int = 1, commit_iterations: int = 3) -> None:
        parsed_posts = set()
        saved_posts = set()
        with Session(ENGINE) as session:
            for iteration in trange(iterations):
                self.scroll_page()

                parsed_posts = parsed_posts.union(self.parse_page())
                if iteration % commit_iterations == 0 or iteration == iterations - 1:
                    for post in parsed_posts.difference(saved_posts):
                        session.add(PostInfoModel(**post.model_dump()))
                    self.log_info(f"Committed {len(parsed_posts)} posts")
                    session.commit()
                    saved_posts = saved_posts.union(parsed_posts)


if __name__ == "__main__":
    cookies_path = Path(__file__).parent.parent / "cookies" / "cookies.pkl"
    parser = Parser(
        login=settings.TW_LOGIN,
        password=settings.TW_PASSWORD,
        username=settings.TW_USERNAME,
        headless=False,
        show_progress=True,
        cookies_path=cookies_path,
    )
    if parser.login_on_page(save_cookies=True):
        parser.go_to_search_page("RTX 4060")
        parser.parse_page_with_scroll(iterations=300)
        time.sleep(300)
    else:
        parser.log_info("Failed to login", MessageType.ERROR)
