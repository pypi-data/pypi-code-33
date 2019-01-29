"""
Test Favourite accounts
"""



def test_favourite_accounts():
    """ Call the cli  """
    from gnucash_portfolio_cli import gpcli
    #gpcli.main("scheduled")
    gpcli.main("fav")
