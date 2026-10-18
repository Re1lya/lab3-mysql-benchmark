# 实验三 MySQL 读写性能测试

最终实验以教师仓库 `fce17e7dd6a204b91bbe89181ad6a30b09aa0270` 为基线，完成 JPA 与 MyBatis 两套读写测试。教师 Gitee 仅拉取，本仓库是个人公开实验仓库，不包含服务器凭据或私人项目。

## 教师版本与正式数据

- 教师来源：https://gitee.com/mingqcn/spring-fundamentals
- 当前入口：`4. SpringAOP/`，与最新指导书目录一致。
- 原始 JMX、运行脚本、Prometheus 规则及文件哈希：`reference/teacher-fce17e7/`。
- 正式方案：[教师版本执行记录](deploy/lab3/TEACHER_PROTOCOL.md)。
- 原自定义35秒测试仅为前期探索，不用于最终报告。先前 Git 提交保留历史，当前正式入口已改为教师版本。
- 正式结果正在按教师版本重新采集，完成后本仓库补充原始数据、统计、截图与报告。

教师主程序的36个Java文件、Maven配置、clonefactory和商品CSV与先前源码基线934bbaf一致；监控公式、运行参数、随机写载荷及部署资源设置已经按最新版重新核对。

## 环境

四台 Ubuntu 18.04.6，2核/2GiB，Docker20.10.21；编译/JMeter、应用、MySQL、Prometheus各一台，使用私网发压。JDK21、Maven3.9.16、JMeter5.6.3、SpringBoot4.1.1、MySQL9.2.0、MyBatis3.5.19、MyBatis-Spring4.0.0、Prometheus3.7.3、node-exporter1.10.2。

应用采用教师有效参数：Tomcat最大300/最小100；Druid最大300/最小100/初始100；保留业务DEBUG和JPA SQL输出。JVM按实际2GiB内存调整：应用堆256–512MiB、JMeter堆256–768MiB。Prometheus抓取2秒、评估5秒，CPU rate[5m]和内存Free+Buffers+Cached公式使用教师原件。

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
