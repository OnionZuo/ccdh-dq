import functools
import logging
from pytz import timezone
from datetime import datetime
import pandas as pd
from config import TZ, MASTERTBS, EMAILCONFIG, EMAIL_SUCCESS, EMAIL_FAIL
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path
import os
import sys

# 设置日志时区
tz = timezone(TZ)


def timetz(*args):
    return datetime.now(tz).timetuple()


# 生成当前运行批次ID
run_id = datetime.now(tz).strftime("%Y%m%d%H%M%S")

# region logging
logfolder = 'logs'
logfile = f'{run_id}.log'
logpath = Path(f'{logfolder}/{logfile}')

if not os.path.exists(Path(f'{logfolder}/')):
    os.makedirs(Path(f'{logfolder}/'))


class DispatchingFormatter:

    def __init__(self, formatters, default_formatter):
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        formatter = self._formatters.get(record.name, self._default_formatter)
        return formatter.format(record)


def get_logger(default_format=True):
    """ 生成或获取Logger

    Args:
        default_format (bool): 值为True时生成日志内容包含时间-日志级别-日志信息，值为False时生成日志内容仅包含日志信息。默认值为True。

    Returns:
        logging.Logger: 用于生成日志的Logger类实例
    """
    if default_format:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger('detail')
    if not logging.getLogger().handlers:
        logging.Formatter.converter = timetz
        logging.basicConfig(level=logging.INFO, filemode='w')
        f_handler = logging.FileHandler(logpath)
        f_handler.setFormatter(
            DispatchingFormatter(
                {'detail': logging.Formatter(fmt='%(message)s')},
                logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')))
        logger.addHandler(f_handler)
    return logger


def exception_logging(log_info):
    """ 生成日志信息的装饰器

    Args:
        log_info (str): 被装饰函数执行时生成日志的标签
    """

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            logger.info(f'[{log_info}...]')
            try:
                func = function(*args, **kwargs)
                logger.info(f'[FINISHED {log_info.split()[0]}]\n')
                return func
            except Exception as e:
                err = f'EXCEPTION OCCURRED RUNNING FUNCTION {function.__name__}\n{e}'
                logger.error(f'[FAILED {log_info.split()[0]}] {err}\n')
                if args and 'dbconnect' in str(args[0]) and args[0].connection:
                    args[0].connection.rollback()
                return 'e'

        return wrapper

    return decorator


utils_logger = get_logger()


# endregion


# region email notification
def send_email(group_id, job_instances=None, mailtype=''):
    """ 发送邮件

    Args:
        group_id (int / None): 运行run.py时传入的校验组id，没有传入参数时为None。
        job_instances (list, optional): 当前任务批次的所有Job类实例。批次执行正常终止时传入，用于生成邮件内容。
        mailtype (str, optional): 描述批次执行情况的字符串。批次执行非正常终止时传入，邮件标题将会包含该字符串，邮件内容将仅包含日志内容。

    Returns:
        None
    """
    group_id = 'ALL' if not group_id else group_id

    with logpath.open() as f:
        log_content = f.read()
        log_content = log_content.replace('- ERROR -', '- <span style="color:red">ERROR</span> -')

    subject = f'[DQC Group {group_id}-{run_id}] '

    if mailtype:
        subject += mailtype
        content = EMAIL_FAIL.format(log_content=log_content)
    else:
        red_list = []
        green_list = []
        content_d = {'count': {_: 0 for _ in ['pass', 'fail', 'error']},
                     'content': {_: '' for _ in ['pass', 'fail', 'error']}}

        for job in job_instances:
            if job.check_result == 1:
                content_d['content']['pass'] += f'<p>[{job.id}] {job.name}</p>'
                content_d['count']['pass'] += 1
                green_list.append(f'[{job.id}] {job.name} {job.desc}')
            elif job.check_result == 0:
                content_d['content'][
                    'fail'] += f'<p>[{job.id}] {job.name} - expected {job.expected_result} get {job.run_result}</p>'
                content_d['count']['fail'] += 1
                red_list.append(f'[{job.id}] {job.name} {job.desc}')
            else:
                content_d['content']['error'] += f'<p>[{job.id}] {job.name}</p>'
                content_d['count']['error'] += 1
                red_list.append(f'[{job.id}] {job.name} {job.desc}')

        for _ in red_list:
            log_content = log_content.replace(_, f'<span style="color:red"><b>{_}</span></b>')
        for _ in green_list:
            log_content = log_content.replace(_, f'<span style="color:green"><b>{_}</span></b>')

        ttl_count = sum(content_d['count'].values())
        summary = f'''<p>{ttl_count}  jobs: {content_d['count']['error']} running failed, {content_d['count']['fail']} check failed, {content_d['count']['pass']} check passed</p>'''
        content = EMAIL_SUCCESS.format(summary=summary, pass_content=content_d['content']['pass'],
                                       fail_content=content_d['content']['fail'],
                                       error_content=content_d['content']['error'], log_content=log_content)
        if content_d['count']['pass'] == {ttl_count}:
            subject += f'''✔ {content_d['count']['pass']}/{ttl_count} PASSED'''
        else:
            subject += f'''✘ {content_d['count']['pass']}/{ttl_count} PASSED'''

    # email configuration
    s = smtplib.SMTP(host=EMAILCONFIG['smtp_host'], port=EMAILCONFIG['smtp_port'])
    s.login(EMAILCONFIG['sender'], EMAILCONFIG['password'])
    msg = MIMEMultipart()
    msg.attach(MIMEText(content, 'html', _charset="utf-8"))
    msg['From'] = EMAILCONFIG['sender']
    msg['Subject'] = Header(subject, "utf-8")
    s.sendmail(EMAILCONFIG['sender'], EMAILCONFIG['recipient'], msg.as_string())
    s.quit()
    sys.exit(0)


# endregion

# region database query/update

@exception_logging(log_info='EXECUTING QUERY')
def execute_sql(db, sql, fetch='one', log_flag=True):
    """ 执行SQL语句并获取结果

    Parameters:
        db (DB):
        sql (str):
        fetch (str, optional)
            one: fetch a single value (default)
            many: fetch the first row as a tuple
            df: fetch all as a df
        log_flag (str, optional)
            a flag to log fetched results

    Returns
    -------
    result

    """

    get_logger(False).info(sql)
    with db.connection.cursor() as cursor:
        result = None
        cursor.execute(sql)
        if fetch == 'df':
            cols = [_[0] for _ in cursor.description]
            rows = []
            while True:
                row = cursor.fetchone()
                if row:
                    rows.append(list(row))
                else:
                    break
            if rows:
                df = pd.DataFrame(rows).fillna('')
                df.columns = cols
                result = df
        else:
            results = cursor.fetchone()
            result = results[0] if fetch == 'one' else results
        if log_flag == True:
            utils_logger.info(f'[QUERY RESULT] {str(result)}')
        return result


def get_job_info(db_master, group_id):
    """ 从元数据库获得当前批次任务信息

    Parameters:
    db_master (DB)
    group_id (int)

    Returns:
        pd.DataFrame: df_job
        dict: dict_conn
        dict: dict_param

    """
    with db_master.connection.cursor() as cursor:
        job_cond = f'group_id={group_id} AND is_valid=1' if group_id else 'is_valid=1'
        cursor.execute('OPEN SYMMETRIC KEY DQCSymmetric DECRYPTION BY CERTIFICATE DQCCert')
        sql = f'''
            SELECT P.job_id, job_name, job_desc, group_id, bus_module, job_type, script_value, expected_result, group_name, run_time, is_notify, param_type, P.param_name, param_value, user_name, password, database_type, server_desc, server_name, port_number, database_name FROM 
            (SELECT id, job_name, job_desc, group_id, bus_module, job_type, script_value, expected_result
            FROM {MASTERTBS['JOB'][0]} WHERE {job_cond}) J
            LEFT JOIN
            (SELECT job_id, param_type, param_name, param_value FROM {MASTERTBS['JOBPARAM'][0]} WHERE is_valid=1) P
            ON J.id = P.job_id
            LEFT JOIN 
            (SELECT job_id, param_name, id, user_name, CAST(DecryptByKey(password) AS VARCHAR(100)) AS password, database_type, server_desc, server_name, port_number, database_name 
            FROM (SELECT job_id, param_name, param_value FROM {MASTERTBS['JOBPARAM'][0]} WHERE param_type='connection') a LEFT JOIN (SELECT * FROM {MASTERTBS['JOBCONN'][0]} WHERE is_valid=1) b ON a.param_value=b.id) C
            ON C.job_id = P.job_id AND C.param_name = P.param_name
            LEFT JOIN
            (SELECT id, group_name, run_time, is_notify FROM {MASTERTBS['JOBGROUP'][0]} WHERE is_valid=1) G
            ON J.group_id = G.id
            '''
        df_job_info = execute_sql(db_master, sql, 'df', False)
        cursor.execute('CLOSE SYMMETRIC KEY DQCSymmetric')

        # no job fetched
        if df_job_info is None:
            utils_logger.info(f'[NO JOB IN GROUP {group_id}]')
            return None, None, None

        # jobs fetched
        dict_param = dict()
        for row in df_job_info.itertuples():
            if dict_param.get(row.job_id, None):
                dict_param[row.job_id][row.param_name] = row.param_value
            else:
                dict_param[row.job_id] = {row.param_name: row.param_value, }
        df_job = df_job_info.loc[:,
                 ['job_id', 'job_name', 'job_desc', 'group_id', 'bus_module', 'job_type', 'script_value',
                  'expected_result', 'group_name', 'run_time', 'is_notify']].drop_duplicates().set_index('job_id',
                                                                                                         drop=False)
        df_conn = df_job_info.loc[
            df_job_info['user_name'] != '', ['param_value', 'user_name', 'password', 'database_type', 'server_desc',
                                             'server_name', 'port_number',
                                             'database_name']].drop_duplicates().set_index('param_value')
        dict_conn = df_conn.to_dict('index')
        return df_job, dict_conn, dict_param


@exception_logging('INITIALIZING LOG TABLE')
def init_logtb(db, init_logs):
    """ 日志表初始化


    """
    with db.connection.cursor() as cursor:
        # move data in log table into log_his table
        cursor.execute(f'''INSERT INTO {MASTERTBS['LOGHIS'][0]} SELECT * FROM {MASTERTBS['LOG'][0]}''')
        cursor.execute(f'''TRUNCATE TABLE {MASTERTBS['LOG'][0]}''')
        # add new job data to log table
        sql = f'''INSERT INTO {MASTERTBS['LOG'][0]} VALUES {", ".join(init_logs)}'''
        get_logger(False).info(sql)
        cursor.execute(sql)
        db.connection.commit()


@exception_logging('UPDATING LOG')
def update_logtb(job, db, update_type, update_dict):
    """ 日志表更新

    """

    with db.connection.cursor() as cursor:
        if update_type == 'begin':
            job.begin_time = datetime.now(tz)
            update_dict['job_begin_time'] = job.begin_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elif update_type == 'end':
            job.end_time = datetime.now(tz)
            update_dict['job_end_time'] = job.end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            time_str = str(job.end_time - job.begin_time)
            update_dict['sum_running_time'] = round(
                float(time_str.split('.')[1]) / 1000000 + float(time_str.split(':')[2].split('.')[0]) + float(
                    time_str.split(':')[1]) * 60 + float(time_str.split(':')[0]) * 3600, 3)
        update_dict['update_time'] = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        update_str = ', '.join([f'{_[0]}={_[1]!r}' for _ in list(update_dict.items())])
        sql = f'''UPDATE {MASTERTBS['LOG'][0]} set {update_str} where job_id = {job.id}'''
        get_logger(False).info(sql)
        cursor.execute(sql)
        db.connection.commit()

# endregion
