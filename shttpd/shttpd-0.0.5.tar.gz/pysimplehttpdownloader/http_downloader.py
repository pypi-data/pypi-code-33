# -*- coding: utf-8 -*-

import sys
import urllib.request
import os.path


class HTTPDownloader(object):

    def __init__(self, url=None, output_path="", output_name=None):
        self.__url = url
        self.__output_path = output_path
        self.__output_name = output_name

    # https://stackoverflow.com/a/13895723
    @staticmethod
    def __reporthook__(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if readsofar > totalsize:
            readsofar = totalsize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            s = "\r%5.1f%% %*d / %d" % (
                percent, len(str(totalsize)), readsofar, totalsize)
            sys.stderr.write(s)
            if readsofar >= totalsize:  # near the end
                sys.stderr.write("\n")
        else:  # total size is unknown
            sys.stderr.write("read %d\n" % (readsofar,))

    def run(self):
        __filename, __headers = urllib.request.urlretrieve(
            self.__url,
            filename=os.path.join(self.__output_path,
                                  (self.__output_name if self.__output_name else self.__url.split("/")[-1])
                                  ),
            reporthook=self.__reporthook__)
        return __filename, __headers


if __name__ == "__main__":
    print("download start!")
    downloader = HTTPDownloader(
        "https://raw.githubusercontent.com/RDCH106/i-love-firefox/183266a9/I_Love_Firefox_220x56.png"
    )
    filename, headers = downloader.run()
    print("download complete!")
    print("download file location: ", filename)
    print("download headers: ", headers)
