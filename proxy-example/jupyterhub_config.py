# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()  # noqa: F821

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Spawn containers from this image
c.DockerSpawner.image = os.environ["DOCKER_NOTEBOOK_IMAGE"]

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most `jupyter/docker-stacks` *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {
        "jupyterhub-user-{username}": notebook_dir,
        "/mnt/jupyter-data/{username}": "/home/jovyan/work/hive2-jupyter-data/{username}",
}

c.DockerSpawner.read_only_volumes = {
        "/mnt/jupyter-data/": "/home/jovyan/work/hive2-jupyter-data",
        "/mnt/tim-data/": "/home/jovyan/work/hive1-tim-data",
}

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = 8080

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

from secrets import compare_digest
from traitlets import Dict
from jupyterhub.auth import Authenticator


class DictionaryAuthenticator(Authenticator):

    passwords = {}

    async def authenticate(self, handler, data):
        username = data["username"]
        password = data["password"]
        check_password = self.passwords.get(username, "")
        # always call compare_digest, for timing attacks
        if compare_digest(check_password, password) and username in self.passwords:
            return username
        else:
            return None

import fileinput
for line in fileinput.input("passwd"):
    a, b, *ignore = line.split("\t")
    DictionaryAuthenticator.passwords[a] = b

c.JupyterHub.authenticator_class = DictionaryAuthenticator
c.Authenticator.admin_users = ["moorejo", "boissoto"]
c.Authenticator.allow_all = True

# Not working
c.CondaKernelSpecManager.name_format = "{language} [{environment}]"


# shutdown the server after no activity for an hour
# c.ServerApp.shutdown_no_activity_timeout = 60 * 60
# shutdown kernels after no activity for 20 minutes
c.MappingKernelManager.cull_idle_timeout = 20 * 60
# check for idle kernels every two minutes
c.MappingKernelManager.cull_interval = 2 * 60
