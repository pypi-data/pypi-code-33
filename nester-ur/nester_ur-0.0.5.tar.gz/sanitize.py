""" Corrige a string de tempo e adota dois-pontos (:) como o padrão de separação"""

def sanitize(time_string):

  if '-' in time_string:
    splitter = '-'
  elif ':' in time_string:
    splitter = ':'
  else:
    return(time_string)

  (mins, secs) = time_string.split(splitter)

  return(mins + '.' + secs)
