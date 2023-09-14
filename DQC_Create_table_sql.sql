--连接信息配置表
DROP TABLE IF EXISTS [dbo].[t_check_database_conn_info];
CREATE TABLE [dbo].[t_check_database_conn_info] (
	id	INT PRIMARY KEY
	,user_name	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,password	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,database_type	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS
	,server_desc	NVARCHAR(500) COLLATE Chinese_PRC_90_CI_AS
	,server_name	NVARCHAR(200) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,port_number	INT
	,database_name	NVARCHAR(200) COLLATE Chinese_PRC_90_CI_AS
	,is_valid	INT  NOT NULL
	,insert_time	DATETIME DEFAULT CURRENT_TIMESTAMP
	,update_time	DATETIME DEFAULT CURRENT_TIMESTAMP
);
--为表及字段添加描述信息
EXECUTE sp_addextendedproperty N'MS_Description', '连接信息配置表', N'user', N'dbo', N'table', N't_check_database_conn_info', NULL, NULL
EXECUTE sp_addextendedproperty N'MS_Description', 'ID', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'id'
EXECUTE sp_addextendedproperty N'MS_Description', '用户名', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'user_name'
EXECUTE sp_addextendedproperty N'MS_Description', '密码', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'password'
EXECUTE sp_addextendedproperty N'MS_Description', '数据库类型', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'database_type'
EXECUTE sp_addextendedproperty N'MS_Description', '描述', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'server_desc'
EXECUTE sp_addextendedproperty N'MS_Description', 'IP地址', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'server_name'
EXECUTE sp_addextendedproperty N'MS_Description', '端口号', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'port_number'
EXECUTE sp_addextendedproperty N'MS_Description', '数据库名称', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'database_name'
EXECUTE sp_addextendedproperty N'MS_Description', '是否生效', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'is_valid'
EXECUTE sp_addextendedproperty N'MS_Description', '插入时间', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'insert_time'
EXECUTE sp_addextendedproperty N'MS_Description', '更新时间', N'user', N'dbo', N'table', N't_check_database_conn_info', N'column', N'update_time'


--创建数据库主密钥
CREATE master key  ENCRYPTION BY PASSWORD ='passW@ord'
--创建证书
CREATE CERTIFICATE DQCCert with SUBJECT = 'DQC Certificate'
--创建对称密钥
CREATE SYMMETRIC KEY DQCSymmetric WITH ALGORITHM = AES_256
    ENCRYPTION BY CERTIFICATE DQCCert 
--使用对称秘钥加密数据		
OPEN SYMMETRIC KEY DQCSymmetric DECRYPTION BY CERTIFICATE DQCCert;
INSERT INTO dbo.t_check_database_conn_info 
(
	id
	,user_name
	,password
	,database_type
	,server_desc
	,server_name
	,port_number
	,database_name
	,is_valid
	,insert_time
	,update_time
)
VALUES 
(3,'MW_USER', ENCRYPTBYKEY(Key_Guid(N'DQCSymmetric'),'McQuery2017#05'), 'MSSQL', 'ACE', '172.19.121.198', '1433', 'amore', '1',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
;
CLOSE SYMMETRIC KEY DQCSymmetric;

--解密
OPEN SYMMETRIC KEY DQCSymmetric DECRYPTION BY CERTIFICATE DQCCert;
SELECT  CAST(DecryptByKey(password) as varchar(100)) Password FROM t_check_database_conn_info;
CLOSE SYMMETRIC KEY DQCSymmetric;



--校验组
DROP TABLE IF EXISTS [dbo].[t_check_group];
CREATE TABLE [dbo].[t_check_group] (
	id	INT PRIMARY KEY
	,group_name	NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,run_time	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,is_notify	INT
	,is_valid	INT  NOT NULL
	,insert_time	DATETIME DEFAULT CURRENT_TIMESTAMP
	,update_time	DATETIME DEFAULT CURRENT_TIMESTAMP
);
--为表及字段添加描述信息
EXECUTE sp_addextendedproperty N'MS_Description', '校验组', N'user', N'dbo', N'table', N't_check_group', NULL, NULL
EXECUTE sp_addextendedproperty N'MS_Description', '校检组ID', N'user', N'dbo', N'table', N't_check_group', N'column', N'id'
EXECUTE sp_addextendedproperty N'MS_Description', '校检组名称', N'user', N'dbo', N'table', N't_check_group', N'column', N'group_name'
EXECUTE sp_addextendedproperty N'MS_Description', '运行时间', N'user', N'dbo', N'table', N't_check_group', N'column', N'run_time'
EXECUTE sp_addextendedproperty N'MS_Description', '是否通知', N'user', N'dbo', N'table', N't_check_group', N'column', N'is_notify'
EXECUTE sp_addextendedproperty N'MS_Description', '是否生效', N'user', N'dbo', N'table', N't_check_group', N'column', N'is_valid'
EXECUTE sp_addextendedproperty N'MS_Description', '插入时间', N'user', N'dbo', N'table', N't_check_group', N'column', N'insert_time'
EXECUTE sp_addextendedproperty N'MS_Description', '更新时间', N'user', N'dbo', N'table', N't_check_group', N'column', N'update_time'


--校验任务
DROP TABLE IF EXISTS [dbo].[t_check_job];
CREATE TABLE [dbo].[t_check_job] (
	id	INT PRIMARY KEY
	,job_name	NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,job_desc	NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,group_id	INT
	,bus_module	NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,job_type	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,script_value	NVARCHAR(4000) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,expected_result	NVARCHAR(500) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,is_valid	INT  NOT NULL
	,insert_time	DATETIME DEFAULT CURRENT_TIMESTAMP
	,update_time	DATETIME DEFAULT CURRENT_TIMESTAMP
);
--为表及字段添加描述信息
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务表', N'user', N'dbo', N'table', N't_check_job', NULL, NULL
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务ID', N'user', N'dbo', N'table', N't_check_job', N'column', N'id'
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务名称', N'user', N'dbo', N'table', N't_check_job', N'column', N'job_name'
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务描述', N'user', N'dbo', N'table', N't_check_job', N'column', N'job_desc'
EXECUTE sp_addextendedproperty N'MS_Description', '校验组ID', N'user', N'dbo', N'table', N't_check_job', N'column', N'group_id'
EXECUTE sp_addextendedproperty N'MS_Description', '业务板块', N'user', N'dbo', N'table', N't_check_job', N'column', N'bus_module'
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务类型', N'user', N'dbo', N'table', N't_check_job', N'column', N'job_type'
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务SQL', N'user', N'dbo', N'table', N't_check_job', N'column', N'script_value'
EXECUTE sp_addextendedproperty N'MS_Description', '预期结果', N'user', N'dbo', N'table', N't_check_job', N'column', N'expected_result'
EXECUTE sp_addextendedproperty N'MS_Description', '是否生效', N'user', N'dbo', N'table', N't_check_job', N'column', N'is_valid'
EXECUTE sp_addextendedproperty N'MS_Description', '插入时间', N'user', N'dbo', N'table', N't_check_job', N'column', N'insert_time'
EXECUTE sp_addextendedproperty N'MS_Description', '更新时间', N'user', N'dbo', N'table', N't_check_job', N'column', N'update_time'

--校验参数表
DROP TABLE IF EXISTS [dbo].[t_check_param];
CREATE TABLE [dbo].[t_check_param] (
	job_id	INT PRIMARY KEY
	,param_type NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,param_name	NVARCHAR(100) COLLATE PRIMARY KEY Chinese_PRC_90_CI_AS NOT NULL
	,param_value	NVARCHAR(4000) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,is_valid	INT  NOT NULL
	,insert_time	DATETIME DEFAULT CURRENT_TIMESTAMP
	,update_time	DATETIME DEFAULT CURRENT_TIMESTAMP
);
--为表及字段添加描述信息
EXECUTE sp_addextendedproperty N'MS_Description', '校验参数表', N'user', N'dbo', N'table', N't_check_param', NULL, NULL
EXECUTE sp_addextendedproperty N'MS_Description', '任务ID', N'user', N'dbo', N'table', N't_check_param', N'column', N'job_id'
EXECUTE sp_addextendedproperty N'MS_Description', '参数类型', N'user', N'dbo', N'table', N't_check_param', N'column', N'param_type'
EXECUTE sp_addextendedproperty N'MS_Description', '参数名称', N'user', N'dbo', N'table', N't_check_param', N'column', N'param_name'
EXECUTE sp_addextendedproperty N'MS_Description', '参数值', N'user', N'dbo', N'table', N't_check_param', N'column', N'param_value'
EXECUTE sp_addextendedproperty N'MS_Description', '是否生效', N'user', N'dbo', N'table', N't_check_param', N'column', N'is_valid'
EXECUTE sp_addextendedproperty N'MS_Description', '插入时间', N'user', N'dbo', N'table', N't_check_param', N'column', N'insert_time'
EXECUTE sp_addextendedproperty N'MS_Description', '更新时间', N'user', N'dbo', N'table', N't_check_param', N'column', N'update_time'


--校验日志表
DROP TABLE IF EXISTS [dbo].[t_check_log];
CREATE TABLE [dbo].[t_check_log] (
	run_id	NCHAR(14) PRIMARY KEY COLLATE Chinese_PRC_90_CI_AS NOT NULL 
	,group_name	NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,job_id	INT PRIMARY KEY
	,job_name	NVARCHAR(200) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,run_status	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,job_begin_time	DATETIME
	,job_end_time	DATETIME
	,sum_running_time	BIGINT
	,check_result	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,insert_time	DATETIME DEFAULT CURRENT_TIMESTAMP
	,update_time	DATETIME DEFAULT CURRENT_TIMESTAMP
);
--为表及字段添加描述信息
EXECUTE sp_addextendedproperty N'MS_Description', '校验日志表', N'user', N'dbo', N'table', N't_check_log', NULL, NULL
EXECUTE sp_addextendedproperty N'MS_Description', '运行批次', N'user', N'dbo', N'table', N't_check_log', N'column', N'run_id'
EXECUTE sp_addextendedproperty N'MS_Description', '校验组名称', N'user', N'dbo', N'table', N't_check_log', N'column', N'group_name'
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务ID', N'user', N'dbo', N'table', N't_check_log', N'column', N'job_id'
EXECUTE sp_addextendedproperty N'MS_Description', '检验任务名称', N'user', N'dbo', N'table', N't_check_log', N'column', N'job_name'
EXECUTE sp_addextendedproperty N'MS_Description', '运行状态', N'user', N'dbo', N'table', N't_check_log', N'column', N'run_status'
EXECUTE sp_addextendedproperty N'MS_Description', '开始时间', N'user', N'dbo', N'table', N't_check_log', N'column', N'job_begin_time'
EXECUTE sp_addextendedproperty N'MS_Description', '结束时间', N'user', N'dbo', N'table', N't_check_log', N'column', N'job_end_time'
EXECUTE sp_addextendedproperty N'MS_Description', '运行时长', N'user', N'dbo', N'table', N't_check_log', N'column', N'sum_running_time'
EXECUTE sp_addextendedproperty N'MS_Description', '校验结果', N'user', N'dbo', N'table', N't_check_log', N'column', N'check_result'
EXECUTE sp_addextendedproperty N'MS_Description', '插入时间', N'user', N'dbo', N'table', N't_check_log', N'column', N'insert_time'
EXECUTE sp_addextendedproperty N'MS_Description', '更新时间', N'user', N'dbo', N'table', N't_check_log', N'column', N'update_time'



--校验历史日志表
DROP TABLE IF EXISTS [dbo].[t_check_log_his];
CREATE TABLE [dbo].[t_check_log_his] (
	run_id	NCHAR(14) PRIMARY KEY COLLATE Chinese_PRC_90_CI_AS NOT NULL 
	,group_name	NVARCHAR(100) COLLATE Chinese_PRC_90_CI_AS NOT NULL
	,job_id	INT PRIMARY KEY
	,job_name	NVARCHAR(200) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,run_status	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,job_begin_time	DATETIME
	,job_end_time	DATETIME
	,sum_running_time	BIGINT
	,check_result	NVARCHAR(50) COLLATE Chinese_PRC_90_CI_AS  NOT NULL
	,insert_time	DATETIME DEFAULT CURRENT_TIMESTAMP
	,update_time	DATETIME DEFAULT CURRENT_TIMESTAMP
);
--为表及字段添加描述信息
EXECUTE sp_addextendedproperty N'MS_Description', '校验日志表', N'user', N'dbo', N'table', N't_check_log_his', NULL, NULL
EXECUTE sp_addextendedproperty N'MS_Description', '运行批次', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'run_id'
EXECUTE sp_addextendedproperty N'MS_Description', '校验组名称', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'group_name'
EXECUTE sp_addextendedproperty N'MS_Description', '校验任务ID', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'job_id'
EXECUTE sp_addextendedproperty N'MS_Description', '检验任务名称', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'job_name'
EXECUTE sp_addextendedproperty N'MS_Description', '运行状态', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'run_status'
EXECUTE sp_addextendedproperty N'MS_Description', '开始时间', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'job_begin_time'
EXECUTE sp_addextendedproperty N'MS_Description', '结束时间', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'job_end_time'
EXECUTE sp_addextendedproperty N'MS_Description', '运行时长', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'sum_running_time'
EXECUTE sp_addextendedproperty N'MS_Description', '校验结果', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'check_result'
EXECUTE sp_addextendedproperty N'MS_Description', '插入时间', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'insert_time'
EXECUTE sp_addextendedproperty N'MS_Description', '更新时间', N'user', N'dbo', N'table', N't_check_log_his', N'column', N'update_time'

