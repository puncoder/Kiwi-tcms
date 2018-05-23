import argparse
from termcolor import colored
from ec2 import EC2


def exec_action(action, env):
    """
    :param access_key:
    :param secret_key:
    :param action: start or stop
    :param env: env name
    :return: None
    """
    ec2 = EC2(action, env)
    ec2.exec_ec2_action()

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EC2 Instance actions')
    parser.add_argument('-e', '--env', required=True,
                        help='Environment/Profile to be used')
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

    exec_action(action, env)


# Made it compatible for both versions of python.
# python start_stop_ec2.py -a start -e plivo-tcms
# python3 start_stop_ec2.py -a start -e plivo-tcms
