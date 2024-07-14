from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from pydantic import BaseModel

init(autoreset=True)


def format_string(s, n):
    formatted_string = f"{s[:n]}...".replace("\n", "") if len(s) > n else f"{s}"
    return formatted_string


def number_normalizer(number: str) -> int:
    multiplier = {"k": 10**3, "m": 10**6, "b": 10**9}
    if number == "":
        return 0
    if number.isdigit():
        return int(number)
    elif number[-1].isalpha():
        prefix = number[-1].lower()
        if prefix in multiplier.keys():
            return int(float(number[:-1]) * multiplier.get(number[-1].lower(), 1))
        else:
            print(Fore.RED + f"Unknown prefix: {prefix}" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Unknown number format: {number}" + Style.RESET_ALL)
    return 0


class PostInfo(BaseModel):
    content: str
    author_nickname: str
    author_name: str
    created_at: datetime
    views: int
    likes: int
    reposts: int
    comments: int

    def __str__(self):
        return (
            f"Post By: {self.author_name} ({self.author_nickname})\n"
            f"at {self.created_at.strftime('%A, %B %d, %Y %H:%M:%S')}\n"
            f"{self.content}\n"
            f"V: {self.views}, L: {self.likes}, R: {self.reposts}, C: {self.comments}\n"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, PostInfo):
            return False
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.model_fields.keys()
        )

    def __hash__(self):
        return hash(tuple(getattr(self, attr) for attr in self.model_fields.keys()))

    class Config:
        from_attributes = True


def parse_from_article(article: BeautifulSoup) -> PostInfo | None:
    try:
        spans = [
            span.text
            for span in article.select("span")
            if span.findChildren("span", recursive=False) == []
        ]
        views, likes, reposts, comments = list(map(number_normalizer, spans[::-1][:4]))
        posted_at = article.find("time")["datetime"]
        posted_at = datetime.fromisoformat(posted_at.rstrip("Z")).replace(
            tzinfo=timezone.utc
        )
        author_name = spans[0]
        author_nickname = spans[2]
        content = "".join(
            [span.replace("\n", "").replace("Show more", "") for span in spans[4:-4]]
        )
        return PostInfo(
            content=content,
            author_nickname=author_nickname,
            author_name=author_name,
            created_at=posted_at,
            views=views,
            likes=likes,
            reposts=reposts,
            comments=comments,
        )
    except Exception as ex:
        print(
            Fore.RED
            + f"Failed to parse article with error: {format_string(str(ex), 15)}"
            + Style.RESET_ALL
        )
        return None


if __name__ == "__main__":
    file = Path(__file__).parent / "page1.html"
    text = file.read_text()
    print(parse_from_article(BeautifulSoup(text, "html.parser")))
