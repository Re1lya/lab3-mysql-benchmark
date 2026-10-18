# 实验三完整材料

本包用于现场验收，包含精简实验报告、对应原始数据、程序和操作手册。

## 材料导航

| 材料 | 位置与内容 |
| --- | --- |
| 实验报告 | `实验报告/`：最终 10 页 Word、PDF |
| 报告原始数据 | `原始数据/`：基本测试 36 组、扩展测试 54 组，分别存放 |
| 数据索引 | `原始数据/测试组索引.csv`：参数、样本数、文件位置和 SHA-256 |
| 统计与图表 | `统计与图表/`：两批各自的汇总表和图表 |
| JMeter 页面 | `JMeter可视化报告/`：各组目录下打开 `index.html` |
| 过程证据 | `过程截图/`、`过程记录/`：截图、日志、采集及恢复记录 |
| 部署与测试 | `操作手册/`：详细命令、测试矩阵、数据复位、恢复和排错 |
| 实验程序 | `实验程序/`：源码、JMX、部署脚本、监控配置和商品 SQL |
| 环境核验 | `部署核验/`：本次检查记录及 Docker 升级评估 |

原始数据共 **90 组、111600 条请求**，全部业务断言成功；性能指标未达标的轮次也完整保留。基本测试与扩展测试分别统计，未混入早期探索数据。原始 JTL 与原采集文件、公开仓库 gzip 解压内容一致。

## 重新部署结论

**现有四台机器具备重新部署的主要条件，按组员手册适配后的步骤执行；不能逐字照抄指导书示例。** 2026 年 10 月 18 日只读检查确认：4 节点 Ready，课程服务副本正常，应用 UP，6 个监控目标 UP、13 条规则 OK，工具、镜像、网络、配置和 secret 均在。本次整理没有实际重启或重新部署。

指导书第 1 页要求 Ubuntu 18.04 和 Docker，未指定 Docker 版本，也没有要求 `docker stack config`。当前使用 `docker stack deploy`，Docker 20.10.21 已支持本实验所需功能。建议本次验收前保持版本一致；升级评估另见 `部署核验/Docker升级评估.md`。

## 操作顺序

1. **准备与备份**：向环境维护者取得 SSH 和监控凭据；记录原服务、数据库和 demo 状态。详见手册第 3–4 节。
2. **编译**：CDWY3 在 `/root/spring-fundamentals` 执行 `bash deploy/lab3/build-teacher.sh`。重新构建后把镜像通过 SFTP 传到 CDWY1，加载并核对 ID。详见第 5 节。
3. **部署**：CDWY1 在同一源码目录执行下列命令；等待应用健康 UP，再核查 profile 和监控。详见第 6–7 节。

```bash
PERSISTENCE=jpa LAB_DATABASE=oomall_lab3_teacher bash deploy/lab3/deploy-teacher.sh
# 测完 JPA 后切换 MyBatis
PERSISTENCE=mybatis LAB_DATABASE=oomall_lab3_teacher bash deploy/lab3/deploy-teacher.sh
```

4. **测试**：CDWY3 从 `4. SpringAOP/jmeter` 运行读写 JMX，1000 线程、10 秒升压、1 循环为指导书示例；使用 `-J` 参数和适合 2 GiB 机器的 JVM 内存。每次创建新结果目录，正式采集前停 demo，写入前后核对专用库行数。完整可复制命令与全部矩阵见第 8–9 节。
5. **恢复**：按开始前记录恢复应用、专用库和 demo，检查健康及监控，保存现场截图。详见第 10 节。

唯一部署文件为 `4. SpringAOP/conf/docker/productdemoaop-docker.yml`。保留现有私密配置和外部 secret；不要重复初始化已有 MySQL 数据目录。历史采集程序带固定日期目录，重新采集前必须按手册修改路径和监控认证，不能直接重跑覆盖旧结果。若重装四台系统，还需重建集群和软件；本包不是含密码及镜像的一键恢复包。

## 检查时展示

先打开报告，再从测试组索引找到对应 `samples.jtl`、`metadata.json` 和 JMeter HTML；监控原始时序也保存在同组目录。现场新测数据另存，不替换报告的历史数据。

解压后可在材料包根目录运行文件完整性校验（仅需 Python 3）：

```bash
python '完整性校验/verify.py'
```

程序仓库：https://github.com/Re1lya/lab3-mysql-benchmark 。本包不含服务器密码，教师仓库未推送任何实验改动。
