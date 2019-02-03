from bs4 import BeautifulSoup as bs
import requests as r
def get(sub):
	page = r.get(r"http://www.primapad.com/"+sub)
	soup = bs(page.text,"html.parser")
	soup.find(id="conteudo")
	element=soup.find(id="conteudo")
	return element.contents[0]


