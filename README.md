# 实验三 MySQL 读写性能测试

最终实验以教师仓库 `fce17e7dd6a204b91bbe89181ad6a30b09aa0270` 为基线，完成 JPA 与 MyBatis 两套读写测试。教师 Gitee 仅拉取，本仓库是个人公开实验仓库，不包含服务器凭据或私人项目。

## 教师版本与正式数据

- 教师来源：https://gitee.com/mingqcn/spring-fundamentals
- 当前入口：`4. SpringAOP/`，与最新指导书目录一致。
- 原始 JMX、运行脚本、Prometheus 规则及文件哈希：`reference/teacher-fce17e7/`。
- 正式方案：[教师版本执行记录](deploy/lab3/TEACHER_PROTOCOL.md)。
- 原自定义35秒测试仅为前期探索，不用于最终报告。先前 Git 提交保留历史，当前正式入口已改为教师版本。
- 正式采集已完成：36组、18000次请求、0次失败；两套实现各16项真实MySQL功能测试通过。
- [Word/PDF报告](report/) · [原始数据与截图](results/teacher-20261018/) · [逐次统计CSV](results/teacher-20261018/analysis/all-runs.csv) · [分组统计CSV](results/teacher-20261018/analysis/group-summary.csv)
- 36份HTML报告见结果目录的 `jmeter-html-reports.zip`，JTL以gzip无损压缩保存，并提供SHA-256清单。
- Node原始JTL统计与JMeter Java报告的样本数、错误数、均值、极值和吞吐量逐组一致。服务器已恢复JPA到原运行库，demo恢复健康。

教师主程序的36个Java文件、Maven配置、clonefactory和商品CSV与先前源码基线934bbaf一致；监控公式、运行参数、随机写载荷及部署资源设置已经按最新版重新核对。

## 环境

四台 Ubuntu 18.04.6，2核/2GiB，Docker20.10.21；编译/JMeter、应用、MySQL、Prometheus各一台，使用私网发压。JDK21、Maven3.9.16、JMeter5.6.3、SpringBoot4.1.1、MySQL9.2.0、MyBatis3.5.19、MyBatis-Spring4.0.0、Prometheus3.7.3、node-exporter1.10.2。

应用采用教师有效参数：Tomcat最大300/最小100；Druid最大300/最小100/初始100；保留业务DEBUG和JPA SQL输出。JVM按实际2GiB内存调整：应用堆256–512MiB、JMeter堆256–768MiB。Prometheus抓取2秒、全局评估5秒，两个规则组实际按显式配置30秒评估；CPU rate[5m]和内存Free+Buffers+Cached公式使用教师原件。

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

1000总线程、10秒升压、1次循环时，三轮平均响应：读取JPA 11.58ms、MyBatis 8.35ms；写入JPA 1307.02ms、MyBatis 41.33ms。写入存在明显轮间波动，完整三轮均保留。吞吐量受启动节奏约束，不代表最大容量。CPU按教师5分钟窗口，规则组30秒评估，不作为10秒单组瞬时峰值。

本地完整材料采用 `output/playwright/lab3-teacher-20261018` 目录。公开目录按体积压缩JTL和HTML；复算时先解压恢复为原始布局。`analyze-teacher.mjs` 统计原始JTL，`verify-teacher-results.mjs` 独立核对JMeter HTML统计，`plot-teacher.py` 从结果JSON生成图，`build-teacher-report.py` 和 `report-layout.py` 生成Word。离线生成HTML使用 `dashboards.py`，需要指定本机JMeter路径。

恢复后4个节点Ready，服务副本正常，6个监控目标UP、13条记录规则OK；专用库恢复3912条商品，原运行库3913条保持不变。132份节点文件与公开源码按换行标准化后SHA-256一致。对应证据在结果目录 `verification/`。指导书要求的教师认可需实际提交审核。
