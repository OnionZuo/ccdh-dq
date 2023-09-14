.. DQC documentation master file, created by
   sphinx-quickstart on Fri May 28 14:05:03 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======================
DQC文档
=======================
DQC（数据质量控制）旨在基于一系列规则制定数据质量校验任务，通过系统定时调用任务程序主动捕获ETL错误，确保数据仓库的数据质量。常见任务包括主键唯一，非空，拉链正确，字段类型转换，业务规则等。

项目主要使用：

* SQL Server: 存储任务配置元数据，记录任务执行情况等
* Python: 从元数据库读取任务配置信息，执行任务并输出结果

目录
========
.. toctree::
   :maxdepth: 2

   data_model
   environment
   deployment
   debug
   development