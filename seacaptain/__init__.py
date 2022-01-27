import random
import time

import orjson

from .utils import Context, _create_nft, link_metamask


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


__all__ = ["Context", "upload_nfts", "link_metamask"]
