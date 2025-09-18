CREATE TABLE xxxx.xxxx.products AS 

with product as (
select distinct product 

from samples.bakehouse.sales_transactions
),
cost_price as (
select 
product as product_name 
, CAST(FLOOR(rand() * 10) + 1 AS DECIMAL(10,2)) as cost_price
from product )

select 
row_number() OVER(partition by 1 order by 1) AS product_id
, product_name
, cost_price
, cost_price*2 as sales_price
from cost_price
