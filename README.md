# 实验三 MySQL 读写性能测试

在相同的 Spring Boot RESTful 应用中，对比 Spring Data JPA 与 MyBatis 的读取和新建商品性能。代码来自厦门大学课程 spring-fundamentals，在保持 Controller、Service、DAO 和数据库结构一致的基础上增加 MyBatis 持久层。

本仓库提供两套实现、JMeter 测试计划、构建部署脚本、实验设计及结果材料。正式实验使用四台 Ubuntu 18.04.6 云服务器，每台 2 核/2 GiB。实验结论仅适用于报告中的硬件、配置和数据集。

## 源码与版本

- 课程源码基线：`934bbaf69dbdedffdd571f57b768023cdd196743`。
- 来源：https://gitee.com/mingqcn/spring-fundamentals
- JDK 21；Maven 3.9.16；Spring Boot 4.1.1；MySQL 9.2.0。
- MyBatis 3.5.19；MyBatis-Spring 4.0.0；JMeter 5.6.3。
- Prometheus 3.7.3；node-exporter 1.10.2；Docker 20.10.21。
- 此仓库只提取实验依赖的源码；没有复制原仓库的 Git 历史、服务器凭据和个人项目。

原有版权及文件级许可声明均保留。仓库根 LICENSE 为上游 Apache-2.0；部分课程文件另有 GPL-3.0 文件头，使用对应文件时应遵循其自身声明。

## 两套持久层

默认 `jpa` profile 使用 Spring Data Repository。设置 `--spring.profiles.active=mybatis` 后，使用 `persistence/MyBatis*Repository` 和 `resources/mybatis/Lab3Mapper.xml`，关闭 Hibernate/JPA 自动配置。

两套实现共用以下接口：

- GET `/shops/{shopId}/products/{id}`
- POST `/shops/{shopId}/products`

写接口遵循同一业务事务：新增商品，再读取商品及关联信息构造响应。MyBatis 采用 Spring 管理的 SqlSessionTemplate 和 DataSourceTransactionManager。JPA 数据库生成时间字段在 INSERT 后回读，确保两种实现都返回创建时间。

功能测试包含管理员与顾客接口各 8 项，两种 profile 均通过。测试使用真实 MySQL，并通过事务回滚保持数据。删除测试使用新建且无外键引用的商品，避免原示例在事务回滚时掩盖外键冲突。

## 构建

从仓库根执行，不调用原课程会删旧镜像的 `pre-integration-test` 阶段：

```bash
mvn -B -ntp -f clonefactory/pom.xml -Dmaven.compiler.release=21 -Dmaven.test.skip=true install
mvn -B -ntp -f '5. SpringAOP/pom.xml' -Djava.version=21 -Dmaven.test.skip=true package
docker build --build-arg JAR_FILE=target/productdemoaop-0.0.1-SNAPSHOT.jar \
  -t xmu-javaee/productdemoaop:lab3-comparison-20261018 '5. SpringAOP/productdemoaop'
```

实际编译节点的可执行脚本为 `deploy/lab3/build.sh`。脚本中的工具安装路径和工作目录对应本次四节点环境，在其他机器上运行时应先调整。

## 数据与功能测试

`data/baseline.sql.gz` 是不含账号密码的课程样本数据库快照。向一个全新的实验库导入，不能覆盖有业务数据的库。基线为 3,913 条商品、30,660 条商品关联、3,914 条上架记录。账号由部署者在 MySQL 中创建并授权。

创建仓库外私有配置，例如 `/root/.config/lab3/test.properties`：

```properties
spring.datasource.url=jdbc:mysql://MYSQL_PRIVATE_IP:3306/oomall_lab3?serverTimezone=Asia/Shanghai
spring.datasource.username=YOUR_DATABASE_USER
spring.datasource.password=YOUR_PRIVATE_PASSWORD
spring.jpa.show-sql=false
logging.level.cn.edu.xmu.javaee=INFO
```

分别以 `jpa` 和 `mybatis` 运行：

```bash
cd '5. SpringAOP'
mvn -B -ntp -Djava.version=21 -pl productdemoaop -am \
  -Dtest=AdminProductControllerTest,ProductControllerTest \
  -Dsurefire.failIfNoSpecifiedTests=false \
  -Dspring.profiles.active=jpa \
  -Dspring.config.additional-location=file:/root/.config/lab3/test.properties test
```

## 四节点部署与监控

唯一 Swarm 部署配置为 `5. SpringAOP/conf/docker/productdemoaop-docker.yml`。需要先按配置建立 `javaee-proxy` overlay 网络、节点标签、MySQL 挂载目录、Prometheus 配置目录以及应用 Docker secret。

应用密码通过名为 `lab3_app_properties_v1` 的外部 secret 注入；secret 内容是 `spring.datasource.password=...`。MySQL 初始密码只从仓库外的 `/root/.config/lab3/deploy.env` 读取。该环境文件须设为 600 权限；已有 MySQL 数据目录不会因修改环境变量而改变数据库密码。

本次部署参数为 JVM 256–512 MiB、Tomcat 最大 100 线程、Druid 最大 30 连接。测试时只有一个应用副本，避免同时部署两种实现相互干扰。

```bash
PERSISTENCE=jpa LAB_DATABASE=oomall_lab3 bash deploy/lab3/deploy.sh
PERSISTENCE=mybatis LAB_DATABASE=oomall_lab3 bash deploy/lab3/deploy.sh
```

Prometheus 9090 使用独立随机密码，配置文件不进入仓库。四节点 node-exporter 监听 9100；抓取与规则评估间隔均为 5 秒。需检查 6 个 targets 均为 UP，并查看三项课程指标：

```promql
spring:jvm_threads_live_threads
node:cpu_usage_percent
node:memory_usage_percent
```

## 执行与分析

详细设计和指导书逐项对应见 [实验方案](deploy/lab3/EXPERIMENT.md)。

原课程风格入口保留在 `5. SpringAOP/jmeter/jmeter-command.sh`。比较测试使用 `ReadProductComparison.jmx`、`WriteProductComparison.jmx`，增加业务断言、返回 ID、超时和定时运行参数。

`deploy/lab3/benchmark.py` 是本次专用主控脚本，包含固定实验库名称、基线检查、服务切换和 demo 状态恢复。不要直接用于其他环境。公网 SSH 主机映射通过 `LAB3_HOSTS_JSON` 提供，SSH 账号密码通过 `SSH_USER`、`SSH_PASS` 环境变量提供。监控 API 通过本机回环代理访问。

结果统计区分完整请求窗口和升压后的窗口；所有原始 JTL 均保留，不修改或删掉慢请求。重复运行的波动单独展示。1000/10/1 的示例结果与持续负载结果分开解释。

## 参考

- [MyBatis Spring SqlSessionTemplate](https://mybatis.org/spring/sqlsession.html)
- [JMeter Dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)
- [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/)

