# 实验三完整材料与重新部署手册

本手册供小组成员复现实验和现场验收使用。执行命令请优先从同目录的详细操作步骤.md复制，PDF中的长命令可能自动折行。最终提交报告为“实验报告”目录中的精简版 Word 和 PDF，共 10 页；报告使用的全部原始请求数据单独放在“原始数据”目录，基本测试与扩展测试分别保存。

## 1 能否按照指导书重新部署

**现有四台服务器具备重新部署所需的主要条件，可以按指导书的流程，结合本手册中的环境适配步骤操作；不能逐字复制指导书里的示例命令。** 本次整理进行了只读检查，没有重启服务，也没有重新执行整套部署和压测。因此，以下结论是部署条件核对结果，不是一次新的全流程部署通过记录。

2026 年 10 月 18 日复核结果见“部署核验/redeployment-audit.json”：4 个 Swarm 节点 Ready；MySQL、应用、Prometheus 各 1/1，node-exporter 4/4；应用健康 UP；监控 6 个目标 UP，13 条规则 OK；构建工具、应用镜像、配置文件、overlay 网络和外部 secret 均存在。部署脚本通过 bash 语法检查，Prometheus 配置通过 promtool 检查。当前应用使用 jpa 和原运行库 oomall_demo；专用实验库 oomall_lab3_teacher 已恢复到 3912 条商品。demo 容器正常运行。

本手册的命令针对**现有集群重新部署**。若重装系统或换四台空白机器，还需重建 Swarm、网络、标签、软件、镜像、挂载目录、数据库账号、外部 secret 和监控认证文件；本包不含私密凭据、完整数据库备份或所有 Docker 镜像，不能当作空白机器的一键恢复包。

### 指导书与本环境的对应关系

| 指导书位置 | 要求或示例 | 本环境执行方式 |
| --- | --- | --- |
| 第 1 页 | 编译测试、应用、数据库、监控分机 | CDWY3、CDWY1、CDWY2、CDWY4；四台均 2 核 2 GiB |
| 第 2 页 | 安装 JMeter 5.6.3，按内存设置 JVM | 已安装；JMeter 堆 256–768 MiB，不能照抄 2–4 GiB 示例 |
| 第 2 页 | 修改测试服务器地址 | 已适配到应用私网 172.31.1.202:8080 |
| 第 3 页 | clonefactory、core、应用构建 | 使用 build-teacher.sh；package 加 docker build 完成打包 |
| 第 3 页 | pre-integration-test 构建阶段 | 原阶段含旧镜像清理，本环境保留镜像并单独构建，便于恢复 |
| 第 3 页 | Prometheus 登录和监控 | 使用已配置的独立密码，不是 admin/admin；6 目标、13 规则 |
| 第 3 页 | JMeter 路径和启动脚本 | 实际目录是 /root/spring-fundamentals/4. SpringAOP/jmeter，注意空格及大小写 |
| 第 3 页 | 1000 线程、10 秒升压、1 循环 | 保留该示例；参数使用 -J，使 JMX 的 __P 正确取值 |
| 第 3 页 | 写测试计划 | 已修正 rampup.period 拼写，清除 Windows 结果绝对路径 |
| 第 4 页 | 程序 Git 地址、原始 JTL、实验报告 | 公共仓库、原始数据子目录、精简报告均已提供 |

历史文件名含 teacher 的目录或脚本是既有技术标识，不代表另有一套最终报告口径。仅使用本包中的两批最终数据，早期探索性测试不属于提交数据。

## 2 材料怎么查

| 目录 | 用途 |
| --- | --- |
| 实验报告 | 精简版 Word 与 PDF，检查时优先打开 PDF |
| 原始数据 | 90 组原始 JTL、逐组元数据、日志、监控 JSON；索引和哈希清单 |
| 统计与图表 | 基本测试和扩展测试分别统计的 CSV、JSON、PNG、PDF |
| JMeter可视化报告 | 每组独立 HTML，打开对应目录的 index.html，保留全部资源文件 |
| 过程截图 | JMeter、Prometheus 实际页面及明确标注的日志页面截图 |
| 过程记录 | 采集计划、完成记录、恢复记录、原始操作日志、截图页面来源 |
| 部署核验 | 本次只读服务器检查结果，含首次检查命令兼容性记录 |
| 操作手册 | 完整部署与测试步骤的 Word 和 PDF 版本 |
| 实验程序 | 本次程序、构建与部署脚本、测试计划、监控规则、原始商品 SQL |
| 完整性校验 | 本包逐文件 SHA-256 和校验程序 |

公开仓库：https://github.com/Re1lya/lab3-mysql-benchmark 。程序对应课程提交 fce17e7dd6a204b91bbe89181ad6a30b09aa0270，增加 MyBatis 实现、环境适配和实验工具。教师仓库只拉取，不推送实验改动。公开仓库中的 JTL 为 gzip 无损压缩，本包已保留直接可读的 samples.jtl。

两批共 **90 组、111600 条请求，0 次业务断言失败**：基本测试 36 组 18000 条；扩展测试 54 组 93600 条。扩展性能判据未通过的轮次同样保留，不能只展示较快轮次。请求成功不等于响应时间判据达标。

检查顺序建议：打开报告 → 根据“原始数据/测试组索引.csv”定位对应组 → 打开 samples.jtl → 查看 metadata.json 中线程、循环、框架及数据库行数 → 打开该组 HTML → 对照统计表、监控 JSON 和截图。截图用于说明过程，原始 JTL 是请求数据依据。

## 3 机器与凭据准备

| 机器 | 用途 | 公网 SSH 地址 | 内网地址 |
| --- | --- | --- | --- |
| CDWY1 | Swarm Manager 和应用 | 120.46.82.71 | 172.31.1.202 |
| CDWY2 | MySQL | 120.46.146.243 | 172.31.8.46 |
| CDWY3 | Maven 编译和 JMeter | 120.46.213.158 | 172.31.12.156 |
| CDWY4 | Prometheus | 124.70.102.248 | 172.31.1.19 |

四台均为 Ubuntu 18.04.6、Docker 20.10.21。CDWY3 为 JDK 21、Maven 3.9.16、JMeter 5.6.3；MySQL 9.2.0。应用镜像自带 Java 21，编译机 Java 与容器运行时的补丁版本可不同。

先由环境维护者向操作组员私下提供 SSH、应用数据库和 Prometheus 凭据。材料包不提供密码。现有部署依赖 CDWY1 的 /root/.config/lab3/deploy.env（权限 600，仅设置 MYSQL_ROOT_PASSWORD）和 Swarm secret lab3_app_properties_v1；CDWY4 的 /root/prometheus/web.yml 及 self-scrape-password。已有配置直接复用，不要重新生成不一致密码。

Windows 可以使用 ssh root@公网地址交互登录。含中文文件使用 SFTP 传输，服务器命令和批次名使用 ASCII。docker node、service、stack 命令只在 CDWY1 执行；docker ps、exec、logs 在容器所在节点执行。不能把 docker compose 当作此环境的部署入口，也不要使用旧实验二或旧 5. SpringAOP 部署文件。

## 4 部署前记录和备份

提前约定验收时间。以下命令会写备份或更新课程服务；先确认没有其他成员正在实验。仅正式性能采集需要暂停 demo，完成后恢复其原状态。

CDWY1 记录节点、服务和旧应用配置，并保存应用旧镜像标签。服务配置导出可能含私密内容，备份留在服务器，不加入提交材料。

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
BACK=/root/backups/lab3-check-$STAMP
mkdir -p "$BACK"
chmod 700 "$BACK"
docker node ls > "$BACK/nodes.txt"
docker service ls > "$BACK/services.txt"
docker service inspect lab_productdemoaop > "$BACK/app-spec.json"
docker inspect demo --format '{{.State.Running}}' > "$BACK/demo-running.txt"
cp -a '/root/spring-fundamentals/4. SpringAOP/conf/docker' "$BACK/"
docker tag xmu-javaee/productdemoaop:lab3-teacher-20261018 lab3/app:before-$STAMP
printf '%s\n' "$BACK"
```

CDWY2 对专用实验库做逻辑备份。不要删除 MySQL 数据目录，不要对现有数据目录重复执行首次初始化脚本。

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
BACK=/root/backups/lab3-check-$STAMP
mkdir -p "$BACK"
chmod 700 "$BACK"
CID=$(docker ps -q --filter name=lab_mysql | head -1)
docker exec "$CID" sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --single-transaction --no-tablespaces oomall_lab3_teacher' > "$BACK/experiment.sql"
test -s "$BACK/experiment.sql"
```

## 5 编译和镜像准备

现有服务器源码在 /root/spring-fundamentals。材料包“实验程序”是可供比对和恢复的源码快照。需要同步时先备份该目录，再用 SFTP 上传选定文件，shell 脚本使用 LF 换行；不要直接覆盖私密环境文件。公开仓库也可检出到新目录进行比对，构建脚本中的绝对路径须随目录调整。

CDWY3 执行：

```bash
source /etc/profile.d/lab3-tools.sh
java -version
mvn -version
jmeter --version
cd /root/spring-fundamentals
bash deploy/lab3/build-teacher.sh > /root/lab3-rebuild.log 2>&1
tail -40 /root/lab3-rebuild.log
docker image inspect xmu-javaee/productdemoaop:lab3-teacher-20261018 --format '{{.Id}}'
```

脚本先安装 clonefactory，再安装 core，随后 package 和 docker build。历史成功构建镜像 ID 为 b2e12d68ea0cd4154ab9604b48b474b84cf7b91407f558a89df875e48e9074dc；重新构建受打包时间影响，ID 可能不同，应比较本次编译机和应用机是否一致，不能要求新构建总是等于历史 ID。

CDWY3 已保存 /opt/lab3-downloads 下的 JDK、Maven、JMeter 安装包、基础镜像归档、监控镜像归档及 Maven 缓存。当前路径 /opt/jdk-21、/opt/maven-current、/opt/apache-jmeter-5.6.3 已配置。无需重复下载或重装；离线重建还取决于 Maven 依赖缓存是否齐全，不能只凭安装包存在承诺完全断网构建成功。

若本次重新构建了应用，将镜像导出，使用本机 SFTP 从 CDWY3 下载再上传 CDWY1，不假设服务器间免密登录：

```bash
# CDWY3
docker save xmu-javaee/productdemoaop:lab3-teacher-20261018 | gzip > /root/lab3-app-rebuilt.tar.gz
sha256sum /root/lab3-app-rebuilt.tar.gz
# SFTP transfer via the operator computer
# CDWY1
sha256sum /root/lab3-app-rebuilt.tar.gz
gzip -dc /root/lab3-app-rebuilt.tar.gz | docker load
docker image inspect xmu-javaee/productdemoaop:lab3-teacher-20261018 --format '{{.Id}}'
```

两端 tar.gz 哈希及镜像 ID 应一致。如果使用原有已验证镜像，省略重建与传输。重建覆盖了同名标签时，stack deploy 可能不触发更换容器；需在更新配置后执行 docker service update --force lab_productdemoaop，并检查新容器实际镜像 ID。仅更改配置时仍须先 stack deploy，force 不能替代配置更新。

## 6 数据库检查与部署两种实现

CDWY2 只读检查专用库：

```bash
CID=$(docker ps -q --filter name=lab_mysql | head -1)
docker exec -i "$CID" sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N oomall_lab3_teacher' <<'SQL'
SELECT COUNT(*),MAX(id) FROM goods_product;
SELECT COUNT(*) FROM goods_goods;
SELECT COUNT(*) FROM goods_onsale;
SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA='oomall_lab3_teacher' AND TABLE_NAME='goods_product';
SQL
```

预期依次为 3912 和 5461、30660、3914、5609。原运行库 oomall_demo 当前商品 3913 条，不作为本次性能实验的初始库。重新部署无需重复导入数据。新建专用库时使用“实验程序/data/teacher-product.sql.gz”，先核对 SQL 的目标库语句，再创建空库、导入和授权；禁止把导入命令用于现有业务库。MySQL 9.2 修改密码使用 SET PASSWORD ... = '新密码'，不使用 PASSWORD()。

CDWY1 部署 JPA 到专用库：

```bash
cd /root/spring-fundamentals
PERSISTENCE=jpa LAB_DATABASE=oomall_lab3_teacher LAB3_BLOCK=acceptance-jpa bash deploy/lab3/deploy-teacher.sh
docker service ls
docker service ps lab_productdemoaop
curl -fsS http://127.0.0.1:8080/actuator/health
curl -fsS http://127.0.0.1:8080/actuator/prometheus | grep '^jvm_threads_live_threads'
```

等待应用健康 UP，指标标签 persistence="jpa"。首次启动可能需要数十秒，失败先查看本节点应用容器日志。切换 MyBatis 使用同一镜像与入口：

```bash
PERSISTENCE=mybatis LAB_DATABASE=oomall_lab3_teacher LAB3_BLOCK=acceptance-mybatis bash deploy/lab3/deploy-teacher.sh
```

同样等待健康 UP，标签应为 persistence="mybatis"。两套实现共用 Controller、Service、DAO 和 DTO；JPA 通过 Spring Data Repository 持久化，MyBatis 通过 XML SQL、SqlSessionTemplate 和事务管理器持久化。对比应保持数据、接口、参数、机器和负载计划一致。

应用 Tomcat 最大 300/最小 100，Druid 最大 300/最小 100/初始 100；保留业务 DEBUG 和 JPA SQL 输出；应用堆 256–512 MiB、容器上限 1 GiB。不要为了得到更快数据临时关闭 SQL 日志或改变连接池而不记录。

功能验证历史记录位于“过程记录/基本测试/logs”中的 tests-final.json、test-jpa.log 和 test-mybatis.log，两套各 16 项测试通过。若修改程序，需重新执行 ProductControllerTest 与 AdminProductControllerTest，使用专用库和真实 MySQL；通过环境变量注入数据库 URL、账号、密码与 profile，不能把密码写入命令行提交记录。

## 7 监控检查

CDWY4 上检查配置和记录规则：

```bash
CID=$(docker ps -q --filter name=lab_prometheus | head -1)
docker exec "$CID" promtool check config /etc/prometheus/prometheus.yml
sha256sum /root/prometheus/rules/recording.yml
```

规则文件预期 SHA-256 为 02dbf03210523be719bb2f6cce0f255370864106d6d1335ed1e4cfcd2adfb1de。修改监控配置前先备份 /root/prometheus；如确需应用修改，在 CDWY1 更新 Prometheus 服务，之后重新核查目标和规则。

本机建立 SSH 隧道后在浏览器打开 http://127.0.0.1:19091，使用单独的 Prometheus 凭据登录：

```bash
ssh -N -L 19091:127.0.0.1:9090 root@124.70.102.248
```

Targets 应有 4 个 node、1 个应用和 1 个 Prometheus，全部 UP；Rules 应有 13 条且无错误。查询 spring:jvm_threads_live_threads、node:cpu_usage_percent、node:memory_usage_percent，选择覆盖测试起止的时间窗口并截图。应用 target 是 productdemoaop:8080，避免误写成含下划线的服务名造成请求问题。

抓取周期 2 秒、全局 evaluation 5 秒，但两个规则组显式 interval 为 30 秒。CPU 使用 5 分钟 rate，内存使用 Free+Buffers+Cached。短测试中的 CPU 曲线不能解释为瞬时峰值；每 2 秒导出也不意味着记录规则每 2 秒产生一个新样本。

## 8 现场重新运行一组读写测试

以下是在新目录运行的验收样本，不覆盖本包历史数据。先确认应用已连接专用库，再暂停干扰进程。CDWY1 将 demo 原始运行状态保存在第 4 节备份中，正式测量前执行 docker stop demo；结束后仅在原状态为 true 时恢复。普通配置查看不必停 demo。

CDWY3 执行以下读测试；JMX 中地址和 CSV 相对路径已适配，必须从 jmeter 目录运行。为了保留现场过程，可在登录后先使用 script -q -f /root/lab3-check-terminal.log 记录会话，结束时 exit；含密码的命令不要录入公开日志。

```bash
source /etc/profile.d/lab3-tools.sh
cd '/root/spring-fundamentals/4. SpringAOP/jmeter'
export HEAP='-Xms256m -Xmx768m -XX:MaxMetaspaceSize=192m'
export JVM_ARGS='-Xss512k'
BATCH=/root/lab3-results/check-$(date +%Y%m%d-%H%M%S)
mkdir "$BATCH"
RUN="$BATCH/jpa-read-t1000-r1"
mkdir "$RUN"
date -Is > "$RUN/start.txt"
jmeter -n -t ReadProduct.jmx -Jthread.num=1000 -Jrampup.period=10 -Jloop.count=1 -Jjmeter.save.saveservice.timestamp_format=ms -l "$RUN/samples.jtl" -j "$RUN/jmeter.log" > "$RUN/console.log" 2>&1
date -Is > "$RUN/end.txt"
tail -8 "$RUN/console.log"
jmeter -g "$RUN/samples.jtl" -o "$RUN/html" -Jjmeter.reportgenerator.overall_granularity=1000
```

预期 1000 条请求，业务断言失败 0。写测试将计划改成 WriteProduct.jmx，并使用新的 RUN 目录，如 jpa-write-t1000-r1；JPA/MyBatis 切换后也使用准确命名的新目录。JMX 已包含随机写载荷和断言，不要改成自定义固定请求体。不能把单轮通过当作完成全部实验矩阵。

每组前按第 6 节确认初始数据；写测试成功 1000 条后商品数应为 4912。保存测试后的行数证据，再复位。**下面的 SQL 只适用于已经备份、没有其他用途的 oomall_lab3_teacher 库**：

```bash
# CDWY2, after saving evidence and backing up the experiment database
CID=$(docker ps -q --filter name=lab_mysql | head -1)
docker exec -i "$CID" sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N oomall_lab3_teacher' <<'SQL'
DELETE FROM goods_product WHERE id>5461;
ALTER TABLE goods_product AUTO_INCREMENT=5609;
SELECT COUNT(*),MAX(id) FROM goods_product;
SQL
```

预期恢复为 3912、5461。该复位策略依赖实验写入仅新增 id>5461 商品；若修改业务逻辑导致更新或删除旧行，应先停止测试，从专用库备份恢复，不能仍用上述删除语句宣称恢复成功。

## 9 完整测试矩阵与采集方法

| 批次 | 接口 | 总线程数 | 升压 | 循环 | 每配置重复 |
| --- | --- | --- | --- | --- | --- |
| 基本测试 | 读、写 | 100、400、1000 | 10 秒 | 1 | 3 |
| 扩展测试 | 读 | 1000、1050、1100、1150、1200 | 10 秒 | 2 | 3 |
| 扩展测试 | 写 | 1000、1100、1200、1300 | 10 秒 | 1 | 3 |

每项均执行 jpa 和 mybatis。基本测试 2×2×3×3=36 组，扩展测试 2×(5+4)×3=54 组。这里的线程数是计划启动的总线程，不能称为持续活跃并发人数；观察 allThreads 才能辅助了解请求时的实际活动线程。

原采集控制程序为 teacher-benchmark.py、supplement-benchmark.py，单组运行器为 run-teacher-case.sh、run-supplement-case.sh。程序保留随机种子、分组顺序、逐组数据复位、监控抓取、demo 暂停恢复和失败记录。初始首个分组等待 300 秒，组前等待 15 秒，组后等待 12 秒；不能表述为每组都预热 5 分钟。

**不能直接重跑这些带 20261018 路径的历史控制程序。** 新采集前复制控制程序并修改 EV（本机证据目录）、BACK（远端恢复目录）、REMOTE（远端结果目录）；同步修改运行器 out 路径和控制程序调用的运行器文件名，创建新的 BACK 目录。旧 experiment-started.json 防止误启动，不要删除它来强行重跑。每个新组都必须使用空结果目录，JMeter HTML 输出目录也必须不存在或为空。

公开 remote.py 从 LAB3_HOSTS_JSON 读取节点映射，从 SSH_USER、SSH_PASS 读取凭据；本机 Python 需有 paramiko。原控制程序使用本机 19090 认证代理，该代理不是 JMeter 或 Prometheus 自带服务，也未包含在源码。跨电脑重跑时应在新控制程序的 api 函数中改为第 7 节的 19091 隧道，并使用 Basic Authorization。可将 urlopen(url,...) 替换为下述逻辑，PROM_USER 和 PROM_PASSWORD 仅通过本机环境变量提供：

```python
import base64, os, urllib.request
token = base64.b64encode((os.environ['PROM_USER'] + ':' + os.environ['PROM_PASSWORD']).encode()).decode()
req = urllib.request.Request(url, headers={'Authorization': 'Basic ' + token})
with urllib.request.urlopen(req, timeout=30) as response:
    d = json.load(response)
```

同时将 api 中的端口改为 19091；先验证 targets 和 rules，随后执行一个小样本，确认认证、SFTP、元数据和监控文件保存正常，再开始新矩阵。不要把本手册中的代码片段原样插入而保留原来的 urlopen 语句。

每组保存：samples.jtl、jmeter.log、console.log、start.txt、end.txt、metadata.json、targets-before.json、targets-after.json 和 12 个 prometheus-NN.json。监控 query_range 窗口为请求开始前 15 秒至结束后 10 秒，step=2。元数据记录实现、重复轮次、接口、线程、升压、循环、成功数、时间和数据库变化。

中止可在新 EV 目录创建 STOP_REQUESTED 文件。正常异常处理会恢复应用到 jpa/oomall_demo，并恢复原先运行的 demo。远端心跳兜底只保证尝试恢复 demo，不保证恢复应用库；断电、进程强杀或断网后必须人工执行下一节检查。

## 10 结束恢复与异常排查

CDWY1 恢复本次开始前的已知运行配置（若现场原状态不同，按备份恢复实际原状态）：

```bash
cd /root/spring-fundamentals
PERSISTENCE=jpa LAB_DATABASE=oomall_demo LAB3_BLOCK=restored bash deploy/lab3/deploy-teacher.sh
# Only if demo was running before the experiment
docker start demo
docker service ls
docker ps --format '{{.Names}} {{.Status}}'
curl -fsS http://127.0.0.1:8080/actuator/health
curl -fsS http://127.0.0.1:8080/actuator/prometheus | grep '^jvm_threads_live_threads'
```

随后检查专用库已复位，原运行库仍为 3913 条，6 个监控目标 UP，13 条规则 OK，demo 状态与开始前一致。保存恢复命令输出和截图。若重建镜像不可用，在 APP_IMAGE 环境变量中指定第 4 节保存的 lab3/app:before-时间戳 再执行部署；若更改了配置文件，先从备份恢复对应文件，再部署并验证。

遇到应用反复重启，先看 docker service ps，再在 CDWY1 看实际容器日志；Access denied 通常检查账号、目标库和 secret，而不是修改 MySQL 初始化环境变量。端口拒绝连接需确认应用已健康启动。监控 DOWN 检查内网、服务 DNS、账号文件和 target。JMeter 没有按指定线程执行，应检查 -J 参数、JMX __P 属性名与拼写。不要用删镜像、删数据或全局 prune 解决这些问题。

## 11 原始数据复核与报告生成

基本和扩展数据分别统计。每组按原始 elapsed 计算响应时间均值、分位数和最大值；吞吐量为样本数除以首请求开始至最后请求结束的时间。分组结果保留三轮均值及波动，不能把全部请求合并后冒充三次独立重复。具体算法以包内 analyze-teacher.mjs、analyze-supplement.mjs 为准。

扩展测试判据在采集前规定：全部请求中至少 80% 同时满足业务成功且原始 elapsed≤40ms；一个配置须三轮都通过。18 个配置中 13 个满足，未通过组均保留。elapsed-Connect 仅为辅助指标，不等于 SQL 执行时间；JPA 的非单调变化也不支持把某个线程档位称为精确容量上限。

原始数据/测试组索引.csv 列出每组路径、参数、样本数、失败数和 JTL 哈希。原始数据/SHA256.csv 覆盖整个原始数据子目录中的数据文件。本包完整性校验程序逐文件复核字节数和 SHA-256：

```bash
# Run at the extracted package root; Python 3 standard library only
python '完整性校验/verify.py'
```

需重新生成图表时，先将“原始数据/基本测试”复制到程序根目录 output/playwright/lab3-teacher-20261018/runs，将扩展测试复制到 output/playwright/lab3-supplement-20261018/runs。把对应“统计与图表”复制到各自 analysis，把对应 JMeter 可视化报告复制到各自 reports。脚本采用这些固定相对路径，单纯双击一个统计脚本不能自动识别中文材料目录。

用 Node 22 执行 analyze-teacher.mjs 与 analyze-supplement.mjs；使用 verify-teacher-results.mjs、verify-supplement-results.mjs 对照 JMeter HTML 的 statistics.json。用 matplotlib 运行 plot-teacher.py、plot-supplement.py；用 python-docx 运行 build-teacher-report.py。如果还需重建 Word 报告，须将“过程截图”和“过程记录”中的 pages、logs 及批次根记录同步恢复到相应证据目录；首次重建前检查脚本依赖路径。原始报告及图表已经包含在包内，验收查看无需重建。

生成 JMeter HTML 可用第 8 节的 -g 命令，或 dashboards.py；后者必须显式指定 --evidence 和 --expected 36 或 54，因为默认值属于早期实验。不要为了改报告文案重新跑性能测试，也不要编辑原始 JTL 后继续沿用旧哈希和统计。

## 12 截图与验收留档

现有材料保留两批共 164 张过程截图。截图包括真实 JMeter/Prometheus 页面，以及从真实 SSH 日志渲染的页面；日志页面不是原生终端截图。统计图单独保存在“统计与图表”，不冒充采集现场画面。

重新验收时另建 check-日期 目录，按顺序保存：四节点和服务状态、软件版本、构建成功、两端镜像 ID、数据库初始行数、JPA/MyBatis 健康及标签、Targets/Rules、JMeter 执行结束、HTML Statistics 和响应曲线、监控时间窗口、写入后行数、最后恢复状态。截图文件名包含步骤、实现、接口和时间。密码输入、完整环境变量、secret 内容不截图、不提交。

向老师展示时使用本包中的报告、原始数据和代码地址；现场重新运行产生的数据另行标明日期和参数，不冒充 10 月 18 日报告的原始采集结果。验收是否通过以老师实际检查为准。
