import datetime
import hashlib
import random
import time
import calendar
import os
import io
import json
import platform

from datetime import date, timedelta
from httprunner import exceptions
from httprunner.utils import get_os_environ
from loguru import logger


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


def set_os_environ(variables_mapping):
    """ set variables mapping to os.environ
    """
    for variable in variables_mapping:
        os.environ[variable] = variables_mapping[variable]
        logger.debug("Set OS environment variable: {}".format(variable))


def load_dot_env_file(dot_env_path):
    """ load .env file.
    Args:
        dot_env_path (str): .env file path
    Returns:
        dict: environment variables mapping
            {
                "UserName": "debug talk",
                "Password": "123456",
                "PROJECT_KEY": "A B C D E F G H"
            }
    Raises:
        exceptions.FileFormatError: If .env file format is invalid.
    """
    if not os.path.isfile(dot_env_path):
        return {}

    logger.info("Loading environment variables from {}".format(dot_env_path))
    env_variables_mapping = {}

    with io.open(dot_env_path, 'r', encoding='utf-8') as fp:
        for line in fp:
            # maxsplit=1
            if "=" in line:
                variable, value = line.split("=", 1)
            elif ":" in line:
                variable, value = line.split(":", 1)
            else:
                raise exceptions.FileFormatError(".env format error")

            env_variables_mapping[variable.strip()] = value.strip()

    set_os_environ(env_variables_mapping)
    return env_variables_mapping


def extraction_data(data_key):
    """
        Compatible with two sets of environment data separation for switching
    :param data_key: environment Key
    :return: Key : data
    """

    if get_os_environ('TEST_ENV') == 'TEST1':
        dot_env_path = os.path.join(os.getcwd(), ".env")
        load_dot_env_file(dot_env_path)
    else:
        dot_env_path = os.path.join(os.getcwd(), "2.env")
        load_dot_env_file(dot_env_path)
    return get_os_environ(data_key)


def load_json_file(json_file):
    """
        load json file and check file content format
    :param json_file:
    :return:
    """
    with io.open(json_file, encoding='utf-8') as data_file:
        try:
            json_content = json.load(data_file)
        except Exception as e:
            err_msg = f"JSONDecodeError: JSON file format error: {e}"
            logger.error(err_msg)
            raise

        _check_format(json_file, json_content)
        return json_content


def _check_format(file_path, content):
    """
        check test case format if valid
    :param file_path:
    :param content:
    :return:
    """
    if not content:
        err_msg = f"Test case file content is empty: {file_path}"
        logger.error(err_msg)
        raise exceptions.FileFormatError(err_msg)
    elif not isinstance(content, (list, dict)):
        err_msg = f"Test case file content format invalid: {file_path}"
        logger.error(err_msg)
        raise exceptions.FileFormatError(err_msg)


def get_environ_params(key='TEST_ENV'):
    """
        Get the corresponding data file according to the environment information
    :param key: default
    :return:
    """

    if platform.system() == 'Windows':
        return load_json_file(os.path.join(os.getcwd(), "data/TEST1.json"))

    return load_json_file(os.path.join(os.getcwd(), f"data/{get_os_environ(key)}.json"))


def get_variables_params(obj, variable):
    """
        Gets variable information based on the specified object
    :param variable: variables name
    :param obj: test case name
    :return:
    """
    return analytical_object(get_environ_params(), obj)[variable]


def analytical_object(result, obj, default=None):
    """
        Iterate over the nested object to get the desired value.
    :param default:
    :param result:
    :param obj:
    :return:
    """

    for keys, values in result.items():
        if keys == obj:
            return values

        elif isinstance(values, dict):
            response = analytical_object(values, obj, default)
            if response is not default:
                return response

        elif isinstance(values, list):
            for i in values:
                if isinstance(i, dict):
                    response = analytical_object(i, obj, default)
                    if response is not default:
                        return response

                elif isinstance(i, list):
                    logger.warning("Don't be so much nested, okay ?")
                    for v in i:
                        if isinstance(v, dict):
                            response = analytical_object(v, obj, default)
                            if response is not default:
                                return response


def teardown_hook_sleep_N_secs(response, n_secs):
    """
         sleep n seconds after request
    :param response:
    :param n_secs:
    :return:
    """
    time.sleep(n_secs) if response.status_code == 200 else time.sleep(1.0)


if __name__ == '__main__':
    pass