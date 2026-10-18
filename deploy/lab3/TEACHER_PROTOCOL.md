# 实验三教师版本执行记录

用户要求最终报告以教师最新版为主。正式来源为 Gitee 提交 `fce17e7dd6a204b91bbe89181ad6a30b09aa0270`，同步日期 2026-10-18。教师原始 JMX、运行脚本、监控配置和规则保存在公开实验仓库的 `reference/teacher-fce17e7/`，附 SHA-256。

## 与前期批次的界限

`lab3-comparison-20261018` 的固定载荷、35 秒循环以及自定义监控口径仅为前期探索，已停止并标记 superseded。最终报告、图表和统计只读取 `lab3-teacher-20261018`。环境历史截图另作历史证据，不当成正式性能数据。

## 教师版本保持的内容

- `ReadProduct.jmx` 的 CSV 读取、HTTP 200 与 errno=0 断言；`WriteProduct.jmx` 的随机中文字段、随机数、Authorization、HTTP 201 断言和单次循环。
- CPU 公式：`(1 - sum(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) / sum(rate(node_cpu_seconds_total[5m])) by (instance)) * 100`。
- 内存公式：`(1 - (node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes) / node_memory_MemTotal_bytes) * 100`。
- 原 13 条记录规则；抓取 2 秒、全局评估 5 秒，但两个规则组均显式设为 30 秒（实际生效）；抓取超时 1 秒。
- 教师部署有效参数 Tomcat 最大300/最小100；Druid 最大300/最小100/初始100；JPA SQL 输出及业务 DEBUG 日志。
- 教师原始 product.sql：商品3912、关联30660、上架3914；在专用数据库导入，保留原课程运行库。

## 必要适配与脚本修正

1. hostname 改为应用私网 IP，端口8080；四个 node-exporter 地址改为现有节点。
2. `__P` 读取 JMeter 属性，因此运行参数使用 `-J`；原脚本 `-D` 无法按指导书意图覆盖 JMX 属性。
3. 写计划 `rump-up.period` 拼写统一为 `rampup.period`；移除教师电脑上的 `C:\Users\mingQ\Downloads\W400-10.jtl` 输出路径，使用本次 run 目录。
4. 按指导书第2页根据现有2GiB内存设置 JMeter 堆256–768MiB、应用256–512MiB。机器规格不改，报告如实披露。
5. 密码通过外部配置及 Docker secret 注入；不公开环境端点敏感值；Prometheus 独立密码。监控独立部署到第4台，符合指导书角色安排。
6. 使用同一镜像的 JPA/MyBatis profile 完成用户指定的两套实现；业务代码以教师程序为基础，新增 MyBatis 持久层和生成字段语义修复，功能测试各16项。

## 正式矩阵

两种框架 × 两个接口 × 100/400/1000线程 × 3次重复，共36组、18000次请求。所有组升压10秒、循环1次。1000/10/1直接对应指导书第3页示例，400与教师JMX默认线程数对应，100为低负载对照。没有使用前期定时循环或额外业务断言增加每次请求开销。

每个实现块重新部署，首组前等待5分钟使前期负载离开 CPU 的5分钟窗口。每组前清理专用库的新增行并恢复自增起点5609，检查基线。组前空闲15秒，组后等待12秒采集监控；每组写请求数量与数据库新增行数一致，读后数量不变。

必须解释：1000个线程分10秒各发一次请求，不能称为1000持续并发；CPU rate[5m]是最近5分钟平滑值，包含邻近时间段，不能视为某10秒组的瞬时CPU峰值。采集元数据、查询时序和完整JTL均保留，以便复核。

## 交付与恢复

所有原始JTL、HTML报告、监控JSON、测试日志及截图保存。最后恢复JPA应用到oomall_demo、恢复demo原运行状态并核验服务和数据库。GitHub为个人公开仓库，教师Gitee不推送。教师认可仍需实际审核，不代为宣称完成。
