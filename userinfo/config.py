import configparser
import os
import errno

config = configparser.SafeConfigParser()
config.read(["conf/ippuserinfo.conf", os.environ.get("AMR_RS_CONFIG", ""), "/etc/ipp/conf/ippuserinfo.conf"])

def get(section, option, default = None):
    """
    Reads config optoin from the given section, returning default if not found
    """
    try:
        return config.get(section, option)
    except:
        return default