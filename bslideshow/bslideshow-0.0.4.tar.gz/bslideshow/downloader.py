#!/usr/bin/env python2.7
#coding:utf-8

#Split video (desde segundo 184 y dura 7 segundos)
#ffmpeg -i thirds.mp4 -ss 184 -t 7 t1.mp4

#Scalar video
#ffmpeg -i video_1920.mp4 -vf scale=640:360 video_640.mp4 -hide_banner

#Convertir video en imágenes
#ffmpeg -i thirds.mp4 -vsync 0 out%d.png

#Plantillas posibles para lower thirds
'''

[sellt6]: https://www.youtube.com/watch?v=1j2SdLcKX8I&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=155
[sellt5]: https://www.youtube.com/watch?v=mdn-x5UW_9E&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=151
[sellt4]: https://www.youtube.com/watch?v=Rdl4TUVQMpw&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=149
[sellt3]: https://www.youtube.com/watch?v=QC0QjW2EWEo&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r&index=120
[sellt2]: https://www.youtube.com/watch?v=7ghdipr6d9w&index=105&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r

[sellt1]: https://www.youtube.com/watch?v=zpvpUrsCne8&index=13&list=PLPxLHRwHzxIRMrKy08_azqvmfZeeqHK6r

https://mega.nz/#F!LD5zRAwK!dgkpxG7HT9Lw6ANe7ro9Ug

'''

import sys
import subprocess
import tempfile
import os
import requests
import tarfile
import sbrowser
import selenium

DOWNLOADER_URL = 'https://mega.nz/#F!LD5zRAwK!dgkpxG7HT9Lw6ANe7ro9Ug'

class Downloader:

  def __init__ (self):
    #self.test = False
    pass

  def downloadFile (self, folderName, name, outputFolder=None):
    result = None
    #arrayPath = path.split(os.sep)
    #folderName = arrayPath[0]
    #name = arrayPath[1]

    #downloadDir = '/home/jmramoss/Descargas/periquito'

    b = sbrowser.Browser()
    #b.openUrl(DOWNLOADER_URL, downloadDir=downloadDir).maximize()
    b.openUrl(DOWNLOADER_URL).maximize()
    b.wait(10)

    #downloadDir = '/home/jmramoss/Descargas/pqqq'
    outputFolder = b.getDefaultDownloadDir() if outputFolder is None else outputFolder
    b.changeDownloadDir(outputFolder)

    btnListView = "//a[contains(@class, 'fm-files-view-icon') and contains(@class, 'listing-view')]"
    b.click(btnListView)

    #//div[contains(@class,'content-panel cloud-drive')]//ul[@class='opened']//li//span[text()='samples']
    folder = "//div[contains(@class,'content-panel cloud-drive')]//ul[@class='opened']//li//span[text()='" + folderName + "']"
    b.wait(5).click(folder).wait(5).click(btnListView)

    files = "//table[contains(@class, 'fm megaListContainer')]//tr[contains(@class, 'file megaListItem')]"
    #b.processItems(files, self.fnDownloadFolderFile)
    
    searchFile = files + "//span[@class='tranfer-filetype-txt'][.='" + name + "']/ancestor::tr"
    if b.exists(searchFile):
      b.wait(5).click(searchFile)
      openMenu = searchFile + "//a[@class='grid-url-arrow']"
      b.wait(5).click(openMenu)

      btnDownload = "//a[contains(@class,'dropdown-item download-item')][contains(., 'Descargar')]"
      b.wait(5).click(btnDownload).wait(40)
      
      result = os.path.join(outputFolder, name)
      
    return result
  
  def fnDownloadFolderFile (self, browser, element):
    print("download e1")
    browser.pushPivot(element)
    
    browser.wait(5).click(element)
    openMenu = "//a[@class='grid-url-arrow']"
    browser.wait(5).click(openMenu)

    browser.popPivot()

    btnDownload = "//a[contains(@class,'dropdown-item download-item')][contains(., 'Descargar')]"
    browser.wait(5).click(btnDownload)
  
  def listFolder (self, folderName):
    result = list()
    b = sbrowser.Browser()
    b.openUrl(DOWNLOADER_URL).maximize()
    b.wait(10)

    #b.click("//a[contains(@class, 'fm-files-view-icon') and contains(@class, 'block-view')]")
    #b.wait(10)
    btnListView = "//a[contains(@class, 'fm-files-view-icon') and contains(@class, 'listing-view')]"
    b.click(btnListView)

    #//div[contains(@class,'content-panel cloud-drive')]//ul[@class='opened']//li//span[text()='samples']
    folder = "//div[contains(@class,'content-panel cloud-drive')]//ul[@class='opened']//li//span[text()='" + folderName + "']"
    b.wait(5).click(folder).wait(5).click(btnListView)

    files = "//table[contains(@class, 'fm megaListContainer')]//tr[contains(@class, 'file megaListItem')]"
    #b.processItems(files, self.fnDownloadFolderFile)
    
    numfiles = len(b.listElements(files))
    for i in range(1, numfiles+1):
      efile = files + "[" + str(i) + "]"
      efileName = efile + "//span[@class='tranfer-filetype-txt']"
      
      nameTxt = b.attr(efileName, 'innerText')
      result.append(nameTxt)
    
    return result
  
  def downloadFolder (self, folderName):
    b = sbrowser.Browser()
    b.openUrl(DOWNLOADER_URL, downloadDir='/home/jmramoss/Descargas/periquito').maximize()
    b.wait(10)

    #b.click("//a[contains(@class, 'fm-files-view-icon') and contains(@class, 'block-view')]")
    #b.wait(10)
    btnListView = "//a[contains(@class, 'fm-files-view-icon') and contains(@class, 'listing-view')]"
    b.click(btnListView)

    #//div[contains(@class,'content-panel cloud-drive')]//ul[@class='opened']//li//span[text()='samples']
    folderSamples = "//div[contains(@class,'content-panel cloud-drive')]//ul[@class='opened']//li//span[text()='" + folderName + "']"
    b.wait(5).click(folderSamples).wait(5).click(btnListView)

    '''
    //table[contains(@class, 'fm megaListContainer')]
    //table[contains(@class, 'fm megaListContainer')]//tr[contains(@class, 'file megaListItem')]
    //table[contains(@class, 'fm megaListContainer')]//tr[1]//a[@class='grid-url-arrow']
    '''

    
    files = "//table[contains(@class, 'fm megaListContainer')]//tr[contains(@class, 'file megaListItem')]"
    #b.processItems(files, self.fnDownloadFolderFile)
    
    numfiles = len(b.listElements(files))
    for i in range(1, numfiles+1):
      efile = files + "[" + str(i) + "]"
      b.wait(5).click(efile)
      openMenu = efile + "//a[@class='grid-url-arrow']"
      b.wait(5).click(openMenu)

      btnDownload = "//a[contains(@class,'dropdown-item download-item')][contains(., 'Descargar')]"
      b.wait(5).click(btnDownload).wait(40)
    
    '''
    b.wait(5).click(firstFile)
    openMenu = "//table[contains(@class, 'fm megaListContainer')]//tr[3]//a[@class='grid-url-arrow']"
    b.wait(5).click(openMenu)

    btnDownload = "//a[contains(@class,'dropdown-item download-item')][contains(., 'Descargar')]"
    b.wait(5).click(btnDownload)
    '''
    #b.close()

    
if True and __name__ == '__main__':
  tools = Downloader()
  #tools.downloadFolder("transitions")
  #print(str(tools.listFolder("transitions")))
  print(str(tools.downloadFile("transitions", "transition1.mp4")))
