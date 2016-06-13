# Copyright (C) 2010-2013 Claudio Guarnieri.
# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import json
import ConfigParser

class Config:
    def __init__(self, cfg):
        """@param cfg: configuration file."""
        config = json.load(open(cfg))
        for section in config:
            for name in config[section]:
                setattr(self, name, config[section][name])

    def parse_options(self, options):
        """Get analysis options.
        @return: options dict.
        """
        return json.loads(options)
