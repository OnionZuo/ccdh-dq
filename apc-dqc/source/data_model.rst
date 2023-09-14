.. _`data_model`:

===========
数据模型
===========

.. image:: data_model.png
  :width: 600
  :align: center 
  :alt: data model

校验任务表
----------------
用于存储校验任务的主要配置信息，包括任务所属校验组，任务脚本类型，任务脚本，和脚本运行预期结果等。

.. list-table:: 
   :widths: 20 20 70
   :header-rows: 1

   * - 字段名称
     - 字段类型
     - 描述
   * - id
     - int
     - 主键
   * - job_name
     - nvarchar 
     - 示例：``null_check_fdt_stock_sl_recpt``
   * - job_desc
     - nvarchar 
     - 示例：``非空检查``
   * - group_id	
     - int 
     - 外键 (校验组表)
   * - bus_module
     - nvarchar
     - 示例：  ``stock`` | ``order`` | ...
   * - job_type
     - nvarchar  
     - 值：``sql`` | ``python`` | ...
   * - script_value
     - nvarchar 
     - 带参数SQL语句或Python函数名
       示例：``select count(1) from (select * from ${table_1} where ${filter_1})`` | ``check_two_db_template``
   * - expected_result
     - nvarchar 
     - 用于和脚本返回结果比对的值
       示例：``0``
   * - is_valid
     - int
     - 值：``0`` | ``1``
   * - insert_time
     - datetime
     - 
   * - update_time
     - datetime
     -   


参数表
----------------
用于存储校验任务运行所需参数，包括任务连接ID，任务脚本参数等。

.. list-table:: 
   :widths: 20 20 70
   :header-rows: 1

   
   * - 字段名称
     - 字段类型
     - 描述
   * - job_id	
     - int 
     - 外键 (校验任务表)   
   * - param_type
     - nvarchar
     - 值：``column`` | ``connection`` | ``filter`` | ``table``
   * - param_name
     - nvarchar  
     - 对应校验任务表校验任务脚本中的参数
       示例：``column_1`` | ``connection_1`` | ``filter_1`` | ``table_1``
   * - param_value
     - nvarchar 
     - 脚本参数值或校验任务连接id (param_type=connection)
       示例：``src_recpt_id`` | ``2`` | ``effective_to_date='9999-12-31'`` | ``fdt.fdt_stock_sl_recpt``
   * - is_valid
     - int
     - 值：``0`` | ``1``
   * - insert_time
     - datetime
     - 
   * - update_time
     - datetime
     -     


校验组表
----------------
用于存储校验组信息，其中运行时间将用于生成定时运行配置文件，另外可以单独设置是否邮件通知运行结果。

.. list-table:: 
   :widths: 20 20 70
   :header-rows: 1


   * - 字段名称
     - 字段类型
     - 描述
   * - id	
     - int 
     - 主键   
   * - group_name
     - nvarchar
     - 
   * - run_time
     - nvarchar  
     - Cron时间表达式 (`在线生成工具 <https://qqe2.com/cron/index>`)
   * - is_notify	
     - int 
     - 值：``0`` | ``1``
   * - is_valid
     - int
     - 值：``0`` | ``1``
   * - insert_time
     - datetime
     - 
   * - update_time
     - datetime
     -     


连接信息配置表
----------------
用于存储任务元数据库和任务脚本连接数据库的信息。

.. important::

    元数据库信息需要存为 **id=1**

.. list-table:: 
   :widths: 20 20 70
   :header-rows: 1


   * - 字段名称
     - 字段类型
     - 描述
   * - id	
     - int 
     - 主键 (对应参数表连接参数值)   
   * - user_name
     - nvarchar
     - 
   * - password
     - nvarchar  
     - 
   * - database_type	
     - nvarchar 
     - 值：``MSSQL`` | ``REDSHIFT`` | ...
   * - server_desc
     - nvarchar 
     - 
   * - server_name	
     - nvarchar 
     - 主机域名或IP地址
   * - port_number
     - int
     - 
   * - database_name
     - nvarchar
     - 
   * - insert_time
     - datetime
     - 
   * - update_time
     - datetime
     -     

.. _`log-table`:

日志表
----------------
用于存储当前批次任务的运行时间，状态，结果等。

.. list-table:: 
   :widths: 20 20 70
   :header-rows: 1

   * - 字段名称
     - 字段类型
     - 描述
   * - run_id	
     - nchar(14) 
     - 主键，任务开始运行时间
       格式：``yyyymmddhhmmss``，示例：``202105311430``
   * - group_name
     - nvarchar
     - 
   * - job_id
     - int  
     - 对应执行该任务批次时校验任务表的任务ID
   * - job_name
     - nvarchar 
     - 值：对应校验任务表的任务名称
   * - run_status	
     - nvarchar 
     - 值：``READY`` (准备运行) | ``RUNNING`` (正在运行) | ``FINISHED`` (运行结束) | ``FAILED`` (运行错误)
   * - job_begin_time	
     - datetime 
     - 
   * - job_end_time
     - datetime
     - 
   * - sum_running_time
     - numeric(10, 3)
     - 
   * - check_result
     - int
     - 脚本运行和预期比对结果
       值：``1`` (一致) | ``0`` (不一致) | ``-1`` (任务运行错误)
   * - insert_time
     - datetime
     - 
   * - update_time
     - datetime
     -     


历史日志表
----------------
用于存储历史运行批次任务日志，每个新批次开始运行前脚本会自动将日志表中全部数据移入历史日志表。