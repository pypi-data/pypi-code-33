from os.path import join

def new_profile(user_agent):
    profile = webdriver.FirefoxProfile()
    profile.add_extension('/tools/firefox/JSErrorCollector.xpi')
    profile.set_preference('app.update.auto', False)
    profile.set_preference('app.update.enabled', False)
    profile.set_preference("general.useragent.override", user_agent)

    return profile

def new_driver(profile):

    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)

    firefox_path = '/tools/firefox/firefox'
    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True
    caps['acceptSslCerts'] = True

    binary = FirefoxBinary(firefox_path)

    return webdriver.Firefox(profile, capabilities=caps, log_path="{0}/firefox.log".format(LOG_DIR),
                             firefox_binary=binary, executable_path='/tools/geckodriver/geckodriver')


def screenshots(driver, screenshot_dir, name):
 
    driver.get_screenshot_as_file(join(screenshot_dir, '{0}.png'.format(name)))
  
    with open(join(screenshot_dir, '{0}.html.log'.format(name)), "w") as f:
        f.write(driver.page_source.encode("utf-8"))
   
    with open(join(screenshot_dir, '{0}.js.log'.format(name)), "w") as f:
        try:
            f.write(str(driver.execute_script('return window.JSErrorCollector_errors ? window.JSErrorCollector_errors.pump() : []')))
        except WebDriverException, e:
            print("unable to get js errors: {0}".format(e))
   
