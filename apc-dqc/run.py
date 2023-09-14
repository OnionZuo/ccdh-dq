"""Entrypoint to execute python scripts."""
import argparse
import dbconnect as dbc
from job import Job
from config import DEVCONN
from datetime import datetime
import utils
from utils import exception_logging, tz


@exception_logging('RUNNING PROGRAM')
def main(group_id):
    dbmeta = DEVCONN

    #  database connection
    dbs = {0: dbc.SQLServerDB(host=dbmeta['host'], database=dbmeta['database'],
                              user=dbmeta['user'], password=dbmeta['password']), }

    # fetch job info
    df_job, dict_conn, job_params = utils.get_job_info(dbs[0], group_id)

    if df_job is None:
        utils.send_email(group_id=group_id, mailtype='NO JOB RUN')

    # connect to dbs
    dbs = dbc.connect(dict_conn, dbs)

    # initialzing log table
    init_logs = []
    job_instances = []
    
    for job_detail in df_job.itertuples():
        try:
            job_instance = Job(utils.run_id, job_detail, job_params)
            job_instances.append(job_instance)
            init_logs.append(job_instance.log)
            utils.get_logger().info(f'[JOB INSTANCE CREATED] {job_detail}\n')
        except Exception as e:
            utils.get_logger().error(f'[FAILED CREATING JOB INSTANCE] {job_detail}\n{e}')

    utils.init_logtb(dbs[0], init_logs)

    for job in job_instances:
        utils.get_logger(False).info(f'\n[{job.id}] {job.name} {job.desc}')

        utils.update_logtb(job, dbs[0], 'begin', {'run_status': 'RUNNING'})
        run_return = job.run(dbs)

        if job.run_result == 'e' or run_return == 'e':
            utils.update_logtb(job, dbs[0], 'end', {'run_status': 'FAILED', 'check_result': '-1'})
        else:
            job.check_result = 1 if str(job.run_result) == str(job.expected_result) else 0
            utils.update_logtb(job, dbs[0], 'end', {'run_status': 'FINISHED', 'check_result': job.check_result})

    return job_instances


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entry point to execute data quality control scripts.')
    parser.add_argument('-groupid', default=None, type=int, help='id of the job group to be run')
    args = parser.parse_args()
    group_id = args.groupid

    start_time = datetime.now(tz)
    main_return = main(group_id)
    duration = datetime.now(tz) - start_time

    utils.get_logger().info(f'[TOTAL RUNNING TIME] {duration}')

    if main_return == 'e':
        utils.send_email(group_id=group_id, mailtype='RUNNING ABORTED')
    else:
        utils.send_email(group_id=group_id, job_instances=main_return)
