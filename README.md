# 实验三 MySQL 读写性能测试

实验程序基于课程源码 `fce17e7dd6a204b91bbe89181ad6a30b09aa0270`，完成 JPA 与 MyBatis 两套读写测试。教师 Gitee 仅拉取，本仓库是个人公开实验仓库，不包含服务器凭据或私人项目。

## 实验数据与材料

- 源码来源：https://gitee.com/mingqcn/spring-fundamentals
- 当前入口：`4. SpringAOP/`，与最新指导书目录一致。
- 原始 JMX、运行脚本、Prometheus 规则及文件哈希：`reference/teacher-fce17e7/`。
- 正式方案：[测试计划与配置来源](deploy/lab3/TEACHER_PROTOCOL.md)。
- 已完成90组、111600次请求、0次断言失败：基本测试36组18000次请求，扩展测试54组93600次请求；两套实现各16项真实MySQL功能测试通过。
- [Word/PDF报告](report/) · [原始数据与截图](results/teacher-20261018/) · [逐次统计CSV](results/teacher-20261018/analysis/all-runs.csv) · [分组统计CSV](results/teacher-20261018/analysis/group-summary.csv)
- [扩展测试数据与截图](results/supplement-20261018/) · [扩展逐轮统计](results/supplement-20261018/analysis/all-runs.csv)。两批分别保存36份与54份HTML报告，见各目录的 `jmeter-html-reports.zip`；JTL以gzip无损压缩保存，并提供SHA-256清单。
- Node原始JTL统计与JMeter Java报告的样本数、错误数、均值、极值和吞吐量逐组一致。服务器已恢复JPA到原运行库，demo恢复健康。

教师主程序的36个Java文件、Maven配置、clonefactory和商品CSV与先前源码基线934bbaf一致；监控公式、运行参数、随机写载荷及部署资源设置已经按最新版重新核对。

## 环境

四台 Ubuntu 18.04.6，2核/2GiB，Docker20.10.21；编译/JMeter、应用、MySQL、Prometheus各一台，使用私网发压。JDK21、Maven3.9.16、JMeter5.6.3、SpringBoot4.1.1、MySQL9.2.0、MyBatis3.5.19、MyBatis-Spring4.0.0、Prometheus3.7.3、node-exporter1.10.2。

应用运行参数：Tomcat最大300/最小100；Druid最大300/最小100/初始100；保留业务DEBUG和JPA SQL输出。JVM按实际2GiB内存调整：应用堆256–512MiB、JMeter堆256–768MiB。Prometheus抓取2秒、全局评估5秒，两个规则组实际按显式配置30秒评估；CPU rate[5m]和内存Free+Buffers+Cached公式使用原始配置。

## 构建与两套实现

```bash
mvn -B -ntp -f clonefactory/pom.xml -Dmaven.compiler.release=21 -Dmaven.test.skip=true install
mvn -B -ntp -f '4. SpringAOP/pom.xml' -Djava.version=21 -pl core -am -Dmaven.test.skip=true install
mvn -B -ntp -f '4. SpringAOP/pom.xml' -Djava.version=21 -Dmaven.test.skip=true package
docker build --build-arg JAR_FILE=target/productdemoaop-0.0.1-SNAPSHOT.jar -t xmu-javaee/productdemoaop:lab3-teacher-20261018 '4. SpringAOP/productdemoaop'
```

`jpa` profile 使用 Spring Data Repository；`mybatis` 使用同接口的MyBatis实现、XML SQL及Spring事务。两者共用Controller、Service、DAO和DTO。JPA数据库生成时间回读与MyBatis插入后读取保持创建时间语义。功能测试使用真实MySQL事务回滚。

本次构建脚本为 `deploy/lab3/build-teacher.sh`，用 Maven package 与 docker build 完成镜像打包，避开原课程删除历史镜像的阶段。

## 数据与配置

`data/teacher-product.sql.gz` 是教师原始product.sql的无损压缩版本，不含账户密码。导入一个新建专用库 `oomall_lab3_teacher`：商品3912行、关联30660行、上架3914行，商品最大ID5461、自增起点5609。不能覆盖有业务数据的数据库。

数据库账号、密码、Prometheus独立密码均由部署者私下设置。应用密码通过外部Docker secret `lab3_app_properties_v1` 注入，内容为 `spring.datasource.password=YOUR_PRIVATE_PASSWORD`；MySQL容器配置从 `/root/.config/lab3/deploy.env` 读取。配置需要600权限。

```bash
PERSISTENCE=jpa LAB_DATABASE=oomall_lab3_teacher bash deploy/lab3/deploy-teacher.sh
PERSISTENCE=mybatis LAB_DATABASE=oomall_lab3_teacher bash deploy/lab3/deploy-teacher.sh
```

唯一正式Swarm部署文件为 `4. SpringAOP/conf/docker/productdemoaop-docker.yml`，需按配置建立overlay网络、节点标签、挂载目录和外部secret。脚本的路径对应本次环境，其他机器应先调整。

## 测试

在 `4. SpringAOP/jmeter` 中使用JMeter5.6.3：

```bash
jmeter -n -t ReadProduct.jmx -Jthread.num=1000 -Jrampup.period=10 -Jloop.count=1 -l ReadProduct-1000-10-1.jtl
jmeter -n -t WriteProduct.jmx -Jthread.num=1000 -Jrampup.period=10 -Jloop.count=1 -l WriteProduct-1000-10-1.jtl
jmeter -g ReadProduct-1000-10-1.jtl -o ReadProduct-1000-10-1 -Jjmeter.reportgenerator.overall_granularity=1000
```

相对于教师原件仅修复连接地址、写升压参数拼写、Windows结果绝对路径和启动参数-D/-J不匹配；随机载荷、业务断言及循环语义保留。完整修正清单和原件可复核。

正式矩阵为100/400/1000线程、10秒升压、1循环，2框架×2接口×3档×3重复，共36组、18000次请求。1000/10/1为指导书原例，不是1000个持续活跃用户。CPU为5分钟平滑值，不能作为10秒组的瞬时峰值。

`teacher-benchmark.py` 为本次专用控制程序，包含专用库复位、服务切换、私人demo容器的暂停恢复和远端心跳恢复。不要未经调整直接用于其他集群。主机映射通过 `LAB3_HOSTS_JSON`，SSH凭据通过 `SSH_USER`、`SSH_PASS` 提供；监控API通过本机认证代理访问。

## 许可与参考

保留上游版权和文件级许可。根LICENSE来自上游Apache-2.0，部分课程文件有GPL-3.0文件头，遵循对应文件声明。

- [MyBatis Spring SqlSessionTemplate](https://mybatis.org/spring/sqlsession.html)
- [JMeter HTML Dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)
- [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/)

## 本次结果与复核

1000总线程、10秒升压、1次循环时，三轮平均响应：读取JPA 11.58ms、MyBatis 8.35ms；写入JPA 1307.02ms、MyBatis 41.33ms。写入存在明显轮间波动，完整三轮均保留。吞吐量受启动节奏约束，不代表最大容量。CPU按5分钟窗口，规则组30秒评估，不作为10秒单组瞬时峰值。

本地完整材料采用 `output/playwright/lab3-teacher-20261018` 目录。公开目录按体积压缩JTL和HTML；复算时先解压恢复为原始布局。`analyze-teacher.mjs` 统计原始JTL，`verify-teacher-results.mjs` 独立核对JMeter HTML统计，`plot-teacher.py` 从结果JSON生成图，`build-teacher-report.py` 和 `report-layout.py` 生成Word。离线生成HTML使用 `dashboards.py`，需要指定本机JMeter路径。

恢复后4个节点Ready，服务副本正常，6个监控目标UP、13条记录规则OK；专用库恢复3912条商品，原运行库3913条保持不变。132份节点文件与公开源码按换行标准化后SHA-256一致。对应证据在结果目录 `verification/`。指导书要求的教师认可需实际提交审核。

## 扩展负载实验

参考实验报告样例，增加以下负载档位；JPA与MyBatis分别测试，每组重复3次。

| 操作 | 总线程数 | 升压 | 循环 | 组数 |
|---|---|---|---|---|
| 读取 | 1000 / 1050 / 1100 / 1150 / 1200 | 10秒 | 2 | 30 |
| 写入 | 1000 / 1100 / 1200 / 1300 | 10秒 | 1 | 24 |

扩展实验单独统计，与基本测试不混合计算。比较目标为至少80%的全部请求成功且原始elapsed不超过40ms；三轮均满足才记为该档位达标。另报告elapsed-Connect辅助口径，不将其当作纯SQL耗时。

18种配置中13种三轮均满足目标。MyBatis读取所有已测档位均满足目标；写入1000、1100、1200线程三轮均满足，1300线程存在一轮未满足。JPA的达标情况非单调，需结合应用预热和运行顺序解释，不能给出唯一容量临界点。上述结果描述本次环境和请求模型。

补测脚本为 `supplement-benchmark.py` 与 `run-supplement-case.sh`，保留原JMX、应用镜像和监控公式。`analyze-supplement.mjs`、`verify-supplement-results.mjs`、`plot-supplement.py`用于统计、交叉核验和绘图；`build-teacher-report.py`直接整合两批结果，生成精简报告；`supplement-report.py`保留详细版的补测排版逻辑。所有脚本均在 `deploy/lab3/`。

分析脚本读取原始JTL；公开目录的JTL需先解压，并按脚本中本地证据目录布局放置。统计可使用Node.js 22；绘图、报告生成另需Python、matplotlib和python-docx。最终报告按样例结构精简为10页，呈现两批90组测试的主要结果、代表性图表和结论；逐轮明细、完整截图与监控数据保留在材料目录。

## 实验操作与材料导航

[按实验三指导书编排的操作手册](docs/handoff/HANDOFF_MANUAL.md)提供安装、参数设置、编译部署、监控、测试及数据整理步骤。[材料目录](docs/handoff/HANDOFF_README.md)列出报告、基本读写测试、扩展读写测试、功能测试和截图的存放位置。
