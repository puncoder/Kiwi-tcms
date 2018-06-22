import sys
import tcms_api
from tcms_api.xmlrpc import TCMSKerbXmlrpc , TCMSXmlrpc
import tcms_api.immutable
from tcms_api.immutable import CaseStatus
from tcms_api.mutable import TestCase, TCMS, TestRun, TestCaseRun, TestCaseRunStatus
from tcms_api import TestPlan

# All the attributes of tcms_api.immutable
immutable_objects = dir(tcms_api.immutable)

# pass the credential of your running instance.
# Username, password, kiwi-server/xml-rpc
# TCMSXmlrpc('plivo', 'root', 'http://0.0.0.0:80/xml-rpc/')
TCMSXmlrpc('plivo', 'root', 'http://127.0.0.1:8000/xml-rpc/')


def change_status(args):

    if len(args) < 4:
        raise Exception('Please pass at least 3 arguments.\nStatus, Plan id, TestCase ids')
    status = args[1].upper()
    plan_id = int(args[2])
    testCase_ids = set(map(int, args[3:]))

    print('testCase_ids :: ',testCase_ids)
    test_data = {}

    print('============= UPDATING CASES ===============================\n')

    for case in TestRun(plan_id):
        if case.id in testCase_ids:
            _old_status = case.status
            case.status = TestCaseRunStatus(status)
            case.update()
            print('Case id:', case.id, '::', _old_status, 'Changes to =>', case.status)
    print('\n========== UPDATED CASES ===================================\n')
    for case in TestRun(plan_id):
        print('Case id:', case.id, '===>', case)


    print('\n================= RUN PLAN ATTRIB ==========================\n')

    for funct in immutable_objects:
        try:
            method = getattr(tcms_api.immutable, funct)
            test_data[funct] = str(method(plan_id))
            if funct == 'Tag':
                print (test_data[funct])


        except Exception as e:
            pass

    for key, val in test_data.items():
        print(key, "::", val)

    print('\n============================================================\n')


if __name__ == '__main__':
    change_status(sys.argv)


# Kill running port 8000
# sudo lsof -t -i tcp:8000 | xargs kill -9