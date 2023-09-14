import utils

def check_two_db_template(job, dbs):
    db_1 = dbs[job.params['connection_1']]
    db_2 = dbs[job.params['connection_2']]
    script_1 = job.params['script_1']
    script_2 = job.params['script_2']
    run_results = (utils.execute_sql(db_1, script_1, 'many'),utils.execute_sql(db_2, script_2, 'many'))
    job.run_result  =  sum(tuple(map(lambda i, j: i - j, run_results[0], run_results[1])))