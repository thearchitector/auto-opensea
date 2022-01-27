import random
import time

import orjson
from selenium.webdriver.remote.webdriver import WebDriver

from .utils import Context, _create_nft, _install_metamask, link_metamask


def OpenSeaContext(driver: WebDriver, mnemonic: str, timeout: int = 60):
    with driver:
        context = Context(driver, mnemonic, timeout)
        _install_metamask(context)

        yield context


def upload_nfts(context: Context, collection: str):
    # go to OpenSea and link MetaMask
    context.driver.get(f"https://opensea.io/collection/{collection}/assets/create")
    link_metamask(context, 3)

    # load metadata
    with open("nfts/metadata.json", "rb") as f:
        metadata = orjson.loads(f.read())

    # create all the items
    for N, data in list(metadata.items()):
        _create_nft(context, data)
        time.sleep((random.random() * 2) + 2)
        context.driver.get(f"https://opensea.io/collection/{collection}/assets/create")
