# This file is being used to include and exclude instances from starting/ stopping.

include_exclude_instances = {}

# Regions ===============

# region 1
region = 'us-west-2'
include_exclude_instances[region] = {}
include_exclude_instances[region]['region'] = region
include_exclude_instances[region]['exclude'] = ['']

# region 2
region = 'us-east-2'
include_exclude_instances[region] = {}
include_exclude_instances[region]['region'] = region
include_exclude_instances[region]['exclude'] = ['qa-jenkins']


# Env/ Accounts ================

# Env/Acc 1
env = 'plivo-tcms'
include_exclude_instances[env] = {}
include_exclude_instances[env]['region'] = 'us-west-2'
include_exclude_instances[env]['include'] = ['plivo-tcms']


# Adding excluded instances in an account for a region.
for env, values in include_exclude_instances.items():
    if 'region' in values:
        region = values['region']
        if region in include_exclude_instances and 'exclude' in include_exclude_instances[region]:
            include_exclude_instances[env]['exclude'] = include_exclude_instances[region]['exclude']
