# 扩展负载实验材料

读取：1000/1050/1100/1150/1200总线程，10秒升压，2循环。
写入：1000/1100/1200/1300总线程，10秒升压，1循环。
JPA和MyBatis均完成，每组重复3次，共54组93600次请求。

测试计划、载荷规则、应用镜像、数据库初始数据和监控公式沿用基本实验。
本批次独立保存，不与基本实验36组18000请求混合计算。

protocol.json在采集前记录比较目标：至少80%的全部请求成功且elapsed不超过40ms。
analysis/all-runs.csv保留每轮比例、原始响应分位数、吞吐量、活动线程峰值、监控统计。
elapsed-Connect仅作为扣除连接建立时间的辅助口径，不等于SQL执行时间。
截图分为实际JMeter/Prometheus页面和明确标注的真实日志渲染页面。

runs保存原始JTL与监控JSON；reports保存54份完整JMeter HTML；analysis保存统计和绘图。
基本与扩展实验共90组111600请求，最终Word/PDF报告位于仓库report目录。

公开目录的JTL使用gzip无损压缩，HTML集中保存在jmeter-html-reports.zip。SHA256-published.csv对应本目录实际文件。
