.. rst-class:: nonmodule

=====================
配置和运行
=====================

.. contents::
   :local:
   :depth: 3


配置
---------------------
为了使用DQC脚本自动执行校验任务，需要在元数据库和项目脚本进行配置，以下提供配置示例。


通用配置
~~~~~~~~~~~~~~~~~~~~~~~

.. tabs::

   .. tab:: 元数据库

       将元数据连接信息以id=1存储在 :ref:`连接信息配置表`：

       .. list-table::
          :widths: 5 5 5 5 5 60 5 5 5
          :header-rows: 1

          * - id
            - user_name
            - password
            - database_type
            - server_desc
            - server_name
            - port_number
            - database_name
            - is_valid
          * - 1
            - 'bigdataprddb'
            - 'your-password'
            - 'MSSQL'
            - 'Portal'
            - 'bigdata-prd-db-sqlsever-rds-beijing.cudupqbpop8x.rds.cn-north-1.amazonaws.com.cn'
            - 1433
            - 'idas'
            - 1

   .. tab:: 校验组表

       在 :ref:`校验组表` 配置校验组信息：

       .. list-table::
          :widths: 12 22 22 22 22
          :header-rows: 1

          * - id
            - group_name
            - run_time
            - is_notify
            - is_valid
          * - 1
            - 'Daily_check'
            - '10 0 \* \* \*'
            - 1
            - 1

   .. tab:: 其他

      Python脚本 ``config.py`` 中另外需要对一些变量进行配置，具体请参照 :ref:`config-module`。

任务配置
~~~~~~~~~~
当前支持的任务类型包括SQL任务和Python任务，以下为不同类型校验任务示例

SQL任务
""""""""""

``示例一：检验是否主键唯一``
''''''''''''''''''''''''''''''''''''''''
该任务需要实现连接IDAS服务器的prd数据库并执行以下查询语句

.. code-block:: sql

    SELECT  COUNT(1)
    FROM 
    (
        SELECT  src_recpt_id
        FROM fdt.fdt_stock_sl_recpt
        WHERE effective_to_date='9999-12-31' 
        GROUP BY  src_recpt_id
        HAVING COUNT(1)>1
    ) 

任务配置如下：

.. tabs::

   .. tab:: 校验任务表

      .. list-table::
         :widths: 20 20 60
         :header-rows: 1

         * - 字段名称 (en)
           - 字段名称
           - 值
         * - id
           - 校验任务ID
           - 1
         * - job_name
           - 校验任务名称
           - 'unique_primary_key_fdt_stock_sl_recpt'
         * - job_desc
           - 校验任务描述
           - '校验主键是否唯一'
         * - group_id
           - 校验组ID
           - 1
         * - bus_module
           - 业务板块
           - 'stock'
         * - job_type
           - 校验任务类型
           - 'sql'
         * - script_value
           - 校验任务脚本
           - 'select count(1) from(select ${column_1} from ${table_1} where $filter_1} group by ${column_1} having count(1)>1'
         * - expected_result
           - 预期结果
           - '0'
         * - is_valid
           - 是否生效
           - 1

   .. tab:: 参数表

      .. list-table::
         :widths: 12 22 22 22 22
         :header-rows: 1

         * - job_id
           - param_type
           - param_name
           - param_value
           - is_valid
         * - 1
           - 'column'
           - 'column_1'
           - 'src_recpt_id'
           - 1
         * - 1
           - 'connection'
           - 'connection_1'
           - '2'
           - 1
         * - 1
           - 'filter'
           - 'filter_1'
           - 'effective_to_date="9999-12-31"'
           - 1
         * - 1
           - 'table'
           - 'table_1'
           - 'fdt.fdt_stock_sl_recpt'
           - 1

   .. tab:: 连接信息配置表

      .. list-table::
         :widths: 5 5 5 5 5 60 5 5 5
         :header-rows: 1

         * - id
           - user_name
           - password
           - database_type
           - server_desc
           - server_name
           - port_number
           - database_name
           - is_valid
         * - 2
           - 'idas_etl'
           - 'your-password'
           - 'REDSHIFT'
           - 'IDAS'
           - 'apcbigdata-prd-redshift-prd-beijing-a.caitnxyxi7ef.cn-north-1.redshift.amazonaws.com.cn'
           - 5439
           - 'prd'
           - 1

.. seealso::

   :ref:`data_model` : :ref:`校验任务表`，:ref:`参数表`，:ref:`连接信息配置表`

Python任务
""""""""""""""""""""

``示例一：检验是否符合业务规则``
''''''''''''''''''''''''''''''''''''''''

该任务需要实现连接IDAS服务器的prd数据库和ACE服务器的amore数据库，并分别执行以下查询语句

.. code-block:: sql

    -- 查询1：连接IDAS
    SELECT  SUM(txn_qty) qty, 
            SUM(txn_amt) amt
    FROM gdt.gdt_stk_sl_fct_stk_txn tx
    WHERE shop_no=999998 AND tx.org_brand_id=1001 AND left(dim_date_id,6)=202104 AND txn_code=9 AND txn_direction=2 AND area_type=1;

    -- 查询2：连接ACE
    DECLARE @month VARCHAR(10)

    SET @month='2021-04'
    SELECT  SUM(count)*-1       AS qty,
            SUM(price*count)*-1 AS amt
    FROM 
    (
      SELECT  a.id, fromlogicid, logicstockname AS fromstockname
      FROM  tock_t_stock_receipt a with(nolock)
      INNER JOIN stock_t_logic_stock c with(nolock) ON a.fromlogicid=c.id
      WHERE a.customerid=1001 AND receipttype=9 AND convert(varchar(7), submitdate,120)=@month AND a.fromlogicid=18 
    )ar
    INNER JOIN 
    (
      SELECT  a.id, convert(varchar(100),submitdate,112) AS saledate, e.dealerid, dealername, a.tologicid, c.logicstockname AS tostockname, manufacturercode, count, price
      FROM stock_t_stock_receipt a
      INNER JOIN stock_tr_stock_receipt_sku b with(nolock) ON a.id=b.receiptid
      INNER JOIN stock_t_logic_stock c with(nolock) ON a.tologicid=c.id
      INNER JOIN user_t_organization d with(nolock) ON d.id=a.fromorgid
      INNER JOIN user_t_dealer e with(nolock) ON e.id=d.dealerid
      INNER JOIN product_t_sku f with(nolock) ON b.skuid=f.id
      INNER JOIN product_t_product g with(nolock) ON f.productid=g.id
      WHERE a.customerid=1001 AND receipttype=9 AND convert(varchar(7), submitdate,120)=@month AND a.tologicid!=18 AND processnodestep='end' AND d.type=2  
    )sr ON ar.id=sr.id;

任务配置如下：

.. tabs::

   .. tab:: Python脚本

      对于Python任务，需要在 :ref:`pyscript 模块` 里将任务脚本定义为函数，函数名即之后配置在校验任务表内的校验任务脚本值，该任务脚本如下：

      .. code-block:: python

          def check_two_db_template(job, dbs):
              db_1 = dbs[job.params['connection_1']]
              db_2 = dbs[job.params['connection_2']]
              script_1 = job.params['script_1']
              script_2 = job.params['script_2']
              run_results = (utils.execute_sql(db_1, script_1, 'many'),utils.execute_sql(db_2, script_2, 'many'))
              job.run_result  =  sum(tuple(map(lambda i, j: i - j, run_results[0], run_results[1]))) # 用于和任务预期结果比对的值

   .. tab:: 校验任务表

      .. list-table::
         :widths: 20 20 60
         :header-rows: 1

         * - 字段名称 (en)
           - 字段名称
           - 值
         * - id
           - 校验任务ID
           - 8
         * - job_name
           - 校验任务名称
           - 'bus_logic_gdt_stk_sl_fct_stk_txn'
         * - job_desc
           - 校验任务描述
           - '校验业务逻辑是否正确'
         * - group_id
           - 校验组ID
           - 1
         * - bus_module
           - 业务板块
           - 'stock'
         * - job_type
           - 校验任务类型
           - 'python'
         * - script_value
           - 校验任务脚本
           - 'check_two_db_template'
         * - expected_result
           - 预期结果
           - '0'
         * - is_valid
           - 是否生效
           - 1

   .. tab:: 参数表

      .. list-table::
         :widths: 12 22 22 22 22
         :header-rows: 1

         * - job_id
           - param_type
           - param_name
           - param_value
           - is_valid
         * - 8
           - 'connection'
           - 'connection_1'
           - '2'
           - 1
         * - 8
           - 'connection'
           - 'connection_2'
           - '3'
           - 1
         * - 8
           - 'script'
           - 'script_1'
           - *查询1脚本字符串*
           - 1
         * - 8
           - 'script'
           - 'script_2'
           - *查询2脚本字符串*
           - 1

   .. tab:: 连接信息配置表

      .. list-table::
        :widths: 5 5 5 5 5 60 5 5 5
        :header-rows: 1


        * - id
          - user_name
          - password
          - database_type
          - server_desc
          - server_name
          - port_number
          - database_name
          - is_valid
        * - 2
          - 'idas_etl'
          - 'your-password'
          - 'REDSHIFT'
          - 'IDAS'
          - 'apcbigdata-prd-redshift-prd-beijing-a.caitnxyxi7ef.cn-north-1.redshift.amazonaws.com.cn'
          - 5439
          - 'prd'
          - 1
        * - 3
          - 'MW_USER'
          - 'your-password'
          - 'MSSQL'
          - 'ACE'
          - '172.19.121.198'
          - 1433
          - 'amore'
          - 1

.. tip::

   同一类型的不同Python任务可以共用一个脚本。

.. seealso::

   :ref:`data_model` > :ref:`校验任务表`，:ref:`参数表`，:ref:`连接信息配置表`

程序运行
-----------------
目前DQC程序将顺序执行在元数据库中配置的任务，支持命令行参数指定校验组。

命令行运行
~~~~~~~~~~~~~
按照 :ref:`安装和部署` 准备好环境后，可使用以下命令运行程序：

.. prompt:: bash

    source dqc/bin/activate  # 激活项目虚拟环境
    python3 run.py           # 不指定校验组
    python3 -groupid 1       # 指定校验组，该命令将运行校验组id=1的任务


Cron定时任务
~~~~~~~~~~~~~~
为了让程序定期自动执行，可以在linux上使用crontab指令使系统自动在指定的时间执行命令。


.. seealso::

   * `调度系统任务（任务）— Oracle系统管理指南`_
   * `crontab - Unix, Linux Command — Tutorialspoint`_

.. _`调度系统任务（任务）— Oracle系统管理指南`: https://docs.oracle.com/cd/E38902_01/html/819-6951/sysrescron-18108.html
.. _`crontab - Unix, Linux Command — Tutorialspoint`: https://www.tutorialspoint.com/unix_commands/crontab.htm

以下为命令示例：

.. prompt:: bash

  crontab -e # 为当前用户创建crontab文件


.. code:: 

  # 在 crontab 文件内
  10 0 * * *  /home/user/dqc/bin/python /home/user/dqcdev/run.py -groupid 1
   0 2 * * *  /home/user/dqc/bin/python /home/user/dqcdev/run.py -groupid 2

.. note::

  由于程序需要在创建的虚拟环境中运行，以上cron任务命令中使用Python解释器 ``/home/user/dqc/bin/python`` 运行 ``/home/user/dqcdev/run.py``，另外，该命令使用 ``-groupid`` 传入校验组参数。关于Python解释器和参数传入可以参考 `Python解释器 — Python文档`_

.. _`Python解释器 — Python文档`: https://docs.python.org/zh-cn/3/tutorial/interpreter.html


.. prompt:: bash

  crontab -l  # 显示当前用户的crontab文件
