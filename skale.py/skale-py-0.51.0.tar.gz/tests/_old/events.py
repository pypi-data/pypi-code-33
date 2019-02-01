from time import sleep
from skale import Skale, EventListener

def handler(event):
  print('Event:')
  print(event)

if __name__ == '__main__':
  skale = Skale('51.0.1.99', 8546)

  event = skale.manager().contract.events.NodeCreated
  listener = EventListener(event, handler, 5)
  listener.run()

  port = 28
  ip = '15.24.32.132'
  account = skale.web3.eth.accounts[0]
  res = skale.manager().create_node(ip, port, account)

  sleep(5)
  receipt = skale.web3.eth.getTransaction(res)
  print("Receipt:")
  print(receipt)
