# 实验三 MySQL读写性能测试

完成JPA读写性能测试、MyBatis读写比较及两种实现对比。读取采用参考样例的5个线程档位，写入采用4个档位，两种实现各一套。当前提交统一使用原采集第一轮，共18组31200次请求。

| 内容 | 位置 |
| --- | --- |
| 实验报告 | [report](report/) |
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

`deploy/lab3/analyze-final.py`从上述18份JTL重新计算统计并核对JMeter报告，需要Python及matplotlib；`build-teacher-report.py`生成报告，另需python-docx。报告PDF和DOCX已提供，可直接查看。

保留上游版权和文件级许可。根LICENSE为Apache-2.0，部分文件遵循其GPL-3.0声明。课程仓库：https://gitee.com/mingqcn/spring-fundamentals
