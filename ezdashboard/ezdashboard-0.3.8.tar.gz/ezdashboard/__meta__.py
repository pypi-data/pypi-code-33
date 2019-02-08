
__name__ = 'ezdashboard'
name_url = __name__.replace('_', '-')

__version__ = '0.3.8'

__description__ = 'Easy dashboard creaation from raw HTML components'
__author__ = 'oscar6echo'
__author_email__ = 'olivier.borderies@sgcib.com'
__url__ = 'https://gitlab.com/oscar6echo/{}'.format(name_url)
__download_url__ = 'https://gitlab.com/oscar6echo/{}/repository/archive.tar.gz?ref={}'.format(
    name_url,
    __version__)
__keywords__ = ['python', 'dashboard', 'jinja', 'html', 'js', 'css']
__license__ = 'MIT'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'
                   ]
__include_package_data__ = True
__package_data__ = {
    'templates': [
        'templates/*.html',
        'templates/*.css'
    ]
}
__zip_safe__ = False
__entry_points__ = {}
