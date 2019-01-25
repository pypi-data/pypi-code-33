# -*- coding: UTF-8 -*-

""" Main Module """

from __future__ import unicode_literals

import argparse
import threading
import requests
from xml.etree import ElementTree
from six import string_types

try:
    import queue  # Python 3
except ImportError:
    import Queue as queue  # Python 2

try:
    from tkinter import *  # Python 3
except ImportError:
    from Tkinter import *  # Python 2

try:
    import readline
except ImportError:
    readline = None  # readline not available

try:
    from urllib.parse import urlparse  # Python 3
except ImportError:
    from urlparse import urlparse  # Python 2


def get_domain(url):
    """
    From a given URL returns just the protocol and domain
    :param url: any URL
    :return: protocol and domain name of that URL
    """
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    return domain


def is_in_structure(key_to_search, value_to_search, structure):
    """Recursive function checking structures made of nested dictionaries and lists if they contain specific key having a specific value"""
    if isinstance(structure, dict):
        if key_to_search in structure:
            value = structure.get(key_to_search)
            return isinstance(value, string_types) and value_to_search.lower() in value.lower()
        else:
            return any((is_in_structure(key_to_search, value_to_search, value) for value in structure.values()))
    elif isinstance(structure, list):
        return any((is_in_structure(key_to_search, value_to_search, el) for el in structure))
    return False


def search_for_string(url, tag, value, results_queue=None):
    """
    Searches in multiple pages of an API for a specific tag and value.

    :param url: URL of an XML API endpoint
    :param tag: XML tag or JSON key to search for
    :param value: String to search in the value of the XML tag or JSON key
    :param results_queue: Queue where to put the results in case of asyncronious execution
    :return: if results_queue is not given, a list of page URLs with the search results
    """
    results = []
    domain = get_domain(url)

    def search_in_page(page_url, tag_to_search, value_to_search):
        headers = {
            'User-Agent': 'Mozilla/5.0',
        }
        response = requests.get(page_url, headers=headers, allow_redirects=True)
        if response.status_code != requests.codes.OK:
            print("Server Error when reading {}".format(page_url))
            return

        try:
            root_dict = response.json()
        except ValueError:
            # XML case
            root = ElementTree.fromstring(response.content)

            for node in root.findall('.//{}'.format(tag_to_search)):
                if node.text and value_to_search.lower() in node.text.lower():
                    results.append(page_url)
                    break

            page_url = root.findtext('./meta/next')
        else:
            # JSON case
            if is_in_structure(tag_to_search, value_to_search, root_dict):
                results.append(page_url)

            page_url = root_dict['meta']['next']

        if page_url:
            if page_url.startswith("/"):
                page_url = domain + page_url
            search_in_page(page_url=page_url, tag_to_search=tag_to_search, value_to_search=value_to_search)

    search_in_page(url, tag, value)

    if results_queue:
        results_queue.put(results)
    else:
        return results


class App:
    """
    GUI App for the search input and output
    """
    def __init__(self, master):
        self.results_queue = None
        self.background_thread = None
        self.master = master
        self.results = []
        master.title("Search in XML or JSON API")

        main_frame = Frame(master, padx=10, pady=10)
        main_frame.pack()

        frame1 = Frame(main_frame, padx=5, pady=5)
        frame1.pack()
        label_url = Label(frame1, text="API URL of the first page:", width=20, anchor="w")
        label_url.pack(side=LEFT)
        self.entry_url = Entry(frame1, width=40)
        self.entry_url.pack(side=RIGHT)

        frame2 = Frame(main_frame, padx=5, pady=5)
        frame2.pack()
        label_tag = Label(frame2, text="Tag/key to search for:", width=20, anchor="w")
        label_tag.pack(side=LEFT)
        self.entry_tag = Entry(frame2, width=40)
        self.entry_tag.pack(side=RIGHT)

        frame3 = Frame(main_frame, padx=5, pady=5)
        frame3.pack()
        label_value = Label(frame3, text="Value to search for:", width=20, anchor="w")
        label_value.pack(side=LEFT)
        self.entry_value = Entry(frame3, width=40)
        self.entry_value.pack(side=RIGHT)

        frame4 = Frame(main_frame, padx=5, pady=5)
        frame4.pack()
        self.button_search = Button(frame4, text="Search", command=self.search)
        self.button_search.pack()

        frame5 = Frame(main_frame, padx=5, pady=5)
        frame5.pack()
        self.status = StringVar()
        self.message_status = Message(frame5, textvariable=self.status, width=2000)
        self.message_status.pack()
        self.button_open_results = Button(frame5, text="Open results in the default browser", command=self.open_results)
        self.button_open_results.pack()

    def is_valid(self):
        errors = []
        url = self.entry_url.get().strip()
        if not url:
            errors.append("URL is required, but not entered.")
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0',
            }
            try:
                response = requests.get(url, headers=headers, allow_redirects=True)
            except requests.exceptions.RequestException:
                errors.append("URL is not valid.")
                raise
            else:
                if response.status_code != requests.codes.OK:
                    errors.append("API is not accessible.")
                    print(response.status_code)

        if not self.entry_tag.get().strip():
            errors.append("Tag is required, but not entered.")
        if not self.entry_value.get().strip():
            errors.append("Value is required, but not entered.")

        if errors:
            self.status.set("\n".join(errors))
            return False

        return True

    def search(self):
        if self.is_valid():
            self.status.set("Searching...")
            self.results_queue = queue.Queue()
            self.background_thread = threading.Thread(
                target=search_for_string,
                kwargs=dict(
                    url=self.entry_url.get().strip(),
                    tag=self.entry_tag.get().strip(),
                    value=self.entry_value.get().strip(),
                    results_queue=self.results_queue,
                )
            )
            self.background_thread.start()
            self.master.after(100, self.process_queue)

    def process_queue(self):
        try:
            self.results = self.results_queue.get(0)
        except queue.Empty:
            self.master.after(100, self.process_queue)
        else:
            if self.results:
                self.status.set("API pages with the search result:\n" + "\n".join(self.results))
            else:
                self.status.set("Nothing was found.")

    def open_results(self):
        import webbrowser
        for url in self.results:
            webbrowser.open_new_tab(url)


def get_parser():
    """
    Gets argument parser of the command-line version
    :return: argument parser
    """
    _parser = argparse.ArgumentParser(description='Search for a tag and value in multiple API pages')
    _parser.add_argument('--command-line', help='Shows command line dialog',
                         dest='command_line', action='store_true')
    _parser.add_argument('--url', help='API URL for the first page')
    _parser.add_argument('--tag', help='tag to search for')
    _parser.add_argument('--value', help='value to search for', default='')
    return _parser


def command_line(arguments):
    """
    Command line execution
    """
    if arguments.command_line:
        url = raw_input("Enter API URL for the first page: ").decode("utf-8").strip()
        tag = raw_input("Enter tag/key to search for: ").decode("utf-8").strip()
        value = raw_input("Enter value to search for: ").decode("utf-8").strip()

        print("Searching...")

        results = search_for_string(url=url, tag=tag, value=value)
        if results:
            print("API pages with the search result:\n" + "\n".join(results))
        else:
            print("Nothing was found.")

        print("Finished.")

    else:
        url = arguments.url
        tag = arguments.tag
        value = arguments.value

        results = search_for_string(url=url, tag=tag, value=value)
        if results:
            print("\n".join(results))


def gui():
    """
    GUI execution
    """
    root = Tk()
    App(root)
    root.mainloop()
    exit()


def main():
    parser = get_parser()       # Start the command-line argument parsing
    args = parser.parse_args()  # Read the command-line arguments

    try:
        if args.command_line or (args.url and args.tag):   # If there is an argument,
            command_line(args)      # run the command-line version
        else:
            gui()                   # otherwise run the GUI version
    except KeyboardInterrupt:
        print("\nProgram canceled.")


if __name__ == "__main__":
    main()
