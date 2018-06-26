# Plivo Test Case Management System
from plivo.products import product
import argparse
from plivo.spreadsheet_reader import parse_spreadsheet
from plivo.tcms_utils import add_testcase_to_run, update_case_run_id_status, create_testcase, \
    set_run_status, get_running_test_runs, close_conn, get_finished_test_runs, create_test_plan, create_testrun, \
    add_testcase_to_plan, create_build

from plivo.update_status_from_jenkins import update_status_from_jenkins, change_status_from_run, _parse_jenkin_output

print('started..')


def sequential_starter(args):

    if args.spreadsheet_product:
        if len(args.spreadsheet_product) == 2:
            spreadsheet_id = args.spreadsheet_product[0]
            product_name = args.spreadsheet_product[1].upper()

        else:
            raise Exception('Please pass exactly two params, spreadsheet id and product_name.')
        print('Adding from Spreadsheet.')
        data_dict, title = parse_spreadsheet(spreadsheet_id)
        rows = 0
        # creating build
        build_data = product[product_name].copy()
        build_data['build_name'] = title
        build_id = create_build(build_data)

        for plan, data in data_dict.items():
            print('plan ::', plan)
            plan_data = product[product_name].copy()
            testrun_data = product[product_name].copy()
            plan_data['name'] = plan
            plan_data['build_id'] = build_id
            plan_id = create_test_plan(plan_data)
            print('plan id :: ', plan_id)

            testrun_data['plan_id'] = plan_id
            testrun_data['summary'] = plan
            testrun_data['notes'] = title
            testrun_data['build_id'] = build_id
            run_id = create_testrun(testrun_data)
            print('test run id ::', run_id)

            print('creating test cases..')

            for case, case_data in data.items():
                print('case', '::', case)
                print('#####')
                testcase_data = product[product_name].copy()
                testcase_data['test_case_name'] = case
                testcase_data['build_id'] = build_id
                testcase_data['notes'] = case_data['note']
                testcase_data['plan_id'] = plan_id
                testcase_data['exp_out'] = ''.join(['<p>'+line+'</p>' for line in case_data['exp_output'].split('\n')])
                testcase_data['status'] = case_data['status']
                row, case_id = create_testcase(testcase_data)
                testcase_data['case_id'] = case_id

                print('Adding test case to plan.')
                row, id = add_testcase_to_plan(testcase_data)

                print('id :: ', id)

                print('Adding test case to test run.')
                testcase_data['run_id'] = run_id
                testcase_data['case_id'] = case_id
                testcase_data['notes'] = title
                row, case_id = add_testcase_to_run(testcase_data)
                rows += row
            print('===============================')

        print('Rows updated ::', rows)
    if args.jenkins_jobs:
        run_name = False
        job = args.jenkins_jobs[0]
        if len(args.jenkins_jobs) > 1:
            run_name = args.jenkins_jobs[1]
        if update_status_from_jenkins(job, run_name):
            print('Job updated :: ', job)
            print('============================================================')

    if args.case_run_id:
        if args.status:
            rows = update_case_run_id_status([args.case_run_id, args.status])
        else:
            raise Exception('Please pass status using -status argument in same command.')

        print('Rows updated : ', rows)

    if args.add_testcase:
        argv = args.add_testcase
        if len(argv) != 3:
            raise Exception('Please pass Exactly 3 arguments. Testcase Name, Category id, Notes.')

        if 'name=' not in argv[0] or 'cat_id=' not in argv[1] or 'notes=' not in argv[2]:
            raise Exception('Please pass Exactly 3 arguments with args name="test case name" cat_id="category id" '
                            'notes="Add notes" ')
        testname = argv[0].split('name=')[1]
        cat_id = argv[1].split('cat_id=')[1]
        notes = argv[2].split('notes=')[1]

        testcase_data = dict()
        testcase_data['test_case_name'] = testname
        testcase_data['category_id'] = cat_id
        testcase_data['notes'] = notes

        rows, case_id = create_testcase(testcase_data)

        print('Rows updated ::', rows)
        print('Test case id ::', case_id)

    if args.add_tc_to_run:
        argv = args.add_tc_to_run
        if len(argv) != 4:
            raise Exception('Please pass Exactly 4 arguments. run_id, case_id, status, Notes.')

        testcase_data = dict()
        try:
            if '-' in argv[1]:
                start, stop = map(int, argv[1].split('-'))
            else:
                start = stop = int(argv[1])

        except ValueError:
            raise Exception('Please pass integers for run_id and case_id.')

        for case_id in range(start, stop + 1):
            try:

                testcase_data['run_id'] = int(argv[0])
                testcase_data['case_id'] = case_id
                testcase_data['status'] = argv[2]
                testcase_data['notes'] = argv[3]

            except ValueError:
                raise Exception('Please pass integers for run_id and case_id.')

            rows, case_run_id = add_testcase_to_run(testcase_data)

            print('Rows updated ::', rows)
            print('Test case id ::', case_run_id)
            print()

    if args.set_running:
        try:
            run_id = int(args.set_running)
            set_run_status(run_id, False)
        except ValueError:
            raise Exception('Please pass integer for Run Id.')

    if args.set_finished:
        try:
            run_id = int(args.set_finished)
            set_run_status(run_id, True)
        except ValueError:
            raise Exception('Please pass integer for Run Id.')

    if args.get_running_testruns:
        running_test_runs = get_running_test_runs()
        if running_test_runs:
            print('Run id\t\tSummary')
            for run_id, summary in running_test_runs:
                print(run_id,'\t\t', summary)
        else:
            print('No Running Test Runs.')

    if args.get_finished_testruns:
        finished_test_runs = get_finished_test_runs()
        if finished_test_runs:
            print('Run id\t\tSummary')
            for run_id, summary in finished_test_runs:
                print(run_id,'\t\t', summary)
        else:
            print('No Finished Test Runs.')

    if args.status_by_run:
        if len(args.status_by_run) < 3:
            raise Exception('Please pass at least 3 arguments.\nStatus, Run id, TestCase ids')
        status = args.status_by_run[0]
        try:
            run_id = int(args.status_by_run[1])
        except ValueError:
            raise Exception('Please pass an integer for plan id.')
        testcase_ids = args.status_by_run[2:]

        change_status_from_run(status, run_id, testcase_ids)

    if args.add_testcase_jenkins:
        argv = args.add_testcase_jenkins
        if len(argv) != 5:
            raise Exception('Please pass Exactly 5 arguments. jenkins_job_name, product, plan name, testrun name and'
                            'Build name.')

        job_name = argv[0]
        product_name = argv[1].upper()
        plan_name = argv[2]
        testrun_name = argv[3]
        build_name = argv[4]

        jenkins_data = _parse_jenkin_output(job_name)

        # all_testcases = [case.strip() for key, val in jenkins_data.items() for case in val['testcase']]
        # creating build
        build_data = product[product_name].copy()
        build_data['build_name'] = build_name
        build_id = create_build(build_data)

        plan_data = product[product_name].copy()
        testrun_data = product[product_name].copy()
        plan_data['name'] = plan_name
        plan_data['build_id'] = build_id

        plan_id = create_test_plan(plan_data)
        print('plan id :: ', plan_id)

        testrun_data['plan_id'] = plan_id
        testrun_data['summary'] = testrun_name
        testrun_data['build_id'] = build_id
        run_id = create_testrun(testrun_data)
        print('test run id ::', run_id)

        print('creating test cases..')
        rows = 0
        for plan, values in jenkins_data.items():
            for case in values['testcase']:
                testcase_data = product[product_name].copy()
                testcase_data['test_case_name'] = case
                testcase_data['notes'] = plan
                testcase_data['plan_id'] = plan_id
                row, case_id = create_testcase(testcase_data)

                testcase_data['case_id'] = case_id

                print('Adding test case to plan.')
                row, id = add_testcase_to_plan(testcase_data)

                print('Adding test case to test run.')
                testcase_data['run_id'] = run_id
                testcase_data['case_id'] = case_id
                testcase_data['status'] = values['testcase'][case]['status']
                row, case_id = add_testcase_to_run(testcase_data)
                rows += row

        print('Rows updated ::', rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-add_from_spreadsheet', action='store', dest='spreadsheet_product', nargs='+',
                        help='Adds the test cases from google spreadsheet. Pass the spreadsheet id and product name')

    parser.add_argument('-update_from_jenkins', action='store', dest='jenkins_jobs', nargs='+',
                        help='Updates status from jenkins jobs. Pass the jenkins job name.\n'
                             'Pass run id to update directly in one test run id.')

    parser.add_argument('-add_from_jenkins', action='store', dest='add_testcase_jenkins', nargs='+',
                        help='This adds the test cases from a jenkins job .'
                             'Need to pass jenkins_job_name, product_name, plan_name , testrun_name and build_name '
                             'with this arg.'
                             'format ::\n -add_testcase_from_jenkins <jenkins_job_name> '
                             '<product_name> <plan_name> <testrun_name> <build_name>')

    parser.add_argument('-status', action='store', dest='status',
                        help='Updates status for a range or single Test Case Run id.'
                             '\nPass the status here. it must be used with -case_ids argument.')

    parser.add_argument('-case_ids', action='store', dest='case_run_id',
                        help='Updates status for a range or single Test Case Run id.'
                             '\nPass either single integer or range of integers separated by -'
                             '\nMust be used with -status argument.')

    parser.add_argument('-add_testcase', action='store', dest='add_testcase', nargs='+',
                        help='This adds the test case for a product.'
                             'Need to pass Test Case Name, Category id, and Notes with this arg.\n'
                             'format ::\n -add_testcase name="test case name" cat_id=category id notes="add notes" ')

    #
    parser.add_argument('-set_running', action='store', dest='set_running',
                        help='This sets the Test Run to Running. Pass the Test Run id')

    parser.add_argument('-set_finished', action='store', dest='set_finished',
                        help='This sets the Test Run to Finished. Pass the Test Run id')

    parser.add_argument('-status_by_run', action='store', dest='status_by_run', nargs='+',
                        help='This changes status of test cases inside a test run.')

    parser.add_argument('-add_tc_to_run', action='store', dest='add_tc_to_run', nargs='+',
                        help='This adds the test case to the Test Runs and sets status.')

    parser.add_argument('-get_running', action='store_true', dest='get_running_testruns',
                        help='This gives the list of running Test Runs.')

    parser.add_argument('-get_finished', action='store_true', dest='get_finished_testruns',
                        help='This gives the list of running Test Runs.')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    results = parser.parse_args()

    # starts the tasks in sequential order.
    flag = True
    while flag:
        try:
            sequential_starter(results)
            flag = False
        except OSError:
            pass

    # close the running Db connection.
    close_conn()







