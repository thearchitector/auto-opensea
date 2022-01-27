import os
import time

from seacaptain import Context
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


def test_context():
    service = Service(executable_path=GeckoDriverManager().install())
    with Context(webdriver.Firefox(service=service)) as c:
        assert not hasattr(c, "mnemonic")
        time.sleep(5)
