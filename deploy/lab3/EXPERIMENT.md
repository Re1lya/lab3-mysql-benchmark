# 实验三执行方案与验收清单

依据《实验三：MySQL读写性能测试》4 页指导书，覆盖 Spring Data JPA 与 MyBatis 两条技术路线。四台机器维持用户购买规格，不更换系统或硬件。

## 变量与比较范围

同一应用镜像、Controller、Service、DAO、DTO、连接池、JVM、Tomcat、MySQL 和网络，只切换 `spring.profiles.active=jpa|mybatis`。JPA 使用 Spring Data Repository，MyBatis 使用 XML SQL 和 Spring 管理的 SqlSessionTemplate。MyBatis 模式关闭 Hibernate 和 JPA 仓库自动配置，并使用 DataSourceTransactionManager。服务层事务边界不变。两条路线都使用真实 MySQL，不使用内存模拟数据库。

读接口为 GET /shops/{shopId}/products/{id}，写接口为 POST /shops/{shopId}/products。商品数据从当前库复制到专用的 oomall_lab3，基线含 3,913 条商品、30,660 条关联关系和 3,914 条上架记录。原 oomall_demo 保持原状。每组开始前仅清理实验新建且带专用 barcode 的记录，校验基线行数与最大 ID，并统一自增起点。

## 测试矩阵

- 两个框架 × 两个接口 × 10、50、100 个线程 × 3 次重复，共 36 组正式定时测试。
- 每组 35 秒，前 5 秒升压。原始 JTL 保留全部请求；统计同时提供全程结果与升压后约 30 秒的结果。
- 每次切换框架先分别预热读、写 20 秒，预热不纳入正式结果。
- 另执行两个框架各自的读、写 1000 线程、10 秒升压、1 次循环示例，共 4 组；这是约每秒启动 100 个单次请求线程，不能称为 1000 个持续活跃用户。
- 重复 1/3 按 JPA→MyBatis，重复 2 按 MyBatis→JPA；每对框架使用相同且固定随机种子的工作负载顺序。
- 正式执行期间不编译、不生成 HTML 报告；JMeter 位于独立节点，私网发压。
- demo 原运行状态被记录，测试前停机，结束后恢复。主控每 15 秒更新心跳；断联超过 180 秒时服务器守护脚本恢复 demo。每组前后检查 demo 确实停止。

## 数据与判定

每次请求保存时间戳、完整响应耗时、首字节等待时间、连接时间、HTTP 状态、断言结果、活动线程、收发字节、URL 和返回商品 ID。读断言同时校验 HTTP 200、errno=0、返回 ID；写断言校验 HTTP 201、errno=1、返回 ID 非空。写入后核对数据库增长量、成功请求数、返回 ID 唯一性一致。

Prometheus 每 5 秒采样，导出指导书要求的三项指标（JVM 活跃线程、四节点 CPU、四节点内存），以及堆内存、GC、进程 CPU、磁盘和网络速率。保存每组前后的 target 状态和每项 query_range 原始 JSON。响应时间直接取 JTL 的 elapsed，不凭空扣除 TCP 时间。

主要结果为成功吞吐量、错误率、均值、P50/P90/P95/P99、最大延迟、资源均值/峰值。重复试验以每次运行为独立观察单位，给出均值、样本标准差及范围；不把大量相关请求当成大量独立试验。

## 指导书逐项对应

| 页码 | 要求 | 本实验执行方式 / 证据 |
| --- | --- | --- |
| 1 | SpringBoot、MySQL、RESTful API | 两条持久层路线和相同读写接口；真实接口与事务测试 |
| 1 | 四台 Ubuntu 18.04 | 已有四节点，2 核/2 GiB；真实规格写入报告，说明与 1G 示例的差别 |
| 1 | A 编译/JMeter、B 应用、C MySQL、D Prometheus | CDWY3、CDWY1、CDWY2、CDWY4 |
| 2 | JMeter 5.6.3 与 PATH | 安装日志、校验和、版本与环境变量截图 |
| 2 | 按 free -m 调整 JVM | JMeter 256–768 MiB，应用 256–512 MiB，线程栈 512 KiB；不照抄不适用的 4G 堆 |
| 2 | 报告粒度 1000ms、目标 IP/端口 | user.properties、JMX 和运行参数 |
| 3 | clonefactory、core、多模块打包、Docker 镜像 | Maven 构建日志、镜像 ID；用 package + docker build 等效完成，避开删旧镜像脚本 |
| 3 | 私网 node-exporter、targets/rules、三个 query | 6 个 UP 目标、13 条规则、页面截图、时序 JSON |
| 3 | JMeter 参数、JTL 与 HTML | 36 组主测试和 4 组指导书示例；全部原始结果和 HTML |
| 4 | Git 地址、JTL、报告 | 公开个人仓库、原始数据包、可编辑报告与 PDF |
| 4 | 教师认可程序与原始数据 | 材料准备齐全后仍需由教师审核，不能自行标记为已获认可 |

## 解释边界

这是特定 2 核/2 GiB 云主机、热缓存、小型课程数据集和指定应用逻辑下的结果，不外推为所有 JPA/MyBatis 系统的排名。不通过 CPU 曲线单独证明锁竞争或磁盘瓶颈。35 秒采样不能替代长时间稳定性实验；1000/10/1 是短时示例而非持续并发容量结论。

预热、联调失败与正式样本分目录保存。截图区分真实页面与原始日志渲染页面。原始 JTL 不修改；压缩版本保留校验和，可无损还原。

