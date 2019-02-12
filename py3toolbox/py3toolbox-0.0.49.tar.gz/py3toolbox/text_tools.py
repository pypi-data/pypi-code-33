import os
import re
 
def re_search (re_pattern , text) :
  m = re.search(re_pattern, text)
  if m :  return m.groups
  return None

  
def re_findall (re_pattern , text) :
  m = re.findall(re_pattern, text)
  return m

def re_sub(re_pattern , text):
  return re.sub(re_pattern, text)


  
if __name__ == "__main__":
  str1 = 'product/900/162-11292V02G01'
  a = re_search('([^\/]*)$',str1)
  print (a(0)[0])
  pass  