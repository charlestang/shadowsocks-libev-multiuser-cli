#!/bin/bash

#sqlite3 -column -header ss-stats.db "select nickname, server_id, pid, pid_created_at, max(total_traffic) / 1048576 as total_traffic from waterlog join server on server.id = waterlog.server_id join account on account.id = server.account_id group by server_id, pid, pid_created_at order by waterlog.id desc;"
sqlite3 -column -header ss-stats.db "select nickname, round(sum(total_traffic) / 1048576.0, 2) as total_traffic_M from (select nickname, server_id, pid, pid_created_at, max(total_traffic) as total_traffic from waterlog join server on server.id = waterlog.server_id join account on account.id = server.account_id group by server_id, pid, pid_created_at order by waterlog.id desc) group by nickname;"
