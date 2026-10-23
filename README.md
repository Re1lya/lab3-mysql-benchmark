# 实验三 MySQL读写性能测试

完成JPA读写性能测试、MyBatis读写比较及两种实现对比。读取采用参考样例的5个线程档位，写入采用4个档位，两种实现各一套。正文逐档图表使用第一轮18组31200次请求；2026-10-23修订补充同批三轮54组93600次请求的稳定性复核。读取上限尚未测定，写入尖峰未稳定复现，不将单轮异常解释为固定容量上限。

| 内容 | 位置 |
| --- | --- |
| 实验报告 | [修订版PDF](report/实验三_MySQL读写性能测试报告.pdf) / [可编辑Word](report/实验三_MySQL读写性能测试报告.docx) |
| 要求与数据核查 | [实验三要求核查](report/实验三要求核查.md) |
| 负载与压力测试答辩 | [按报告页码整理的简明问答](docs/handoff/实验三_负载与压力测试答辩补充.md) |
| 同批三轮完整记录 | [54组JTL、日志、统计与SHA256清单](results/实验数据/三轮复核/) |
| 部署测试操作手册与验收展示说明 | [docs/handoff](docs/handoff/) |
| JPA读取、写入原始数据 | [01_JPA读取](results/实验数据/原始数据/01_JPA读取/)、[02_JPA写入](results/实验数据/原始数据/02_JPA写入/) |
| MyBatis读取、写入原始数据 | [03_MyBatis读取](results/实验数据/原始数据/03_MyBatis读取/)、[04_MyBatis写入](results/实验数据/原始数据/04_MyBatis写入/) |
| 三项运行监控 | [05_Prometheus监控](results/实验数据/原始数据/05_Prometheus监控/) |
| 参数和数据文件索引 | [测试组索引](results/实验数据/原始数据/测试组索引.csv) |
| 测试结果统计 | [各配置测试统计](results/实验数据/统计与图表/各配置测试统计.csv) |
| JMeter网页报告 | [JMeter测试报告.zip](results/实验数据/JMeter测试报告.zip)，整体解压后打开相应index.html |
| 实验过程截图 | [过程截图](results/实验数据/过程截图/) |

读取为1000/1050/1100/1150/1200线程、10秒升压、2循环；写入为1000/1100/1200/1300线程、10秒升压、1循环。JTL保持原始内容；同组监控JSON包含测试参数及线程、CPU、内存三项原始查询结果。

应用入口是 `4. SpringAOP`，JMX在该目录的 `jmeter` 中；部署入口为 `deploy/lab3/deploy-teacher.sh`。环境、构建和运行步骤见操作手册。源码基于课程提交fce17e7，原始计划和配置保存在reference目录。服务器密码不入库。

`deploy/lab3/analyze-final.py`从上述18份JTL重新计算统计并核对JMeter报告，仅需Python标准库；`build-revised-report.py`生成当前修订报告，另需python-docx；`build-teacher-report.py`为修订前的第一轮报告生成器，会覆盖同名报告，重建当前版本请用前者。`analyze-three-rounds.py`复算新增三轮归档并核对第一轮SHA-256。报告PDF和DOCX已提供，可直接查看。报告按样例逐档展示JMeter原生图表，并附Prometheus历史监控页面；JPA结果与框架比较见表格。截图均对应原18组实测数据。

保留上游版权和文件级许可。根LICENSE为Apache-2.0，部分文件遵循其GPL-3.0声明。课程仓库：https://gitee.com/mingqcn/spring-fundamentals

报告成员：温家正、姚景云、杜奕含、陈浩贤。本次修订沿用论文式中英文摘要、三线表和原生截图；新增数据均来自已完成的实验，本次未重跑服务器压力测试。
