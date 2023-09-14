from utils import exception_logging
import utils
import pyscript

DEFAULT = 'DEFAULT'
NULL = 'NULL'
logger = utils.get_logger()


class Job:
    """ A class used to represent a checking job

    Args:
        run_id (int): 当前运行批次ID
        job_detail (tuple): 校验任务信息
        job_params (dict): 校验任务参数

    Attributes:
        id (int)
        name (str)
        desc (str)
        job_type (str)
        expected_result (str)
        run_result (str): the value returned after executing the job script
        check_result (int): indicator of whether the checking job passed
        params (dict)
        begin_time (str)
        end_time (str)
        log (str): string of values to initialize log table
        script (str): script value with parameter values inserted (sql job) / function name (python job)
        connid (str): connection id of the job  (sql job) / None (non-sql job)

    Methods:
        run(dbs): run the job and assign run_result to the job instance
    """
    def __init__(self, run_id, job_detail, job_params):
        self.id = job_detail.job_id
        self.name = job_detail.job_name
        self.desc = job_detail.job_desc
        self.job_type = job_detail.job_type
        self.expected_result = job_detail.expected_result
        self.run_result = None
        self.check_result = None
        self.params = job_params[self.id]
        self.begin_time = None
        self.end_time = None
        self.log = f'''({run_id!r}, {job_detail.group_name!r}, {self.id!r}, {job_detail.job_name!r}, 'READY', 
            {NULL}, {NULL}, {NULL}, 0, {DEFAULT}, {DEFAULT})'''
        self.script = job_detail.script_value
        if self.job_type == 'sql':
            self.connid = self.params['connection_1']
            for param in self.params:
                self.script = self.script.replace('${' + param + '}', self.params[param])
        else:
            self.connid = None

    @exception_logging('RUNNING JOB SCRIPT')
    def run(self, dbs):
        """ 执行当前校验任务的脚本

        Args:
            dbs (list): 所有任务的数据库类实例

        Returns:
            None
        """

        logger.info(f'[EXPECTED RESULT] {self.expected_result}')
        if self.job_type == 'sql':
            self.run_result = utils.execute_sql(dbs[self.connid], self.script)
        elif self.job_type == 'python':
            getattr(pyscript, self.script)(self, dbs)
