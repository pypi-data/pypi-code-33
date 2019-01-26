import datamode.settings

def _jupyter_nbextension_paths():
  print ('in _jupyter_nbextension_paths')
  return [{
    'section': 'notebook',
    'src': 'dist',
    'dest': 'features_react',
    'require': 'features_react/index'
  }]
