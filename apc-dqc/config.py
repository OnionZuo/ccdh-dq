""" 脚本变量配置"""

TZ = 'Asia/Shanghai'
"""程序输出日志中时间的时区"""

ODBCDRIVER = 'ODBC Driver 13 for SQL Server'
"""程序连接SQL Server使用的ODBC驱动"""

DEVCONN = {
    'host': 'bigdata-prd-db-sqlsever-rds-beijing.cudupqbpop8x.rds.cn-north-1.amazonaws.com.cn',
    'database': 'idas',
    'port': 1433,
    'user': 'bigdataprddb',
    'password': 'dbpassword',
    }
"""元数据库的连接信息，同元数据库连接信息配置表ID=1的连接信息"""

MASTERTBS = {
    'LOG': (
        't_check_log', 
        ('run_id', 'group_name', 'job_id', 'job_name', 'run_status', 
         'job_begin_time', 'job_end_time', 'sum_running_time', 
         'check_result', 'insert_time', 'update_time')
        ), 
    'LOGHIS': (
        't_check_log_his',
        ('run_id', 'group_name', 'job_id', 'job_name', 'run_status', 
         'job_begin_time', 'job_end_time', 'sum_running_time', 
         'check_result', 'insert_time', 'update_time')
        ), 
    'JOB': (
        't_check_job',
        ('id', 'job_name', 'job_desc', 'group_id', 'bus_module', 
         'job_type', 'script_value', 'expected_result', 
         'is_valid', 'insert_time', 'update_time')
        ), 
    'JOBGROUP': (
        't_check_group',
        ('id', 'group_name', 'run_time', 'is_notify', 'is_valid',
         'insert_time', 'update_time')
        ), 
    'JOBCONN': (
        't_check_database_conn_info',
        ('id', 'user_name', 'password', 'database_type',
         'server_desc', 'server_name', 'port_nimber',
         'database_name', 'is_valid', 'insert_time')
        ),
    'JOBPARAM': (
        't_check_param',
        ('job_id', 'param_type', 'param_name', 'param_value',
         'is_valid', 'insert_time', 'update_time')
        ),
}
"""元数据库的表信息"""

EMAILCONFIG = {
    'sender':'bdsupport@cn.amorepacific.com', 
    'recipient': ['yingtong.liu@bizfocus.cn', 'vivian.chen@bizfocus.cn', ], 
    'password':'idas202006',
    'smtp_port':25, 
    'smtp_host':'172.19.121.180',
    'smtp_ssl':False
}
"""邮件通知配置，包括发件邮箱账号、密码、服务器端口，收件人等"""

EMAIL_TMPL ='''
<html>
    <head>
        <style type="text/css">
            html,
            body,
            * {{
                font-family: Microsoft YaHei UI, sans-serif;
                margin-block-start: 0.2em !important;
                margin-block-end: 0.2em !important;
            }}
            p {{
                
                font-size: 14px;
                white-space: pre-line
            }}
            h2 {{
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
    ${body}
    </body>
</html>
'''
"""通用邮件模板，可以使用CSS语言自定义格式"""

EMAIL_SUCCESS = EMAIL_TMPL.replace('${body}','''
        {summary}
        <br><h2>📝 job running detail</h2>
        <br><p>running failed:</p>
        <span style="color:red">{error_content}</span>
        <br><p>check failed:</p>
        <span style="color:red">{fail_content}</span>
        <br><p>check passed:</p>
        <span style="color:green"> {pass_content}</span>
        <br><h2>🧾 log content</h2>
        <br><p>{log_content}</p>''')
"""任务成功邮件模板，默认包含任务成功失败明细和输出日志文件内容"""

EMAIL_FAIL = EMAIL_TMPL.replace('${body}','''
        <br><h2>🧾 log content</h2>
        <br><p>{log_content}</p>''')
"""任务失败邮件模板，默认包含输出日志文件内容"""