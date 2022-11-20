"""
Built-in functions used in YAML/JSON testcases.
"""

import datetime
import calendar
import hashlib
import platform
import random
import string
import time
import os

from datetime import date, timedelta
from httprunner.compat import builtin_str, integer_types
from httprunner.exceptions import ParamsError
from httprunner.loader.load import _load_json_file, load_dot_env_file
from httprunner.utils import get_os_environ


def gen_random_string(str_len):
    """ generate random string with specified length
    """
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len))


def get_timestamp(str_len=13):
    """ get timestamp string, length can only between 0 and 16
    """
    if isinstance(str_len, integer_types) and 0 < str_len < 17:
        return str(time.time()).replace(".", "")[:str_len]

    raise ParamsError("timestamp length can only between 0 and 16.")


def get_current_date(fmt="%Y-%m-%d"):
    """ get current date, default format is %Y-%m-%d
    """
    return datetime.datetime.now().strftime(fmt)


def sleep(n_secs):
    """ sleep n seconds
    """
    time.sleep(n_secs)


def custom_random_number(num=8):
    """
        An 8-bit random integer
    :param num:
    :return:
    """
    return int(''.join(str(random.choice(range(10))) for _ in range(num))) if num == 8 \
        else ''.join(str(random.choice(range(10))) for _ in range(num))


def get_timestamp(stamp=None):
    """
        Get the current timestamp.
    :return:
    """
    return int(round(time.time() * 1000)) if stamp is None else calendar.timegm(time.gmtime())


def get_current_time(days=0, FORMAT=False):
    """
        0= today, 1= tomorrow, -1= yesterday
    :param FORMAT:
    :param days: Gets the corresponding date according to the pass parameter
    :return: 2019-10-10 10:56:58
    """

    day = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
    days = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return day if not FORMAT else days


def get_buffered_reader(file_path):
    """
        use BufferedReader because it passes the file object
    :param file_path: relative path
    :return: BufferedReader
    """
    return open(file_path, 'rb')


def md5_encrypt_psw(psw, salt=''):
    """
        MD5-encrypted password.
    :param psw:  str psw
    :param salt:
    :return:
    """
    has = hashlib.md5()
    has.update((psw + salt).encode("utf8"))
    return has.hexdigest()


def get_environ_params(key=None):
    """
        Get the corresponding data file according to the environment information
    :param key: default
    :return:
    """

    if platform.system() == 'Windows' or key is None:
        return _load_json_file(os.path.join(os.getcwd(), "data/default.json"))

    return _load_json_file(os.path.join(os.getcwd(), f"data/{get_os_environ(key)}.json"))


def get_variables_params(obj, variable):
    """
        Gets variable information based on the specified object
    :param variable: variables name
    :param obj: test case name
    :return:
    """
    return analytical_object(get_environ_params(), obj)[variable]


def analytical_object(result, obj):
    """
        Iterate over the nested object to get the desired value.
    :param result:
    :param obj:
    :return:
    """

    for keys, values in result.items():
        if keys == obj:
            return values

        elif isinstance(values, dict):
            return analytical_object(values, obj)

        elif isinstance(values, list):
            for i in values:
                if isinstance(i, dict):
                    return analytical_object(i, obj)


def get_environment_separation(env_key, env_path=".env"):
    """
        Compatible with two sets of environment data separation for switching
    :param env_path:
    :param env_key: environment Key
    :return: Key : data
    """
    load_dot_env_file(os.path.join(os.getcwd(), env_path))
    return get_os_environ(env_key)