import setuptools

setuptools.setup(
    name='mail_notifier',
    version='0.0.5',
    url='http://git.shookai.com/team-black/shk-lib-notifier.git',
    author_email='bartlomiej.tyniewicki@shookai.com',
    description='Sending notification via SMTP',
    packages=["mail_notifier"],
    package_data={'html_template.txt': ['*']},
    include_package_data=True,
)
