WITH ranked_messages AS (SELECT m.*,
                                m.sol_status in ('opt', 'optimal') as succeed
#                                 ROW_NUMBER() OVER (PARTITION BY name,method ORDER BY `version` DESC) AS rn
                         FROM benchmarking_lp.s_mipcol17 AS m)
select tt.method,
       tt.`N`,
       tt.`SGM(T)`,
       tt.`SGM(K)`,
       tt.version
from (select method,
             version,
             sum(succeed) as `N`,
             exp(avg(ln(if(succeed = 0, 15000, ranked_messages.sol_time) + 10))) - 10      as `SGM(T)`,
             exp(avg(ln(if(succeed = 0, 20000, ranked_messages.iteration_num) + 50))) - 50 as `SGM(K)`
      from ranked_messages
      group by method, version) as tt
where
#     tt.rn <= 2 and
  tt.method not in ('\\lbfgs', '\\cg', '\\gd', '\\drsom')
order by  method, version;