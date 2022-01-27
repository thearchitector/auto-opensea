import secrets
from pathlib import Path
from typing import Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ADDON_PATH = Path(__file__, "../lib", "metamask-10.8.1-an+fx").resolve()


class Context:
    """A context object for holding common objects."""

    def __init__(self, driver: WebDriver, mnemonic: str, timeout: int):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.original_window = driver.current_window_handle
        self.mnemonic = mnemonic

        driver.maximize_window()

    def wait_until_present(self, method: By, selector: str, many=False):
        """
        Instructs the driver to wait until the element(s) can by found by the given
        method and selector.
        """
        if many:
            return self.wait.until(lambda d: d.find_elements(method, selector))

        return self.wait.until(lambda d: d.find_element(method, selector))

    def switch_to_metamask(self):
        """Switches the driver context to the new window (will be MetaMask)."""
        self.wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != self.original_window:
                self.driver.switch_to.window(window_handle)
                break

    def switch_to_original(self, close=False):
        """
        Switches the driver context to the original window, optionally closing the
        current window beforehand.
        """
        if close:
            self.driver.close()

        self.driver.switch_to.window(self.original_window)


def _install_metamask(context: Context):
    """
    Installs MetaMask into the current browser context, and initializes the wallet
    using the given mnemonic. Passwords are cryptoraphically-secure generated tokens.
    """
    # install the addon
    context.driver.install_addon(ADDON_PATH, temporary=True)
    context.switch_to_metamask()

    # navigate through the onboarding pages
    context.wait_until_present(By.TAG_NAME, "button").click()
    context.wait_until_present(By.TAG_NAME, "button").click()
    context.wait_until_present(By.TAG_NAME, "button").click()

    # fill out the account recovery and setup the wallet
    fields = context.wait_until_present(By.TAG_NAME, "input", many=True)
    password = secrets.token_hex()
    fields[0].send_keys(context.mnemonic)
    del context.mnemonic
    fields[1].send_keys(password)
    fields[2].send_keys(password)
    context.wait_until_present(By.CLASS_NAME, "first-time-flow__terms").click()
    context.wait_until_present(By.TAG_NAME, "button").click()
    context.wait_until_present(By.CLASS_NAME, "end-of-flow__emoji")
    context.wait_until_present(By.TAG_NAME, "button").click()

    # switch to the original tab, closing the current
    context.switch_to_original(close=True)


def link_metamask(context: Context, num_agreements: int):
    """Links MetaMask to OpenSea."""
    # link your metamask account
    context.wait_until_present(
        By.CLASS_NAME, "ConnectCompatibleWallet--show-more"
    ).click()
    options = context.wait_until_present(
        By.CSS_SELECTOR, "ul.ConnectCompatibleWallet--wallet-list li", many=True
    )

    for o in options:
        if "MetaMask" in o.text:
            o.click()
            break
    context.switch_to_metamask()

    # accept all and switch back
    for _ in range(num_agreements):
        context.wait_until_present(By.TAG_NAME, "button", many=True)[1].click()
    context.switch_to_original()


def _create_nft(context: Context, data: Dict[str, str]):
    """
    Fills in the information and property metadata for the given NFT, returning the URL
    to track uploaded asset addresses.
    """
    # fill in basic information
    context.wait_until_present(By.ID, "media").send_keys(data["media"])
    context.wait_until_present(By.ID, "name").send_keys(data["name"])
    del data["media"]
    del data["name"]

    # create prop fields
    context.wait_until_present(By.CSS_SELECTOR, '[aria-label="Add properties"]').click()
    n_prop = context.wait_until_present(
        By.CSS_SELECTOR, '[role="dialog"] section > button'
    )
    [n_prop.click() for _ in range(len(data) - 1)]

    # fill prop fields with metadata
    p_names = context.driver.find_elements(
        By.CSS_SELECTOR,
        '[role="dialog"] section table [aria-label="Provide the property name"]',
    )
    p_vals = context.driver.find_elements(
        By.CSS_SELECTOR,
        '[role="dialog"] section table [aria-label="Provide the property value"]',
    )
    for (n, v), (p, pv) in zip(zip(p_names, p_vals), data.items()):
        n.send_keys(p)
        v.send_keys(pv)
    context.driver.find_element(
        By.CSS_SELECTOR, '[role="dialog"] footer > button'
    ).click()

    # upload!
    context.driver.find_element(By.CSS_SELECTOR, ".AssetForm--action button").click()
    context.wait_until_present(By.CLASS_NAME, "AssetSuccessModalContent--share-cta")
    return context.driver.current_url
