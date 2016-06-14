# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import ConfigParser

class Config:
    def __init__(self, cfg):
        """@param cfg: configuration file."""
        config = json.load(open(cfg))
        for section in config:
            for name in config[section]:
                value = config[section][name]
                # Options can be UTF encoded.
                if isinstance(value, basestring):
                    try:
                        value = value.encode("utf-8")
                    except UnicodeEncodeError:
                        pass
                setattr(self, name, value)


    def get(self, name, default=None):
        if hasattr(self, name):
            return getattr(self, name)
        return default

    def get_options(self):
        """Get analysis options.
        @return: options dict.
        """
        options = {}
        if hasattr(self, "options"):
            return self.options

        return options
