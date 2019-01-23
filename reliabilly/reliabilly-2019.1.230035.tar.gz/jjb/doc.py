# flake8: noqa
# pylint: disable=trailing-whitespace
"""
@api get /jjb/
description: Returns all jjb
summary: Fetch all jjb
tags:
    - jjb
parameters:
    - name: limit
      in: query
      description: The maximum number of jjb to fetch
      schema:
        type: integer
    - name: offset
      in: query
      description: The number of jjb to offset your query by
      schema:
        type: integer
responses:
    "200":
        description: A list of jjb items
    "400":
        description: The request was badly formed or otherwise invalid
    "403":
        description: The auth token was invalid or not provided
"""

"""
@api post /jjb/
description: >-
    Submit a new jjb item to the service. Do note that not
    all services necessarily support the addition of new items. If it doesn't,
    it shouldn't have this entry but as the documentation is generated,
    the creator may have forgotten this segment.
summary: Add a new  item to the service
tags:
    - jjb
responses:
    "201":
        description: Successfully submitted the new jjb item
    "400":
        description: The request was badly formed or otherwise invalid
    "403":
        description: The auth token was invalid or not provided
"""

"""
@api get /jjb/{id}
description: Fetch a single jjb item by ID
summary: Fetch a single jjb item by ID
tags:
    - jjb
responses:
    "200":
        description: Successfully retrieved item
    "403":
        description: The auth token was invalid or not provided
    "500":
        description: The ID provided is invalid
"""

"""
@api put /jjb/{id}
description: Update a jjb item in the service
summary: Update a jjb item in the service
tags:
    - jjb
responses:
    "202":
        description: A success message
    "400":
        description: The request was badly formed or otherwise invalid
    "403":
        description: The auth token was invalid or not provided
    "404":
        description: The item was not found. It was deleted or never existed.
"""

"""
@api delete /jjb/{id}
description: Delete a jjb item from the service
summary: Delete a jjb item from the service
tags:
    - jjb
responses:
    "200":
        description: The item was successfully deleted
    "403":
        description: The auth token was invalid or not provided
    "404":
        description: The item was not found. It was deleted or never existed.
"""

"""
@api get /jjb/collect/
description: >-
    Performing a GET on the /collect/ endpoint will show any
    currently running collections that have been manually triggered.
    You can see which collector is running and when it was started.
summary: View currently running collections
tags:
    - jjb
responses:
    "200":
        description: A JSON object containing the status of active collectors
    "403":
        description: The auth token was invalid or not provided
"""

"""
@api post /jjb/collect/
description: >-
    Triggers a manual collection for the jjb service. You
    don't need to do this as services will manually run collections at regular
    intervals but it can be useful if you 100% fresh data.
summary: Fetch the latest jjb data
tags:
    - jjb
responses:
    "202":
        description: A success message stating "Collection received!"
    "403":
        description: The auth token was invalid or not provided
"""

"""
@api post /jjb/purge/
description: Purges all jjb from the service
summary: Purge all data from the jjb service
tags:
    - jjb
responses:
    "200":
        description: The purge was successful
    "403":
        description: The auth token was invalid or not provided
"""

"""
@api get /jjb/ping/
description: Returns a success code if the service is available
summary: Ping the jjb service
tags:
    - jjb
responses:
    "200":
        description: The string "pong" indicating the request succeeded
    "403":
        description: The auth token was invalid or not provided
"""


"""
@api get /jjb/count/
description: See how many jjb are stored in the service
summary: See how many jjb are stored in the service
tags:
    - jjb
responses:
    "200":
        description: An integer reflecting the total number of jjb
    "403":
        description: The auth token was invalid or not provided
"""

"""
@api get /jjb/version/
description: Check the current version of the jjb service
summary: Check the current version of the jjb service
tags:
    - jjb
responses:
    "200":
        description: A JSON object showing version and build number
    "403":
        description: The auth token was invalid or not provided
"""
