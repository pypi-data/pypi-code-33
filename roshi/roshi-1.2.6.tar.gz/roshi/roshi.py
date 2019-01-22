import bs4
import os
import requests
import multiprocessing
import zipfile
import io
from tqdm import tqdm

SOURCES = {
    'reader': {
        'base_url': 'https://www.mangareader.net'
    },
    'jaminis': {
        'base_url': 'https://jaiminisbox.com/reader/series/'
    },
}

# Helpers
def sluggify(string):
    tokens = ":', "
    temp = string.lower()
    for token in tokens:
        temp = temp.replace(token, "-")

    return temp


class Chapter:
    def __init__(self, name, number, url):
        self.name = name
        self.number = number
        self.url = url

    def __repr__(self):
        return '<Chapter - Name:{}, Url:{}>\n'.format(self.name, self.url)
  
    def __str__(self):
        return '<Chapter - Name:{}, Url:{}>'.format(self.name, self.url)

class Manga:
    def __init__(self, name):
        # TODO: Add option to specifiy save location
        self._name = name
        self._slug_name = sluggify(name)
        self.chapter_archive = self.get_chapter_archive()


    def get_chapter_archive(self):
        # TODO: Add decorator for these functions to automatically add them to a dict
        chapter_archive = {}
        chapter_archive['jaminis'] = self._get_jamini_archive()
        chapter_archive['reader'] = self._get_m_reader_archive()
        
        return chapter_archive      


    def get_series(self, source = 'reader'):
        # TODO: Multiprocessing for series
        # TODO: Add option to give file path
        chapters = self.chapter_archive[source]

        for num, chapter in tqdm(chapters.items()):
            content = self._get_chapter_m_reader(chapter.url)
            with open("{}.cbz".format(chapter.name), "wb") as f:
                f.write(content)


    def get_latest(self):
        latest_source = None
        latest_num = 0
        latest_chapter = None

        print("Going through sources to find the latest chapter:")
        for source, archive in tqdm(self.chapter_archive.items()):
            # continue if archive is empty
            # need to change this
            if archive == {}:
                continue
            current_num = self.get_latest_number(archive)
            if current_num > latest_num:
                latest_num = current_num
                latest_source = source
                latest_chapter = archive[latest_num]
        
        print("Latest is Chapter {}".format(latest_num))

        if source == 'jaminis':
            content = self._get_chapter_jamini(archive[latest_num].url)
        elif source == 'reader':
            content = self._get_chapter_m_reader(archive[latest_num].url)
        
        

        with open("{}.cbz".format(latest_chapter.name), "wb") as f:
            f.write(content)


    def get_latest_details(self):
        """
            Get the latest chapter number and the details of the same chapter
        """
        latest_number = 0
        latest_chapter = None
        for k, v in self.chapter_archive.items():
            if v == {}:
                continue
            
            source_latest = sorted(v.keys())[-1]

            if source_latest > latest_number:
                latest_number = source_latest
                latest_chapter = v[latest_number]

        return latest_number, latest_chapter


    # TODO: Implement these get archive functions in a better way
    def _get_m_reader_archive(self):
        source_url = SOURCES['reader']['base_url']
        url = source_url + '/' + self._slug_name
        req = requests.get(url)
        soup = bs4.BeautifulSoup(req.text, 'lxml')
        chapters = soup.select('#listing tr a')

        chapter_archive = {}

        for chapter in chapters:
            url = source_url + chapter.get('href')
            name = chapter.text
            numbers = [int(s) for s in name.split() if s.isdigit()]
            number = numbers[0]
            chapter_archive[number] = Chapter(name, number, url)

        return chapter_archive
    

    def _get_jamini_archive(self):
        if self._slug_name == "one-piece":
            source_name = "one-piece-2"
        else:
            source_name = self._slug_name
        chapter_archive = {}
        url = SOURCES['jaminis']['base_url'] + source_name
        req = requests.get(url)
        if req.status_code != 200:
            return chapter_archive
        soup = bs4.BeautifulSoup(req.text, 'lxml')
        chapters = soup.select('.group')[0].select('.element')

        
        
        for chapter in chapters:
            url = chapter.select('.icon_wrapper')[0].select('a')[0].get('href')
            name = chapter.select('.title')[0].select('a')[0].get("title")
            numbers = [int(s) for s in name.replace(":", "").split() if s.isdigit()]
            if (len(numbers)) > 0:
                number = numbers[0]
                chapter_archive[number] = Chapter(name, number, url)
            
        return chapter_archive
            

    # Scraping Helper functions

    # Recieves the url to get the latest chapter from Jamini's Box
    # Returns the file object
    def _get_chapter_jamini(self, url):
        latest_req = requests.get(url)

        return latest_req.content


    def _get_chapter_m_reader(self, chapter_url):
        # TODO: Multiprocessing for image downloading
        def get_image(url):
            image_req = requests.get(url)
            soup = bs4.BeautifulSoup(image_req.text, 'lxml')
            img = soup.select('#img')
            image_url = img[0].get('src')
            image_req = requests.get(image_url)
            
            return image_req.content

        chapter_req = requests.get(chapter_url)
        soup = bs4.BeautifulSoup(chapter_req.text, 'lxml')
        pages = soup.select('#pageMenu option')

        in_mem_zip = io.BytesIO()
        with zipfile.ZipFile(in_mem_zip, "w") as chapter_zip:
            for i, page in enumerate(pages):
                page_url = SOURCES['reader']['base_url'] + page.get('value')
                page_name = 'Page-' + str(i + 1) + '.jpg'
                chapter_zip.writestr(page_name, get_image(page_url))

        chapter_content = in_mem_zip.getvalue()
        in_mem_zip.close()

        return chapter_content


    def __str__(self):
        return "<Manga - Series:{}>".format(self._name)


if __name__ == '__main__':
    a = Manga("One Piece 2")
    print(a.get_latest_details())