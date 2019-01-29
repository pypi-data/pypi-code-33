from distutils.core import setup

setup(
  name = 'sanic-simple-swagger',         # How you named your package folder (MyLib)
  include_package_data=True, # adding all my html
  packages = ['sanic_simple_swagger'],   # Chose the same as "name"
  package_data={'sanic_simple_swagger': ['ui/*']},
  version = '0.0.9',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  long_description=
  '''
    # Sanic OpenAPI
    Real project in [https://github.com/huge-success/sanic-openapi](https://github.com/huge-success/sanic-openapi/blob/master/README.md)

    This project just extends functional and fix some bugs
    ![Example Swagger UI](https://raw.githubusercontent.com/huge-success/sanic-openapi/master/images/code-to-ui.png "Swagger UI")

    #[Git Documentation](https://github.com/FerdinaKusumah/sanic_simple_swagger)

    ## Installation
    ```shell
    pip install sanic-simple-swagger
    ```

    #### Add OpenAPI and Swagger UI:
    ```python
    from sanic_simple_swagger import swagger_blueprint, openapi_blueprint
    app.blueprint(openapi_blueprint)
    app.blueprint(swagger_blueprint)
    ```

    You'll now have a Swagger UI at the URL `/swagger/index.html`.

    Your routes will be automatically categorized by their blueprints.

    ### Configure all the things

    ```python
    app.config['API_VERSION'] = '1.0.0'
    app.config['API_TITLE'] = 'Swagger Petstore'
    app.config['API_DESCRIPTION'] = 'This is a sample server Petstore server. You can find out more about Swagger at [http://swagger.io](http://swagger.io) or on [irc.freenode.net, #swagger](http://swagger.io/irc/). For this sample, you can use the api key `special-key` to test the authorization filters.'
    app.config['API_TERMS_OF_SERVICE'] = 'http://swagger.io/terms/'
    app.config['API_CONTACT_EMAIL'] = 'http://swagger.io/terms/'
    app.config['API_LICENSE_NAME'] = 'Apache 2.0'
    app.config['API_LICENSE_URL'] = 'http://www.apache.org/licenses/LICENSE-2.0.html'
    app.config['schemes'] = ['http', 'https']
    ```

    ## Reference
    1. [Sanic](https://github.com/huge-success/sanic)
    2. [Sanic OpenAPI](https://github.com/huge-success/sanic-openapi)
  ''',
  long_description_content_type='text/markdown',
  description = 'Swagger UI for Python web framework Sanic.',   # Give a short description about your library
  author = 'Ferdina kusumah',                   # Type in your name
  author_email = 'ferdina.kusumah@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/FerdinaKusumah/sanic_simple_swagger',   # Provide either the link to your github or to your website
  keywords = ['sanic swagger', 'python sanic swagger', 'sanic openapi', 'sanic simple swagger'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)