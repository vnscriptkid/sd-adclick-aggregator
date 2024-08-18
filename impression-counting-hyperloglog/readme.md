# Impression Counting
```sql
select count(distinct user_id) from impressions
where date between '2020-01-01' and '2020-01-31'
and event_id = 123
```

# Redis HyperLogLog
```shell
PFADD impressions:event-1:2020-01-01T15:00 user-1 user-2 user-3
PFADD impressions:event-1:2020-01-01T15:00 user-1 user-4 user-5

PFCOUNT impressions:event-1:2020-01-01T15:00

PFADD impressions:event-1:2020-01-01T16:00 user-5 user-6

PFMERGE temp impressions:event-1:2020-01-01T15:00 impressions:event-1:2020-01-01T16:00
PFCOUNT temp
```
