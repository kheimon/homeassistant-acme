#!/usr/bin/env python3

# acme.sHomeassistant - A homeassistant add-on wrapper for acme.sh
# Copyright (C) 2025  hupf

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from pathlib import Path
import logging
from acme_client import AcmeClient
from utils import setup_logging
from config import load_config
import sys

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    
    try:
        logger.info("Loading configuration...")
        config = load_config(Path("/data/options.json"), Path("/ssl"))
        dns_env_vars = {env.name: env.value for env in config.dnsEnvVariables} or None
        acme_config_home = Path("/data/acme.sh")
    except Exception:
        logger.exception(f"Invalid or empty config!")
        sys.exit(1)
    
    try:
        logger.info("Preparing required directories for acme client...")
        acme_config_home.mkdir(parents=True, exist_ok=True)
        config.domain_ssl_dir.mkdir(parents=True, exist_ok=True)
    except:
        logger.exception(f"Could not create required directories!")
        sys.exit(1)
    
    try:
        logger.info("Starting acme client...")
        acme_client = AcmeClient(acme_config_home)
        acme_client.enable_auto_upgrade()
        # acme_client.enable_cronjob()
        acme_client.register(config.accountemail, config.server)
        acme_client.issue(config.domains, config.keylength, config.server, config.dns, dns_env_vars)
        acme_client.install(config.domains, config.keylength, config.key_path, config.fullchain_path)
    except Exception:
        logger.exception(f"Acme client failure!")
        sys.exit(1)

if __name__ == "__main__":
    main()