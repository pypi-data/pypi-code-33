#  -*- coding: utf-8 -*-

import os
import sys

import urllib3
from bs4 import BeautifulSoup


def print_help():
    print("USAGE : FFFLaTeX [<Number of FFF>|latest]")


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_latest_version_data():
    blog_list_url = "https://www.factorio.com/blog/"
    soup = get_soup(blog_list_url)
    last_blog_listing = soup.h2.find_next("ul").find_next("li")
    url = "https://factorio.com" + last_blog_listing.find_next("a").get("href")
    name = last_blog_listing.find_next("a").text.lstrip().rstrip()
    author = last_blog_listing.find_next("div").text.lstrip().rstrip()
    return (name, author, url)


def print_latest_version(version_data: tuple):
    print("Latest FFF:\t" + "\n".join(version_data))


def get_blog_url(latest_version_data: tuple) -> str:
    blog_url = latest_version_data[2]
    if len(sys.argv) == 1:
        print_latest_version(latest_version_data)
        num = input("Enter the number of the current FFF: ")
        while True:
            try:
                num = int(num)
                break
            except Exception:
                num = input("Enter the number of the current FFF:")
        print("Generating FFF", num)
        return "https://factorio.com/blog/post/fff-" + str(num)
    elif len(sys.argv) == 2:
        try:
            num = int(sys.argv[1])
            print("Generating FFF", num)
            return "https://factorio.com/blog/post/fff-" + str(num)
        except Exception as e:
            if sys.argv[1] != "latest":
                print_help()
                exit(-1)
    else:
        print_help()
        exit(-1)
    print("Generating latest FFF")
    return blog_url


def get_soup(url: str):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    return BeautifulSoup(response.data.decode('utf-8'), 'html5lib')


def generate_img_data(soup, img_urls, img_size):
    for link in soup.find_all('img'):
        img_urls.add(link.get('src'))
        img_size[link.get('src')] = "0.8\\textwidth"
    return (soup, img_urls, img_size)


def generate_mp4_data(soup, img_urls, img_size):
    for link in soup.find_all('source'):
        src = link.get('src')
        img_urls.add(src)
        img_size[link.get('src')] = "0.8\\textwidth"
    return (soup, img_urls, img_size)


def generate_media_names(img_urls, img_extension, img_size, img_names):
    from FFFLaTeX.parserutil import generate_name

    i = 0
    for img_url in img_urls:
        name = "FFFparserIMG" + generate_name(i).lower()
        for ext in [".png", ".jpg", ".gif", ".mp4", ".webm"]:
            if img_url.endswith(ext):
                img_extension[img_url] = ext
                break

        print(img_url, "\t->\t", name, ", width=", img_size[img_url])
        i += 1
        img_names[img_url] = name
    return (img_urls, img_extension, img_size, img_names)


def get_blog_number(url):
    num = ""
    for c in url[::-1]:
        if c.isnumeric():
            num = c + num
        else:
            return num


def filter_out_incompatible_medias(img_urls):
    return filter(lambda url: not url.endswith(".webm"), img_urls)


def parse_fff_authors_data(data: str):
    # start is after "Posted by" and ends before on @date
    return data[len("Posted by"):data.find(" on "):]


def parse_fff_date_data(data: str):
    # start is after "Posted by" and ends before on @date
    return data[data.find(" on ") + 3:data.rfind(","):]


def parse_fff_author_and_date_from_header_str(header: str):
    return (parse_fff_authors_data(header), parse_fff_date_data(header))


def fff_data(blog):
    from FFFLaTeX.parserutil import sanitize_string
    title = sanitize_string(blog.find_next("h2"))
    header = blog.find_next('div')
    authors, date = parse_fff_author_and_date_from_header_str(header.text)
    return date, authors, title


def write_latex_download_header(out, payload):
    for img_url in payload["__img_urls"]:
        args = []
        if payload["__img_size"][img_url] is not None:
            args.append("width=" + str(payload["__img_size"][img_url]))

        out.write("\\write18{wget -N " + img_url + " -P ../out/pics/ -O " +
                  payload["__img_names"][img_url] + payload["__img_ext"][
                      img_url] + " }\n" + "\\newcommand{\\" +
                  payload["__img_names"][
                      img_url] + "}{\\includegraphics[" + ','.join(
            args) + "]{" + payload["__img_names"][img_url] +
                  payload["__img_ext"][img_url] + "}}\n")


def generate_latex_file(doc_name, payload, blog):
    ensure_dir("./" + doc_name + "/")
    with open("./" + doc_name + "/" + doc_name + ".tex", "w",
              encoding="utf-8") as out:


        from FFFLaTeX.parserutil import process_symbols, get_latex_for_element, \
            generate_latex_from_element
        out.write(process_symbols(None, payload,
                                  get_latex_for_element("documentHeader")))

        # generate constants
        write_latex_download_header(out, payload)

        out.write(process_symbols(None, payload,
                                  get_latex_for_element("documentTitle")))

        out.write(process_symbols(None, payload,
                                  get_latex_for_element("documentBegin")))

        # generate content
        blog_temp = blog
        size = 0
        # we first travel the children space to determine their amount
        for element in blog_temp.children:
            size += 1

        # we skip the first already read elements and the useless last ones
        element_i = -1
        for element in blog.children:
            element_i += 1
            if element_i <= 5 or element_i >= size - 4:
                continue
            else:
                out.write(generate_latex_from_element(element, payload))

        out.write(process_symbols(None, payload,
                                  get_latex_for_element("documentEnd")))

def main():
    img_urls = set()
    img_size = {}
    img_names = {}
    img_ext = {}
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    latest_version_data = get_latest_version_data()
    blog_url = get_blog_url(latest_version_data)
    num = get_blog_number(blog_url)
    soup = get_soup(blog_url).find("div", class_="blog-post")
    date, authors, title = fff_data(soup)
    soup, img_urls, img_size = generate_img_data(soup, img_urls, img_size)
    soup, img_urls, img_size = generate_mp4_data(soup, img_urls, img_size)
    img_urls, img_ext, img_size, img_names = generate_media_names(img_urls,
                                                                  img_ext,
                                                                  img_size,
                                                                  img_names)

    img_urls = filter_out_incompatible_medias(img_urls)

    doc_name = "FFF" + str(num)

    payload = {
        "TeX":         "",
        "__num":       num,
        "__date":      date,
        "__authors":   authors,
        "__title":     title,
        "__url":       blog_url,
        "__img_urls":  img_urls,
        "__img_ext":   img_ext,
        "__img_names": img_names,
        "__img_size":  img_size,
        "__abort":     False
    }
    generate_latex_file(doc_name, payload, soup)


if __name__ == "__main__":
    main()
