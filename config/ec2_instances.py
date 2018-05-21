# This file is being used to include and exclude instances from starting/stoping

include_exclude_instances ={}

# region 1
region = 'us-west-2'
include_exclude_instances[region] = {}
include_exclude_instances[region]['include'] = {'plivo-tcms'}
include_exclude_instances[region]['exclude'] = {}

# region 2
region = 'us-east-2'
include_exclude_instances[region] = {}
include_exclude_instances[region]['include'] = {}
include_exclude_instances[region]['exclude'] = {'qa-jenkins'}


