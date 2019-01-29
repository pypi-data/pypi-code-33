from jupyter_react import Component

# This lets us load the React component 'DatamodeApp', specified in module 'DatamodeApp.js'.
# When an instance of this class is passed to IPython.display, it sends a comm message via the kernel
# to the jupyter-react-js kernel listener, which then displays the component.
class DatamodeApp(Component):
  module = 'DatamodeApp'

  def __init__(self, handler=None, **kwargs):
    self.handler = handler
    super().__init__(target_name='react.featuresapp', **kwargs)
    self.on_msg(self._handle_msg)

  def _handle_msg(self, msg):
    # print() doesn't work here since this is received in the kernel shell channel,
    # but if you really need to debug, you can raise an Exception and it will be printed in the Jupyter terminal output.
    # raise Exception(msg)

    if self.handler:
      self.handler(self.comm, msg)
