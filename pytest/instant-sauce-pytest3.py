# In the following examples we implement the pytest and seleniumbase test frameworks
# pytest docs: https://docs.pytest.org/en/latest/contents.html
# seleniumbase docs: https://github.com/seleniumbase/SeleniumBase
import pytest
import os
from selenium import webdriver
from _pytest.runner import runtestprotocol
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@pytest.fixture
def driver(request):
    sauce_username = os.environ["SAUCE_USERNAME"]
    sauce_access_key = os.environ["SAUCE_ACCESS_KEY"]
    remote_url = "https://ondemand.saucelabs.com:443/wd/hub"
    # use sauce:options to handle all saucelabs.com-specific capabilities such as:
    # username, accesskey, build number, test name, timeouts etc.
    sauceOptions = {
        "screenResolution": "1280x768",
        "seleniumVersion": "3.141.59",
        'name': 'Example Pytest3',
        "username": sauce_username,
        "accessKey": sauce_access_key
    }
    # In ChromeOpts, we define browser and/or WebDriver capabilities such as
    # the browser name, browser version, platform name, platform version
    chromeOpts =  {
        'platformName':"Windows 10",
        'browserName': "chrome",
        'browserVersion': '71.0',
        'goog:chromeOptions': {'w3c': True},
        'sauce:options': sauceOptions
    }

    browser = webdriver.Remote(remote_url, desired_capabilities=chromeOpts)
    yield browser
    browser.quit()
# Here we use a test runner method to handle all postrequisite test execution steps such as:
# sending the test results to saucelabs.com and tearing down the current WebDriver (browser) session
def pytest_runtest_protocol(item, nextitem, driver):
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            # In this if statement the script uses the seleniumbase test framework JS executor command
            # to send the results to saucelabs.com
            # For more information consult the documentation: https://pypi.org/project/seleniumbase/
            driver.execute_script('sauce:job-result={}'.format(report.outcome))
    return True

# Here is our actual test code. In this test we open the saucedemo app in chrome and assert that the title is correct.
def test_should_open_chrome(driver):
    driver.get("http://www.saucedemo.com")
    actual_title = driver.title
    expected_title = "Swag Labs"
    assert expected_title == actual_title