import requests
import sys
import os
import json
import xmltodict
from time import sleep
from tcms_api.xmlrpc import TCMSXmlrpc
from tcms_api.mutable import TestRun, TestCaseRunStatus
from plivo.tcms_utils import get_max_id

# Login to running KIWI server.
with open('xml-rpc.txt') as file:
    server = file.read().strip()
TCMSXmlrpc('plivo', 'root', 'http://'+server+'/xml-rpc/')

# Authenticating Jenkins
home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')
credential_path = os.path.join(credential_dir, 'plivo_auth.json')
file = open(credential_path)
credentials = json.loads(file.read())
username, password = credentials['jenkins_id'], credentials['jenkins_password']
file.close()


def _parse_jenkin_output(job_name):
    try:
        r = requests.get('http://jenkins.qa.plivodev.com/job/'+job_name+'/ws/output.xml',
                         auth=(username, password))
        doc = xmltodict.parse(r.text)
    except Exception as e:
        print('Error :', e)
        print('Not a valid Job name or response issue in :', job_name)
        return False

    test_status = {}
    for test_case in doc['robot']['suite']['suite']:
        name = test_case['@name']
        test_status[name] = {}
        test_status[name]['status'] = test_case['status']['@status']
        test_status[name]['end_time'] = test_case['status']['@endtime']
        test_status[name]['start_time'] = test_case['status']['@starttime']
        test_status[name]['source'] = test_case['@source']

        test_status[name]['testcase'] = {}

        if type(test_case['test']) != list:
            test_name = test_case['test']['@name']
            test_status[name]['testcase'][test_name] = {}
            test_status[name]['testcase'][test_name]['status'] = test_case['test']['status']['@status']
            test_status[name]['testcase'][test_name]['start_time'] = test_case['test']['status']['@starttime']
            test_status[name]['testcase'][test_name]['end_time'] = test_case['test']['status']['@endtime']
        else:
            for each_test in test_case['test']:
                test_name = each_test['@name']
                test_status[name]['testcase'][test_name] = {}
                test_status[name]['testcase'][test_name]['status'] = each_test['status']['@status']
                test_status[name]['testcase'][test_name]['start_time'] = each_test['status']['@starttime']
                test_status[name]['testcase'][test_name]['end_time'] = each_test['status']['@endtime']

    return test_status


def _status_id(status):
    _status = dict()
    _status[1] = {'IDLE'}
    _status[2] = {'RUNNING', 'RUN'}
    _status[3] = {'PAUSED'}
    _status[4] = {'PASSED', 'PASS'}
    _status[5] = {'FAILED', 'FAILS', 'FAIL'}
    _status[6] = {'BLOCKED', 'BLOCK'}
    _status[7] = {'ERROR'}
    _status[8] = {'WAIVED', 'UN-AUTO', 'UNAUTOMATED', 'UNAUTO'}

    for status_id, names in _status.items():
        if status.upper() in names:
            return status_id
    if status.isdigit() and int(status) in _status.keys():
        return int(status)

    raise Exception('No such status found ::', status)


def change_status_from_run(status, run_id, testcases):
    flag = False
    testcase_ids = None
    if testcases[0].upper() == 'ALL':
        flag = True
    else:

        try:
            testcase_ids = set(map(int, testcases))
        except ValueError:
            raise Exception('Please pass integers in test case ids.')

    print('testCase_ids :: ', testcase_ids)

    print('============= UPDATING CASES ===============================\n')

    for case in TestRun(run_id):
        if flag or case.id in testcase_ids:
            _old_status = case.status
            status_id = _status_id(status)
            case.status = TestCaseRunStatus(status_id)
            case.update()
            print('Case id:', case.id, '::', _old_status, 'Changes to =>', case.status)
    print('\n========== UPDATED CASES ===================================\n')
    for case in TestRun(run_id):
        print('Case id:', case.id, '===>', case)


def _change_status(jenkins_status, run_id):
    if not str(run_id).isdigit():
        raise Exception('Please pass integer as run id.')
    run_id = int(run_id)

    print('Test Run id :: ', run_id)
    print('============= UPDATING CASES ===============================\n')
    for Test_plan, plan_val in jenkins_status.items():

        for case in TestRun(run_id):
            try:
                test_case = str(case).split('-')[-1].strip()
                status = plan_val['testcase'][test_case]['status']

                print('Test Case :: ', test_case)
                print('Jenkins Status for the Test case :: ', status)

                status = _status_id(status)
                print('Status id :: ', status)

                _old_status = case.status
                print('Old Status for the Test case :: ', _old_status)
                case.status = TestCaseRunStatus(status)
                case.update()
                print('Case id:', case.id, '::\n\t\tOld Status ==>', _old_status, '\n\t\tChanges to ==>', case.status)
                print()

            except Exception as e:
                pass

    print('\n========== UPDATED CASES ===================================\n')
    for case in TestRun(run_id):
        print('Case id:', case.id, '===>', case)
    print('\n============================================================\n')


def _change_status_all_runs(jenkins_status):
    max_id = int(get_max_id())
    run_id = 1

    while run_id <= max_id:
        try:
            for Test_plan, plan_val in jenkins_status.items():
                for case in TestRun(run_id):
                    try:
                        test_case = str(case).split('-')[-1].strip()
                        status = plan_val['testcase'][test_case]['status']

                        print('Test Case :: ', test_case)
                        print('Jenkins Status for the Test case :: ', status)

                        status = _status_id(status)
                        print('Status id :: ', status)

                        _old_status = case.status
                        print('Old Status for the Test case :: ', _old_status)
                        case.status = TestCaseRunStatus(status)
                        case.update()
                        print('Case id:', case.id, '::\n\t\tOld Status ==>', _old_status, '\n\t\tChanges to ==>',
                              case.status)
                        print()

                    except:
                        pass

                    sleep(0.1)
        except Exception as e:
            if 'Failed to fetch test run' in str(e):
                pass

            if 'Protocol wrong type for socket' in str(e):
                run_id -= 1

            if 'OSError' in str(e):
                run_id -= 1
        run_id += 1


def update_status_from_jenkins(jenkins_job_name, run_id=False):
    flag = True
    i = 1
    while flag:
        print('Iteration :', i)
        i += 1
        try:
            jenkins_status = _parse_jenkin_output(jenkins_job_name)
            if jenkins_status:
                if run_id:
                    _change_status(jenkins_status, run_id)
                else:
                    _change_status_all_runs(jenkins_status)
            else:
                return False
            flag = False
        except OSError:
            pass
    return True


if __name__ == '__main__':
    update_status_from_jenkins(sys.argv[1])
