# This file is being used to include and exclude instances from starting/ stopping.

include_exclude_instances ={}

# region 1
region = 'us-west-2'
include_exclude_instances[region] = {}
include_exclude_instances[region]['region'] = region
include_exclude_instances[region]['exclude'] = ['plivo']

# region 2
region = 'us-east-2'
include_exclude_instances[region] = {}
include_exclude_instances[region]['region'] = region
include_exclude_instances[region]['exclude'] = ['qa-jenkins']


# account 1
account = 'plivo-tcms'
include_exclude_instances[account] = {}
include_exclude_instances[account]['region'] = 'us-west-2'
include_exclude_instances[account]['include'] = ['plivo-tcms']


# Adding excluded instances in an account for a region.
for acc, values in include_exclude_instances.items():
    if 'region' in values:
        region = values['region']
        if region in include_exclude_instances and 'exclude' in include_exclude_instances[region]:
            include_exclude_instances[acc]['exclude'] = include_exclude_instances[region]['exclude']
