from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from prettytable import PrettyTable

class Chapter:
    def __init__(self, text):
        self.title = ""
        self.text = text
        self.length = len(text)
        self.word_count = len(text.split())


    def extract_title(self, soup):
        for tag in ["h1", "h2", "h3", "title"]:
            title = soup.find(tag)
            if title:
                self.title = title.get_text(strip=True)
        self.title = "Untitled chapter"

    def get_title(self):
        return self.title

    def get_text(self):
        return self.text

    def get_length(self):
        return self.length

    def get_word_count(self):
        return self.word_count

    def get_token_count(self):
        return self.length/4


class Character:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description


class Extract_Information:
    def __init__(self, path):
        self.path = path
        self.text = ""
        self.chapters = []
        self.text = self.extract_information()
        self.characters = []

    
    def extract_information(self):
        if self.path.endswith(".epub"):
            self.ebook_to_text()
        return self.text

    def ebook_to_text(self, filter_chapters=True):
        book = epub.read_epub(self.path)
        content = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                content.append((Chapter(soup.get_text())))
        
        self.chapters = content
        if filter_chapters:
            self.filter_chapters()

    def get_chapters(self):
        return self.chapters

    def get_chapter_token_count(self):
        '''
        1 token is around 4 characters thus divided by 4
        '''
        sizes = []
        for chapter in self.chapters:
            sizes.append(chapter.get_token_count())
        return sizes

    def get_chapters_word_count(self):
        sizes = []
        for chapter in self.chapters:
            sizes.append(chapter.get_word_count())
        return sizes

    def get_chapters_titles(self):
        titles = []
        for chapter in self.chapters:
            titles.append(chapter.get_title())
        return titles

    def get_chapter_info(self, displayInfo = False):       
        titles = self.get_chapters_titles()
        token_count = self.get_chapter_token_count()
        word_count = self.get_chapters_word_count()

        info = zip(titles, token_count, word_count)

        if displayInfo:
            table = PrettyTable()
            table.add_column("Chapter Name", titles)
            table.add_column("Token Count", token_count)
            table.add_column("Word Count", word_count)
            print(table)

        return info

    def filter_chapters(self, min_word_count=200):
        unwated_words = ["license", "about", "untitled"]
        self.chapters = [chapter for chapter in self.chapters if not any(word in chapter.get_title().lower() for word in unwated_words)]

        self.chapters = [chapter for chapter in self.chapters if chapter.get_word_count() > min_word_count]

    #TODO ok thats already pretty good, now you can decide to extract characters thanks to the dramatis personae
    #to provide more context to the LLM model, you could also leave it for later and start the script generation code.

extraction = Extract_Information("./data/epdf.pub_priests-of-mars2630113e4568e40991a57be123f3e78049575.epub")
print(extraction.get_chapter_info(displayInfo=True))


