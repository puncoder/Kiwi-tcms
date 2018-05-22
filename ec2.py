import boto3
import datetime
from termcolor import colored
from config.ec2_instances import include_exclude_instances


class EC2(object):
    """
    EC2 class for plivo EC2 instances action
    """

    def __init__(self, access_key, secret_key, action, env,):
        self.session = boto3.Session(aws_access_key_id=access_key,
                                     aws_secret_access_key=secret_key)
        self.env = env
        self.action = action

        if self.env in include_exclude_instances:
            self.region = include_exclude_instances[self.env]['region']
        else:
            raise Exception(colored(
                'Env not found in config file'
                'for env {}.'.format(self.env),
                color='red'
            ))
        if not self.region:
            raise Exception(colored(
                'Region not found in config file'
                'for env {}.'.format(self.env),
                color='red'
            ))

        self.ec2_client = self.session.client('ec2', region_name=self.region)

    def exec_ec2_action(self):
        """
        Does specified action on all ec2 machines barring excluded instances
        :return: None
        """
        # Finding included / excluded instances for this action.

        excluded_instances = include_exclude_instances[self.env].get('exclude', [])
        print(colored('Excluded instances for the region : "{}" are : {} '.format(self.region, excluded_instances),
                      color='yellow'))
        included_instances = include_exclude_instances[self.env].get('include', [])
        print(colored('Included instances for the region : "{}" are : {} '.format(self.region, included_instances),
                      color='yellow'))

        instances = self.get_instance_ids(exclude_instances=excluded_instances,
                                          included_instances=included_instances)
        instance_names = list(instances.keys())
        instance_ids = list(instances.values())
        print(colored('Final list of instances for {} are: {} having instance '
                      'ids: {}'.format(self.action,
                                       instance_names, instance_ids),
                      color='cyan'))
        if self.action.lower() == 'start':
            print(colored('Starting instances : {} '.format(instance_names),
                          color='blue'))
            self.ec2_client.start_instances(InstanceIds=instance_ids)
        elif self.action.lower() == 'stop':
            print(colored('Stoping instances : {} '.format(instance_names),
                          color='blue'))
            self.ec2_client.stop_instances(InstanceIds=instance_ids)
        else:
            pass

        return

    def get_instance_ids(self, exclude_instances=None, included_instances=None):
        """
        This function returns instance name along with instance ids as dict

        :param exclude_instances: Instance names to be excluded from start/stop
               as list
        :param included_instances: Instance names to be included for start/stop
               as list
        :return: Isntance name : instance id -- as dict
        """
        if not included_instances:
            raise Exception(colored(
                'No instances included in the given region {} & '
                'for env {}. Please check ec2_instances.py'.format(self.region, self.env),
                color='red'
            ))

        instances = {}
        response = self.ec2_client.describe_instances()
        for res in response['Reservations']:
            for instance in res['Instances']:
                for instance_name in instance['Tags']:
                    if instance_name['Key'] == 'Name':
                        instances[instance_name['Value']] = \
                            instance['InstanceId']
        if not instances:
            raise Exception(colored(
                'No instances found in the given region {} & '
                'for env {}'.format(self.region, self.env),
                color='red'
            ))

        strictly_included = set(included_instances) - set(exclude_instances)

        if not strictly_included:
            raise Exception(colored(
                'No instances left after excluding instances from included instances in the given region {} & '
                'for env {}.'.format(self.region, self.env),
                color='red'
            ))

        strict_instances = {}

        for instance_name, instance_id in instances.items():
            if instance_name in strictly_included:
                strict_instances[instance_name] = instance_id

        if not strict_instances:
            raise Exception(colored(
                'No instances included after strict_instances in the given region {} & '
                'for env {}.'.format(self.region, self.env),
                color='red'
            ))

        return strict_instances

    def myconverter(self, o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
