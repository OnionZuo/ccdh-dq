.. rst-class:: nonmodule

==========
安装和部署
==========

DQC程序由Python语言编写，在不同系统上均可以运行。以下指南为环境中部署和运行DQC程序提供参照。

Python3, pip和venv
--------------------------
首先，需要安装Python3和pip并使用venv创建虚拟环境。

.. seealso::

    * `python.org`_
    * `Installing packages using pip and virtual environments — Python Packaging User Guide`_

.. _python.org: https://python.org
.. _`Installing packages using pip and virtual environments — Python Packaging User Guide`: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

例如，在Amazon Linux 2环境下可以执行以下命令：
  
.. prompt:: bash

    python --version                             # 查看Python3是否安装
    sudo yum install python3                     # 安装Python3 
    python3 -m pip --version                     # 查看pip是否安装
    python3 -m pip install --user --upgrade pip  # 安装pip
    mkdir dqc                                    # 创建项目目录
    python3 -m venv dqc                          # 在项目目录下创建虚拟环境


ODBC Driver for SQL Server
-------------------------------
另外，需要安装Microsoft ODBC驱动以连接SQL Server数据库。

.. seealso::

    * `安装 Microsoft ODBC Driver for SQL Server (Linux)`_
 

.. _`安装 Microsoft ODBC Driver for SQL Server (Linux)`: https://docs.microsoft.com/zh-cn/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server

例如，在Red Hat Enterprise Server 7环境安装ODBC 13可以执行以下命令：

.. prompt:: bash

    sudo su
    curl https://packages.microsoft.com/config/rhel/7/prod.repo > /etc/yum.repos.d/mssql-release.repo
    exit
    sudo yum update
    sudo yum remove unixODBC #to avoid conflicts
    sudo ACCEPT_EULA=Y yum install msodbcsql-13.0.1.0-1 mssql-tools-14.0.2.0-1
    sudo yum install unixODBC-utf16-devel 
    ln -sfn /opt/mssql-tools/bin/sqlcmd-13.0.1.0 /usr/bin/sqlcmd
    ln -sfn /opt/mssql-tools/bin/bcp-13.0.1.0 /usr/bin/bcp

Python包
---------------------------------
最后，安装DQC程序运行需要的Python包。

.. rst-class:: mylist

* `Pandas <https://pypi.org/project/pandas/>`_: 用于将元数据库查询结果存为DataFrame
* `redshift-connector <https://pypi.org/project/redshift-connector/>`_: 用于连接Redshift数据库
* `pyodbc <https://pypi.org/project/pyodbc/>`_: 用于连接SQL Server数据库
    

先激活项目虚拟环境：

.. prompt:: bash

    source dqc/bin/activate

之后使用以下命令安装：

.. prompt:: bash

    python3 -m pip install -r requirements.txt  # 全部安装
    python3 -m pip install pandas # 单独安装
    
.. note::

    如果pyodbc包安装遇到问题，可参考以下网页：

    .. rst-class:: mylist
    
    * `Unable to install pyodbc on Linux — Stack Overflow`_

    .. _`Unable to install pyodbc on Linux — Stack Overflow`: https://stackoverflow.com/questions/2960339/unable-to-install-pyodbc-on-linux