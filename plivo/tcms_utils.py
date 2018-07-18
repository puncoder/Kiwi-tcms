import psycopg2
hostname = 'localhost'
username = 'postgres'
password = 'root'
database = 'kiwi'
conn = None


# Making Db connection.
try:
    # print('Connecting to PostgreSQL database..')
    # connect to the PostgreSQL database
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    # create a new cursor
    cur = conn.cursor()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


def get_max_id():
    sql = """SELECT max(run_id)  FROM test_runs;"""
    output = None

    try:
        cur.execute(sql)
        # get the data as tuple
        output = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return output


def get_auth_user():
    sql = """select id,username,first_name,last_name,email,is_superuser,is_active from auth_user;"""
    output = None

    try:
        cur.execute(sql)
        # get the data as tuple
        output = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return output


def get_products():
    sql = """select id, name from products;"""
    output = None

    try:
        cur.execute(sql)
        # get the data as tuple
        output = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return output


def get_running_test_runs():
    sql = """SELECT run_id, summary  FROM public.test_runs where stop_date IS NULL;"""
    output = None

    try:
        cur.execute(sql)
        # get the data as tuple
        output = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return output


def get_finished_test_runs():
    sql = """SELECT run_id, summary  FROM public.test_runs where stop_date IS NOT NULL;"""
    output = None

    try:
        cur.execute(sql)
        # get the data as tuple
        output = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return output


def set_run_status(testrun_id, status):
    params = dict()
    params['testrun_id'] = int(testrun_id)

    if status:
        print('Setting status to Finished...')
        sql = """update public.test_runs set stop_date = current_timestamp where run_id = {testrun_id};"""
    else:
        print('Setting status to Running...')
        sql = """update public.test_runs set stop_date = NULL where run_id = {testrun_id};"""
    rows = None

    try:

        # execute the UPDATE  statement
        cur.execute(sql.format(**params))
        conn.commit()
        # get the data as tuple
        rows = cur.rowcount

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return rows


def _get_product_id(product_name):
    """:returns integer id of product name."""
    sql = """select id from public.products where upper(name) = '{}';""".format(product_name.upper())
    product_id = None

    try:
        # get the max id
        cur.execute(sql)
        product_id = cur.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return product_id


def create_testcase(testcase_data):
    """This creates a new test case.
    Params to pass ::
    test_case_name, note, category_id"""

    print('Adding new test case...')
    max_id = """select nextval('test_cases_case_id_seq');"""
    doc_id = """select nextval('test_case_texts_id_seq');"""
    sql = """insert into test_cases values({case_id}, current_timestamp , 0, 'f' , NULL, NULL, NULL, 
                '{test_case_name}', '', '', '{notes}' , {author_id}, 2, {category_id}, {default_tester_id}, 
                1, NULL, '00:00:00');"""

    doc_sql = """insert into test_case_texts values({doc_id}, 1 , current_timestamp , '', '{exp_out}', 
                '' , '{details}', '', '', '', '', 1, {case_id});"""
    rows = None
    try:
        # get the max id
        cur.execute(max_id)
        try:
            testcase_data['case_id'] = cur.fetchone()[0]
        except Exception as e:
            testcase_data['case_id'] = 1
        # execute the insert  statement
        cur.execute(sql.format(**testcase_data))

        # get the max id
        cur.execute(doc_id)
        try:
            testcase_data['doc_id'] = cur.fetchone()[0]
        except Exception as e:
            testcase_data['doc_id'] = 1
        print(testcase_data)
        # execute the insert  statement
        cur.execute(doc_sql.format(**testcase_data))

        conn.commit()
        # get the data as tuple
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return rows, testcase_data['case_id']


def add_testcase_to_run(testcase_data):
    """Adds a test case into test run and sets status.
    Need to pass case id, notes, status and run id."""

    testcase_data['status'] = _status_id(testcase_data['status'])
    max_id = """select nextval('test_case_runs_case_run_id_seq');"""
    sql = """insert into test_case_runs values({case_run_id}, 1, 
            current_timestamp, NULL, '{notes}', 1, 0, 1, 1, {case_id}, {status}, {run_id}, 1);"""

    try:
        # get the max id
        cur.execute(max_id)
        try:
            testcase_data['case_run_id'] = cur.fetchone()[0]
        except Exception as e:
            testcase_data['case_run_id'] = 1
        print(testcase_data)
        # execute the insert  statement
        cur.execute(sql.format(**testcase_data))
        conn.commit()
        # get the data as tuple
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return rows, testcase_data['case_run_id']


def add_testcase_to_plan(testcase_data):
    """Adds a test case to test plan."""

    print('Adding test case to test run ...')
    max_id = """select nextval('test_case_plans_id_seq');"""
    sql = """insert into test_case_plans values({id}, 1, {case_id}, {plan_id});"""

    try:
        # get the max id
        cur.execute(max_id)
        try:
            testcase_data['id'] = cur.fetchone()[0]
        except Exception as e:
            testcase_data['id'] = 1
        print(testcase_data)
        # execute the insert  statement
        cur.execute(sql.format(**testcase_data))
        conn.commit()
        # get the data as tuple
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return rows, testcase_data['id']


def _status_id(status):
    _status = dict()
    _status[1] = {'IDLE'}
    _status[2] = {'RUNNING','RUN'}
    _status[3] = {'PAUSED'}
    _status[4] = {'PASSED', 'PASS'}
    _status[5] = {'FAILED', 'FAILS', 'FAIL'}
    _status[6] = {'BLOCKED', 'BLOCK'}
    _status[7] = {'ERROR'}
    _status[8] = {'WAIVED', 'UN-AUTO', 'UNAUTOMATED', 'UNAUTO'}

    for id, names in _status.items():
        if status.upper() in names:
            return id
    if status.isdigit() and int(status) in _status.keys():
        return status

    raise Exception('No such status found ::', status)


def update_case_run_id_status(args):
    if len(args) != 2:
        raise Exception('Please pass exactly two arguments, e.i. Test Case Run id (single/range), Status to be changed')
    if '-' in args[0]:
        try:
            start_id , stop_id = map(int, args[0].split('-'))
        except Exception as e:
            raise Exception('Please pass integer range separated by -')
    else:
        try:
            start_id = stop_id = int(args[0])
        except ValueError:
            raise Exception('Please pass integer for Test Case Run id.')

    case_updated = 0
    for case_run_id in range(start_id, stop_id+1):
        params = dict()
        params['case_run_id'] = case_run_id
        params['case_run_status_id'] = _status_id(args[1])

        sql = """UPDATE public.test_case_runs
                    SET case_run_status_id = {case_run_status_id}
                    WHERE case_run_id = {case_run_id};"""

        try:
            # execute the UPDATE  statement
            cur.execute(sql.format(**params))
            # get the number of updated rows
            case_updated += cur.rowcount
            # Commit the changes to the database
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return case_updated


def create_build(build_data):
    """creates test build for a product for a test run and returns build id"""

    # Checking if the build is already there for the product.
    sql = '''select build_id from test_builds where name='{build_name}' and product_id={product_id};'''
    cur.execute(sql.format(**build_data))
    if cur.rowcount == 1:
        print('Build already exists with same name.')
        return cur.fetchone()[0]

    print('creating new build...')
    max_id = """select nextval('test_builds_build_id_seq');"""
    sql = """insert into test_builds values({build_id},'{build_name}', '{build_name}' ,'t',{product_id});"""


    try:
        # get the max id
        cur.execute(max_id)
        try:
            build_data['build_id'] = cur.fetchone()[0]
        except Exception as e:
            build_data['build_id'] = 1
        print(build_data)
        # execute the insert  statement
        cur.execute(sql.format(**build_data))
        conn.commit()
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return build_data['build_id']


def create_component(data):
    """creates test component for a product for a test run and returns id"""

    # Checking if the build is already there for the product.
    sql = '''select id from components where name='{component}' and product_id={product_id};'''
    cur.execute(sql.format(**data))
    if cur.rowcount == 1:
        print('Component already exists with same name for the product.')
        return cur.fetchone()[0]

    print('creating new component...')
    max_id = """select nextval('components_id_seq');"""
    sql = """insert into components values({component_id},'{component}', '{component}' ,NULL,NULL,{product_id});"""

    try:
        # get the max id
        cur.execute(max_id)
        try:
            data['component_id'] = cur.fetchone()[0]
        except Exception as e:
            data['component_id'] = 1
        print(data)
        # execute the insert  statement
        cur.execute(sql.format(**data))
        conn.commit()
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return data['component_id']


def add_component(data):
    """Adds component to Test case."""

    print('Adding component to test case...')
    max_id = """select nextval('test_case_components_id_seq');"""
    sql = """insert into test_case_components values({id}, {case_id}, {component_id});"""

    try:
        # get the max id
        cur.execute(max_id)
        try:
            data['id'] = cur.fetchone()[0]
        except Exception as e:
            data['id'] = 1
        print(data)
        # execute the insert  statement
        cur.execute(sql.format(**data))
        conn.commit()
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return data['id']


def create_test_plan(testplan_data):
    """creates test run and returns test run id"""


    print('creating new test plan ...')
    max_id = """select nextval('test_plans_plan_id_seq');"""
    sql = """insert into test_plans values({plan_id}, '{name}', 
            current_timestamp, 't', NULL , '{author_id}', {owner_id}, {parent_id}, {product_id}, {product_version_id},
             {type_id});"""

    try:
        # get the max id
        cur.execute(max_id)
        try:
            testplan_data['plan_id'] = cur.fetchone()[0]
        except Exception as e:
            testplan_data['plan_id'] = 1
        print(testplan_data)
        # execute the insert  statement
        cur.execute(sql.format(**testplan_data))
        conn.commit()
        # get the data as tuple
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return testplan_data['plan_id']


def create_testrun(testrun_data):
    """creates test run and returns test run id"""

    print('creating new test run ...')
    max_id = """select nextval('test_runs_run_id_seq');"""
    sql = """insert into test_runs values({run_id}, {plan_text_version}, 
            current_timestamp, NULL, '{summary}', '{notes}', {environment_id}, 'f', {build_id}, {default_tester_id},
             {manager_id}, {plan_id}, {product_version_id}, '{estimated_time}');"""

    try:
        # get the max id
        cur.execute(max_id)
        try:
            testrun_data['run_id'] = cur.fetchone()[0]
        except Exception as e:
            testrun_data['run_id'] = 1
        print(testrun_data)
        # execute the insert  statement
        cur.execute(sql.format(**testrun_data))
        conn.commit()
        # get the data as tuple
        rows = cur.rowcount
        # Close communication with the PostgreSQL database

    except (Exception, psycopg2.DatabaseError) as error:
        raise Exception (error)
    return testrun_data['run_id']


def close_conn():
    if conn:
        cur.close()
        conn.close()


if __name__ == '__main__':
    data = {
            'test_case_name': 'testingNewCase_123',
            'category_id': 2,
            'notes' : 'dummy notes'
            }
    print('Row added :: ', create_testcase(data))

