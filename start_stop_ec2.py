import sys
import argparse
from termcolor import colored
from ec2 import EC2
import constant

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser as ConfigParser


def exec_action(access_key, secret_key, action, env):
    """
    :param access_key:
    :param secret_key:
    :param action: start or stop
    :param env: env name
    :return: None
    """
    ec2 = EC2(access_key, secret_key, action, env)
    ec2.exec_ec2_action()

    return None


def parse_env(env):
    """

    :param env:  Which env to be used
    :return: tuple of access key and secret key
    """
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(constant.env_file)
    try:
        access_key, secret_key = config_parser.get(env, 'aws_access_key_id'), \
                                 config_parser.get(env,
                                                   'aws_secret_access_key')
    except ConfigParser.NoSectionError:
        raise Exception(colored('No such environement {} keys entries found '.
                                format(env), color='red'))

    return access_key, secret_key


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EC2 Instance actions')
    parser.add_argument('-e', '--env', required=True,
                        help='Environment to be used')
    parser.add_argument('-a', '--action', required=True,
                        help='Action to be specified : start or stop')

    args = parser.parse_args()

    try:
        env, action = args.env, args.action
    except TypeError:
        raise ValueError('Not enough arguments provided')
    print(colored('All inputs provided are environment : {} '
                  '&  action : {} '.format(env, action),
                  color='green'))

    access_key, secret_key = parse_env(env)

    exec_action(access_key, secret_key, action, env)


# Made it compatible for both versions of python.
# python start_stop_ec2.py -a start -e plivo-tcms
# python3 start_stop_ec2.py -a start -e plivo-tcms
