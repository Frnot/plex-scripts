"""Billboard top 40 pop playlist generator"""

from dotenv import dotenv_values

import plexapi
from plexapi.server import PlexServer


env = dotenv_values(".env")

plex = PlexServer(env["plexAddress"], env["authTokenId"])

print()