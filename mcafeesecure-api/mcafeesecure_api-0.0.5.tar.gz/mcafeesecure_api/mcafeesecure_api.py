# Imports
import requests
import os

# API Key Configuration
api_key = ''

# Basic API Key Verification
if len(api_key) != 36:
    print('API Key Missing or Incorrect: Please check ' + os.path.dirname(os.path.abspath(__file__)) + ' to edit the API Key')

# Methods
def account_create(company_name, user_first_name, user_last_name, user_phone,
                    user_email, payment_type):
    """Create a new account the initially consists of a company and user.

    This method requires the 'reseller' permission.

    Args:
        comapny_name (str): Replacement parameter for reseller company.
        user_first_name (str): First name of account owner.
        user_last_name (str): Last name of account owner.
        user_phone (str): Contact number for account.
        user_email (str): Contact email for account.
        payment_type (int): Contact developer for more information.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-account-create
    """    

    headers = {
        'x-apikey': api_key
    }

    params = {
        'company.name': company_name,
        'user.firstName': user_first_name,
        'user.lastName': user_last_name,
        'user.phone': user_phone,
        'user.email': user_email,
        'paymentType': payment_type
    }

    return requests.get('https://api.mcafeesecure.com/api/v1/account-create.json?', headers=headers, params=params).text


def account_create_lite(email, host, *args, **kwargs):
    """Create a new account or add a site to an existing account.

    Args:
        -Required-
        email (str): New user email.
        host (str): New site hostname.

        -Optional-
        first_name (str): First name of user.
        last_name (str): Last name of user.
        phone (str): Contact number for user.
        company_name (str): Company name for new user.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-account-create-lite

    Example on how to use Optional Parameters:
        account_create_lite('test@gmail.com','www.mcafeesecure.com', first_name='John',
                                last_name='Smith', ... )
    """  

    headers = {
        'x-apikey': api_key
    }

    params = {
        'email': email,
        'host': host,
        'firstName': kwargs.get('first_name', None),
        'lastName': kwargs.get('last_name', None),
        'phone': kwargs.get('phone', None),
        'companyName': kwargs.get('company_name', None)
    }       

    return requests.get('https://api.mcafeesecure.com/api/v1/account-create-lite.json?', headers=headers, params=params).text


def site_add(*args, **krawgs):
    """Unclear at this time.

    Args:
        -Optional-
        subscription_id (int): Subscription ID.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-site-add

    """     

    headers = {
        'x-apikey': api_key
    }

    params = {
        'subscriptionId': krawgs.get('subscription_id', None)
    } 

    return requests.get('https://api.mcafeesecure.com/api/v1/site-add.json?', headers=headers, params=params).text


def site_update():
    """Unclear at this time.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-site-update

    """

    headers = {
        'x-apikey': api_key
    }

    return requests.get('https://api.mcafeesecure.com/api/v1/site-update.json?', headers=headers).text


def site_get(site_id):
    """Returns the hostname of the requested site ID.

    Args:
        site_id (int): McAfee SECURE Site ID.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-site-get

    """    
    headers = {
        'x-apikey': api_key
    }

    params = {
        'siteId': site_id
    } 

    return requests.get('https://api.mcafeesecure.com/api/v1/site-get.json?', headers=headers, params=params).text


def site_delete(site_id):
    """Deletes the requested site ID.

    Args:
        site_id (int): McAfee SECURE Site ID.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-site-delete

    """     

    headers = {
        'x-apikey': api_key
    }

    params = {
        'siteId': site_id
    } 

    return requests.get('https://api.mcafeesecure.com/api/v1/site-delete.json?', headers=headers, params=params).text


def site_lookup(url):
    """Unclear at this time. Method unfinished.

    Args:
        url (str): Host URL.

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-site-lookup
    """

    return

def subscription_list():
    """Method unfinished.

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-subscription-list
    """

    return

def subscription_add():
    """Method unfinished.

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-subscription-add
    """

    return


def user_add():
    """Method unfinished.

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-user-add
    """

    return


def company_get():
    """Method unfinished.

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-company-get
    """

    return

def sso(user_id):
    """Unclear. Create a Single Sign On (SSO) URL.

    Args:
        user_id (int): User ID.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-sso

    * This method requires the 'sso' permission.
    """
    headers = {
        'x-apikey': api_key
    }

    params = {
        'userID': user_id
    } 

    return requests.get('https://api.mcafeesecure.com/api/v1/sso.json?', headers=headers, params=params).text      


def scan_targets():
    """Return information about current scan targets.

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-scan-targets
    """

    headers = {
        'x-apikey': api_key
    }

    return requests.get('https://api.mcafeesecure.com/api/v1/scan-targets.json?', headers=headers).text


def scan_target(target_id):
    """Return information about a specific scan target.

    Args:
        target_id (int): The 5 digit McAfee SECURE target ID

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-scan-target
    """

    headers = {
        'x-apikey': api_key
    }

    params = {
        'targetId': target_id
    }

    return requests.get('https://api.mcafeesecure.com/api/v1/scan-target.json?', headers=headers, params=params).text


def scan_result(target_id, scan_id):
    """Return information about the results of a target's scan.

    Args:
        target_id (int): The 5 digit McAfee SECURE target ID
        scan_id (str): The 32 alphanumerical string of a Scan ID

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-scan-result
    """

    headers = {
        'x-apikey': api_key
    }

    params = {
        'targetId': target_id,
        'scanId': scan_id
    }

    return requests.get('https://api.mcafeesecure.com/api/v1/scan-result.json?', headers=headers, params=params).text


def scan_vuln(vuln_id):
    """Return information about a specific vulnerability.

    Args:
        vuln_id (int): The McAfee SECURE 7 digit Vulnerability ID Number

    Returns:
        'utf-8' encoded JSON response

    More Information:
        https://www.mcafeesecure.com/user/support/api/#method-scan-vuln
    """

    headers = {
        'x-apikey': api_key
    }

    params = {
        'vulnId': vuln_id
    }

    return requests.get('https://api.mcafeesecure.com/api/v1/scan-vuln.json?', headers=headers, params=params).text
