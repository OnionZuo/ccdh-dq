主键唯一
关键信息唯一
非空检查
拉链正确，开始日期小于结束日期
拉链正确，开始日期不重复
拉链正确，不存在交叉链
空文件检查
业务规则

--1. 主键唯一 返回值=0
select count(1) from(
select ${column_1} from ${table_1} where ${filter_1} group by ${column_1} having count(1)>1
);

--拉链表
select count(1) from(
select src_recpt_id from fdt.fdt_stock_sl_recpt where effective_to_date='9999-12-31' group by src_recpt_id having count(1)>1
);
${column_1}=src_recpt_id
${filter_1}=effective_to_date='9999-12-31'
${table_1}=fdt.fdt_stock_sl_recpt

--事实表
select count(1) from(
select src_order_id from fdt.fdt_sales_order_offtake group by src_order_id having count(1)>1
);

${column_1}=src_order_id
--${filter_1}=effective_to_date='9999-12-31'
${table_1}=fdt.fdt_sales_order_offtake

--2. 非空检查 返回值=0
select count(1) from( select * from ${table_1} where ${filter_1});

select count(1) from( select * from fdt.fdt_stock_sl_recpt where recpt_type is null);
${filter_1}=recpt_type is null
${table_1}=fdt.fdt_stock_sl_recpt

--3. 拉链正确，开始日期小于结束日期 返回值=0
select count(1) from( select * from ${table_1} where ${filter_1});

select count(1) from( select * from fdt.fdt_stock_sl_recpt where effective_from_date > effective_to_date);
${filter_1}=effective_from_date > effective_to_date
${table_1}=fdt.fdt_stock_sl_recpt

--4. 拉链正确，开始日期不重复 返回值=0
select count(1) from( select ${column_1},${column_2} from ${table_1} where ${filter_1} group by ${column_1},${column_2} having count(1)>1 );

select count(1) from( select src_recpt_id,effective_from_date from fdt.fdt_stock_sl_recpt where effective_to_date='9999-12-31' group by src_recpt_id,effective_from_date having count(1)>1 );

${column_1}=src_recpt_id
${column_2}=effective_from_date
${filter_1}=effective_to_date='9999-12-31'
${table_1}=fdt.fdt_stock_sl_recpt


--5. 拉链正确，不存在交叉链 返回值=0
select sum(datediffs) from(
select ${column_1},effective_from_date,effective_to_date,nvl(lag(effective_to_date,1) over(partition by ${column_1} order by cn),'1970-01-01'),date_diff('day',nvl(lag(effective_to_date,1) over(partition by src_recpt_id  order by cn),'1970-01-01'),effective_from_date) as datediffs
from(select ${column_1},effective_to_date,effective_from_date,row_number() over(partition by ${column_1} order by effective_from_date) as cn
from ${table_1}
))where datediffs<>0;

select sum(datediffs) from(
select src_recpt_id,effective_from_date,effective_to_date,nvl(lag(effective_to_date,1) over(partition by src_recpt_id order by cn),'1970-01-01'),date_diff('day',nvl(lag(effective_to_date,1) over(partition by src_recpt_id  order by cn),'1970-01-01'),effective_from_date) as datediffs
from(select src_recpt_id,effective_to_date,effective_from_date,row_number() over(partition by src_recpt_id order by effective_from_date) as cn
from fdt.fdt_stock_sl_recpt
))where datediffs<>0;

${column_1}=src_recpt_id
${table_1}=fdt.fdt_stock_sl_recpt

--6. 字段类型转换正确 返回值=0
select count(1) from( select * from ${table_1} where ${filter_1});

select count(1) from (select * from fdt.fdt_stock_sl_recpt where apply_date>getdate());
${filter_1}=apply_date>getdate()
${table_1}=fdt.fdt_stock_sl_recpt

--7.业务规则
${script_1}
${script_2}
${connection_1}
${connection_2}

select
  sum(txn_qty) qty
 ,sum(txn_amt)  amt
from gdt.gdt_stk_sl_fct_stk_txn tx
where shop_no=999998 and tx.org_brand_id=1001 and left(dim_date_id,6)=202104 
and txn_code=9 and txn_direction=2 and area_type=1
;

--从ace查
declare @month varchar(10)
set @month='2021-04'

select 
sum(count)*-1 as qty
,sum(price*count)*-1 as amt
from
(
select a.id,fromlogicid,logicstockname as fromstockname
from stock_t_stock_receipt a with(nolock)
inner join stock_t_logic_stock c with(nolock) on a.fromlogicid=c.id
where a.customerid=1001 and receipttype=9  and convert(varchar(7),submitdate,120)=@month and  a.fromlogicid=18
)ar
inner join 
(
select a.id,convert(varchar(100),submitdate,112)as saledate,e.dealerid,dealername,a.tologicid,c.logicstockname as tostockname,manufacturercode,count,price
from stock_t_stock_receipt a
inner join stock_tr_stock_receipt_sku b with(nolock) on a.id=b.receiptid
inner join stock_t_logic_stock c with(nolock) on a.tologicid=c.id
inner join user_t_organization d with(nolock) on d.id=a.fromorgid
inner join user_t_dealer e with(nolock) on  e.id=d.dealerid
inner join product_t_sku f  with(nolock)on  b.skuid=f.id
inner join product_t_product g with(nolock) on f.productid=g.id
where a.customerid=1001 and receipttype=9  and convert(varchar(7),submitdate,120)=@month and a.tologicid!=18 and processnodestep='end'
and d.type=2
)sr on ar.id=sr.id
;

