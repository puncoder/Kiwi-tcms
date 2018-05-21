import sys
if sys.version_info[0] < 3:
    import ConfigParser
    config_parser = ConfigParser.ConfigParser()
else:
    import configparser
    config_parser = configparser.ConfigParser()
import argparse

from termcolor import colored

from ec2 import EC2
import constant


def exec_action(access_key, secret_key, region, action, env):
    """

    :param access_key:
    :param secret_key:
    :param region: region name
    :param action: start or stop
    :param env: env name
    :return: None
    """
    ec2 = EC2(access_key, secret_key, region, action, env)
    ec2.exec_ec2_action()

    return None


def parse_env(env):
    """

    :param env:  Which env to be used
    :return: tuple of access key and secret key
    """
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
    parser.add_argument('-r', '--region', required=True,
                        help='Region in which EC2 to be started/stopped')
    parser.add_argument('-a', '--action', required=True,
                        help='Action to be specified : start or stop')

    args = parser.parse_args()

    try:
        env, region, action = args.env, args.region, args.action
    except TypeError:
        raise ValueError('Not enough arguments provided')
    print(colored('All inputs provided are environment : {}, region name : {} '
                  '&  action : {} '.format(env, region, action),
                  color='green'))

    access_key, secret_key = parse_env(env)

    exec_action(access_key, secret_key, region, action, env)


# Made it compatible for both versions of python.
# python start_stop_ec2.py -a start -r us-west-2 -e plivo-tcms
# python3 start_stop_ec2.py -a start -r us-west-2 -e plivo-tcms
