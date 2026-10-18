# 实验三教师版本材料说明

正式数据来自教师 fce17e7 的 JMX 与13条记录规则。100/400/1000总线程、10秒升压、1次循环、两框架两接口三次重复，共36组18000次请求。

- runs/：未经修改的原始JTL、JMeter日志、起止时间、元数据、目标状态和12类监控时序JSON。
- reports/：全部36份JMeter离线HTML，打开各目录index.html。
- analysis/：逐次CSV、分组CSV、统计JSON和由原始数据生成的图表。
- screenshots/：实际Prometheus/JMeter页面截图，以及明确标注的真实SSH日志渲染截图。
- pages/：日志渲染页面的HTML来源；logs/保留原始日志。
- deliverables/：可编辑Word报告与对应PDF。
- SHA256.csv：原始数据及各交付文件的完整性清单。

报告时间采用北京时间。Prometheus网页横轴可能为UTC；原始时序使用Unix时间戳。CPU使用教师rate[5m]公式，两个记录规则组均每30秒评估；2秒导出间隔不等于每2秒新增记录规则测量。

截图是过程证据，数值复核以原始JTL和JSON为准。JMeter页面截图在采集后离线生成，日志页面截图不是原生终端截图。analysis中的图是统计图，不宣称为屏幕截图。

前期lab3-comparison-20261018批次已废止，本包不包含其性能数据。教师认可程序与数据仍须实际审核。

代码：https://github.com/Re1lya/lab3-mysql-benchmark

公开仓库中JTL保存为samples.jtl.gz，解压后与原始JTL哈希一致；HTML打包为jmeter-html-reports.zip。SHA256-original-materials.csv对应本机完整材料包，SHA256-published.csv对应公开目录的实际文件。
