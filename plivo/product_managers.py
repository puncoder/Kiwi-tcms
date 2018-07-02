managers = dict()
mandatory_reviewers = ['Rahul,rahul@plivo.com','Amit,amityadav@plivo.com']
managers['messaging'] = ['Prashant,prashant@plivo.com','Rahul,rahul.k@plivo.com']
managers['voice'] = ['Nalin,nalin@plivo.com','Haiku,haiku@plivo.com']
managers['internal system'] = ['Karthik,karthik@plivo.com']
managers['data'] = ['Karthik,karthik@plivo.com']
managers['phlo'] = ['Govinda,govinda@plivo.com']
managers['console'] = ['Govinda,govinda@plivo.com']
managers['zentrunk'] = ['Abhilash,abhilash@plivo.com','Sushant,sushant@plivo.com']
for user in managers:
    managers[user].extend(mandatory_reviewers)
