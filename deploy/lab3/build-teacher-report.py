"""Experiment report generated from verified measurements."""
import json,argparse,importlib.util
from pathlib import Path
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[2];EV=ROOT/'output/playwright/lab3-teacher-20261018'
spec=importlib.util.spec_from_file_location('layout',Path(__file__).with_name('report-layout.py'))
layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
doc=layout.doc;para=layout.para;heading=layout.heading;sub=layout.sub;page=layout.page;table=layout.table;picture=layout.picture
ap=argparse.ArgumentParser();ap.add_argument('--draft',action='store_true');args=ap.parse_args();layout.DRAFT=args.draft
d=json.loads((EV/'analysis/results.json').read_text());rows=d['rows'];groups=d['groups']
if not args.draft:
 assert d['complete'] and len(rows)==36 and d['samples']==18000
 assert (EV/'restored.json').exists() and (EV/'logs/final-verification.json').exists()
by={(g['profile'],g['operation'],g['threads']):g for g in groups}
SUP=ROOT/'output/playwright/lab3-supplement-20261018'
supplement=json.loads((SUP/'analysis/results.json').read_text()) if (SUP/'analysis/results.json').exists() else None
include_supplement=bool(supplement and supplement['complete'] and (SUP/'restored.json').exists())
s=doc.sections[0];s.page_width=Inches(8.5);s.page_height=Inches(11)
doc.settings.odd_and_even_pages_header_footer=False
s.top_margin=Inches(.7);s.bottom_margin=Inches(.65);s.left_margin=Inches(.9);s.right_margin=Inches(.9)
s.header_distance=Inches(.28);s.footer_distance=Inches(.28)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2']:
 st=doc.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
 st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体' if name=='Normal' else '黑体')
for st in doc.styles:
 for border in list(st.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.line_spacing=1.2;normal.paragraph_format.space_after=Pt(7)
doc.styles['Title'].font.size=Pt(23);doc.styles['Subtitle'].font.size=Pt(13)
doc.styles['Subtitle'].font.italic=False
doc.styles['Heading 1'].font.size=Pt(16);doc.styles['Heading 2'].font.size=Pt(12)
hp=s.header.paragraphs[0];hp.text='Spring 框架课程实验三  |  MySQL 读写性能测试';hp.runs[0].font.size=Pt(8)
fp=s.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER;fp.add_run('第 ')
f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');fp._p.append(f);fp.add_run(' 页')
for r in fp.runs:r.font.size=Pt(9)

# Concise report: the full measurements and screenshots remain in the evidence bundle.
assert include_supplement, 'Completed supplementary results are required'
assert len(supplement['rows'])==54 and supplement['samples']==93600

def ext_table(operation):
 values=sorted([g for g in supplement['groups'] if g['operation']==operation],key=lambda g:(g['threads'],g['profile']))
 table(['线程','实现','均值 ms','P95 ms','≤40 ms比例','三轮比例范围','三轮达标'],[[
  g['threads'],'JPA' if g['profile']=='jpa' else 'MyBatis',f'{g["mean_ms_mean"]:.2f}',f'{g["p95_ms_mean"]:.2f}',
  f'{g["within40_pct_mean"]:.1f}%',f'{g["within40_pct_min"]:.1f}–{g["within40_pct_max"]:.1f}%',
  '是' if g['within40_all_repeats_pass'] else '否'] for g in values],[.55,.75,.8,.8,1,1.7,1.1])

# 1
p=doc.add_paragraph('MySQL 读写性能测试',style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph('Spring Data JPA 与 MyBatis 读写性能对比',style='Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=para('实验日期：2026 年 10 月 18 日');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
heading('摘要')
para('本实验在四台云服务器上部署 Spring 商品管理应用，使用 JMeter 对读取与新建商品接口进行测试，比较 MyBatis 的读写效率以及 JPA 与 MyBatis 的响应差异，并通过 Prometheus 记录线程数、CPU 和内存使用情况。基本测试采用 100、400、1000 线程，扩展测试增加 1000–1300 线程档位及双循环读取；各组合重复三次，共完成 90 组、111600 次请求，未出现断言失败。')
para('基本测试中，MyBatis 在三个档位下均表现为读快于写；1000 线程时，写入平均耗时约为读取的 4.95 倍。相同写入条件下，JPA 和 MyBatis 的平均响应分别为 1307.02 ms 和 41.33 ms。扩展测试的 18 种配置中，13 种在三轮中均达到至少 80% 请求成功且响应不超过 40 ms 的目标。重复测试存在波动，结论适用于本次实现、环境与请求模型，不能据此认定框架的普遍性能排序或持续并发容量。')
para('关键词：MySQL；Spring Data JPA；MyBatis；JMeter；读写性能')
heading('1 问题描述')
para('实验围绕三个问题展开：JPA 在商品读写场景中的响应表现如何；同一 MyBatis 实现的读取与写入效率有何差异；在相同接口和负载下，切换持久层实现会怎样影响响应时间。通过平均响应时间、响应时间百分比分布、时间趋势及重复波动分析结果。')
para('首先完成应用构建、部署和功能验证，再在统一初始数据上执行基本与扩展测试。基本测试用于直接比较读写及两种实现；扩展测试参考实验报告样例的负载档位和响应目标，进一步观察不同请求规模下的表现。[1][2]')

# 2
page('2 实验分析')
sub('2.1 实验环境与方法')
para('四台服务器均为 Ubuntu 18.04.6，配置 2 核 CPU、2 GiB 内存和 40 GiB 系统盘，通过私网互联，使用 Docker Swarm 部署服务。')
table(['节点','任务','主要软件'],[
 ['CDWY3','编译与压力测试','JDK 21、Maven 3.9.16、JMeter 5.6.3'],
 ['CDWY1','商品管理应用','Spring Boot 4.1.1、JPA、MyBatis 3.5.19'],
 ['CDWY2','数据库','MySQL 9.2.0'],
 ['CDWY4','运行监控','Prometheus 3.7.3；各节点部署 node-exporter']],[.8,1.7,4.2])
para('应用使用相同 Controller、Service、DAO 和 DTO，通过 profile 切换 JPA 与 MyBatis。JPA 使用 Spring Data Repository；MyBatis 通过 XML SQL 和 Spring 事务实现相同仓储接口，两者均在写入后读取生成字段及关联信息以构造响应。两套实现各 16 项真实 MySQL 功能测试全部通过。')
sub('数据与运行参数')
para('初始数据库含商品 3912 行、关联关系 30660 行、上架记录 3914 行。每组前恢复初始数据；写后核对新增行数与成功请求数，读后确认数据量不变。测试期间暂停无关容器，结束后恢复。')
para('应用保留业务 DEBUG 和 JPA SQL 输出。Tomcat 最大/最小线程为 300/100；Druid 最大/最小/初始连接为 300/100/100。应用 JVM 堆为 256–512 MiB，JMeter 堆为 256–768 MiB，线程栈为 512 KiB。')
sub('测试执行')
para('读取使用 GET /shops/{shopId}/products/{id}，商品 ID 来自 CSV；新建使用 POST /shops/1/products，按测试计划生成随机字段。读取校验 HTTP 200 与 errno=0，写入校验 HTTP 201。JMeter 以非 GUI 模式运行，将结果保存为 JTL，再离线生成 1000 ms 粒度的 HTML 报告。[3]')
para('两种实现使用相同测试计划、请求规则和应用镜像。第 1、3 轮先测 JPA，第 2 轮先测 MyBatis，轮内组合按固定种子打乱。切换实现时重新部署，通过健康检查并等待空闲窗口后开始测试，未额外发送业务预热请求。')

# 3
page('2.2 实验设计与评价指标')
para('两种持久层均完成下表全部组合，每组重复三次，升压时间统一为 10 秒。基本与扩展测试分批统计，避免将不同循环次数的结果混合。')
table(['测试','操作','总线程档位','循环','组数','请求数'],[
 ['基本','读、写','100 / 400 / 1000',1,36,'18000'],
 ['扩展','读','1000 / 1050 / 1100 / 1150 / 1200',2,30,'66000'],
 ['扩展','写','1000 / 1100 / 1200 / 1300',1,24,'27600']],[.55,.6,3.05,.5,.6,1.4])
para('基本测试在相同线程数、升压时间与循环次数下比较读写效率；框架对比固定接口和负载，仅切换持久层。扩展读取每线程执行两次请求，写入执行一次，因此扩展结果主要比较同一操作内部的档位变化和框架差异。配置的总线程数不等于瞬时活跃线程数。')
sub('响应时间与吞吐量')
para('响应时间采用原始 JTL 的 elapsed，保留连接时间与全部慢请求；报告均值、P95 及响应分布和时间趋势。P95 表示约 95% 请求的耗时不超过该值，使用线性插值计算。汇总表中的均值与 P95 均为三轮对应统计量的平均，不是合并全部请求后的分位数。')
para('吞吐量按成功请求数除以“最后完成时间−首次发起时间”计算。由于线程在 10 秒内陆续启动并仅执行有限次请求，吞吐量受发送节奏约束，不能作为系统最大吞吐能力。原始统计与 JMeter 报告的样本数、失败数、均值、极值和吞吐量已逐组核对。')
sub('扩展实验的响应目标')
para('参考样例，将“至少 80% 的全部请求成功且响应不超过 40 ms”设为扩展实验的比较目标；每轮分别计算，三轮均达标才记为该配置达标。[2] 该阈值仅用于本次比较，不作为所有应用的通用标准。')
para('另计算 max(elapsed−Connect, 0) 作为连接建立时间的辅助分析，详见附带 CSV。该值仍包含其他网络和业务处理耗时，不能视为纯 SQL 时间。正文以完整 elapsed 判断是否达到目标。')
sub('重复测试与波动')
para('全部轮次均纳入统计，未删除未达标或较慢轮次。应用冷启动、JIT 编译、缓存状态及运行顺序可能影响短时结果，因此同时报告三轮范围；不能仅凭单轮结果推断容量不足。')

# 4
page('2.3 基本测试结果')
para('基本测试共 36 组、18000 次请求，断言失败为 0。响应时间单位为 ms；均值列同时给出三轮样本标准差，吞吐量单位为 req/s。')
table(['操作','实现','线程','均值 ± 标准差','P95','吞吐量'],[[
 '读' if g['operation']=='ReadProduct' else '写','JPA' if g['profile']=='jpa' else 'MyBatis',g['threads'],
 f'{g["mean_ms_mean"]:.2f} ± {g["mean_ms_sd"]:.2f}',f'{g["p95_ms_mean"]:.2f}',f'{g["success_rps_mean"]:.1f}'
 ] for g in groups],[.45,.8,.55,2.2,1.2,1.5])
para('MyBatis 在 100、400、1000 线程下的读取均值分别为 4.25、3.33、8.35 ms，写入均值为 8.95、7.66、41.33 ms；写入耗时分别约为读取的 2.11、2.30、4.95 倍。写路径包含插入、生成字段回读及关联查询，工作量高于查询已有商品。')
para('1000 线程时，JPA 与 MyBatis 的读取均值为 11.58 和 8.35 ms，写入均值为 1307.02 和 41.33 ms。JPA 写入三轮均值为 1383.62、549.26、1988.18 ms，波动较大；这些差异描述本次配置下的完整业务接口响应，不能仅归因于框架本身。')
para('两种实现的吞吐量接近，且随请求规模上升。这主要反映相同的发送节奏；延迟及其波动仍有明显差异，相近吞吐量不表示两种实现的极限处理能力相同。')

# 5
page('2.4 MyBatis 读写响应分布')
para('下图取基本测试第 3 轮，在相同线程档位比较 MyBatis 读取与写入。左图为累计响应分布，右图为按请求发起时间划分的 1 秒平均响应趋势，各组均对齐首个请求。')
picture(EV/'analysis/mybatis-read-write-trends.png','图 1  MyBatis 读写响应分布与时间趋势，10 秒升压、1 次循环。',6.4)
para('1000 线程示例中，读取平均响应为 3.36 ms、P95 为 4.00 ms；写入分别为 55.98 ms 和 364.45 ms。写入存在更长的慢请求尾部，仅看平均值会低估部分请求的等待时间。图示用于解释单轮形态，整体判断仍以三轮统计为依据。')

# 6
page('2.5 扩展读取结果')
para('读取采用 10 秒升压、2 次循环，共 30 组、66000 次请求。表中响应时间和“≤40 ms 比例”为三轮均值，比例范围保留轮间波动；达标要求三轮均达到 80%。')
ext_table('ReadProduct')
para('MyBatis 在所有已测档位均达到目标；最高 1200 线程时平均响应为 2.44 ms，三轮达标比例为 99.5%–99.8%。本次读取范围内未找到失效边界。')
para('JPA 在 1100 线程有一轮仅 58.0% 的请求在 40 ms 内成功，但更高的 1150、1200 线程三轮均达标，结果并非随线程数单调变化。因此不能将 1100 线程直接认定为容量临界点，需结合启动状态和运行顺序解释。')
picture(SUP/'screenshots/mybatis-r3-read-statistics.png','图 2  MyBatis 第 3 轮 1200 线程双循环读取的 JMeter 实际统计截图。',6.5)
para('该轮共 2400 次请求，平均响应 2.26 ms，失败数为 0。JMeter 与正文使用的分位数估计方法不同，P95 可能有小幅差异；样本数、均值及失败数一致。')

# 7
page('2.6 扩展写入结果')
para('写入采用 10 秒升压、1 次循环，共 24 组、27600 次请求。统计口径与读取表一致，所有轮次的写后数据库增量均与成功请求数相符。')
ext_table('WriteProduct')
para('MyBatis 在 1000、1100、1200 线程三轮均达标；1300 线程的比例范围为 71.8%–98.8%，其中一轮未达到目标。1200 与 1300 线程之间可作为进一步细化测试的区间，但现有短时测试不足以确定精确最大容量。')
para('JPA 写入只有 1200 线程三轮均达标，其他档位存在未达标轮次。1300 线程三轮平均响应为 1084.74 ms，达标比例跨度为 0.0%–97.8%，再次说明应结合重复数据，而非仅用一轮结果判断性能。')
picture(SUP/'screenshots/mybatis-r3-write-statistics.png','图 3  MyBatis 第 3 轮 1300 线程单循环写入的 JMeter 实际统计截图。',6.5)
para('该轮 1300 次请求全部成功，平均响应 6.05 ms；该轮表现较好不代表同档位全部重复均达标。零断言失败与满足响应时间目标是不同评价维度。')

# 8
page('2.7 响应目标与负载变化')
picture(SUP/'analysis/within40-target.png','图 4  40 ms 内成功请求比例；粗线为三轮均值，细线为各轮，虚线为 80% 目标。',6.5)
para('18 种扩展配置中，13 种在三轮中均达到目标。MyBatis 读取在全部已测档位保持达标，写入在最高档位出现未达标轮次；JPA 读写均出现非单调变化，无法据此给出唯一临界线程数。')
para('图中均值可能掩盖单轮下降，因此达标判断采用“三轮全部满足”，而非“三轮均值超过 80%”。例如 MyBatis 1300 线程写入的平均达标比例为 89.8%，但最低一轮为 71.8%，仍判为未全部达标。')
para('原始 elapsed 与扣除 Connect 后的曲线较接近，单独扣除连接建立时间没有消除主要波动。两种口径均保留在原始统计中；正文结论以完整请求响应时间为准。')

# 9
page('2.8 运行监控与结果解释')
para('Prometheus 采集 JVM 活跃线程、CPU 和内存等指标。抓取间隔为 2 秒，全局评估为 5 秒，两组记录规则按各自设置每 30 秒评估；共有 6 个监控目标和 13 条记录规则，检查结果均正常。')
picture(SUP/'analysis/WriteProduct-monitoring.png','图 5  第 3 轮 1300 线程写入的 JVM 线程数、应用 CPU、应用内存和发压 CPU。',6.5)
para('图中两种实现各自对齐首个请求。该示例中，JPA 的 JVM 线程数和应用节点内存占用高于 MyBatis；这是本次运行的资源表现，不能直接等同于数据库操作线程数或推断唯一性能瓶颈。')
para('CPU 使用率按 (1−空闲 CPU 时间变化率/总 CPU 时间变化率)×100% 计算，变化率采用 rate[5m]；内存使用率为 [1−(MemFree+Buffers+Cached)/MemTotal]×100%。JVM 活跃线程取自 spring:jvm_threads_live_threads。[4]')
para('CPU 的 5 分钟窗口包含相邻测试与部署活动，记录规则每 30 秒才产生新值，因此曲线适合观察整体趋势，不能精确定位十余秒测试内的瞬时峰值。未采集 SQL 分段耗时或锁等待证据，故不把延迟差异直接归因于锁竞争、磁盘或某条 SQL。')

# 10
page('3 总结')
para('实验完成了 JPA 性能测试、MyBatis 读写效率对比和两种实现的横向比较。90 组测试累计执行 111600 次请求，断言失败为 0，写入数量核验通过。')
para('基本测试中，MyBatis 在相同请求模型下均表现为读快于写，1000 线程时写入均值约为读取的 4.95 倍；相同档位的 JPA 写入耗时高于 MyBatis，但重复波动明显。扩展测试中，MyBatis 读取全部已测档位达标，写入 1200 线程三轮均达标、1300 线程存在未达标轮次；JPA 的达标情况非单调，不能得出唯一容量临界点。')
para('这些结果适用于本次 2 核/2 GiB 云主机、3912 条初始商品以及有限循环的请求模型。运行顺序、JIT 和缓存状态可能影响早期请求；持续并发、混合读写、长期稳定性及更大数据规模仍需另行验证。')
sub('程序与实验材料')
para('程序地址：https://github.com/Re1lya/lab3-mysql-benchmark')
para('仓库和完整材料包保存全部原始 JTL、90 份 JMeter HTML 报告、逐轮 CSV、监控时序及 164 张过程截图，并附 SHA-256 校验清单。基本与扩展数据分目录保留，可按测试组复核；正文仅选取代表性图表。测试结束后，应用及无关容器已恢复原运行状态。')
sub('参考资料')
for text in [
 '[1] 《实验三：MySQL 读写性能测试》，第 1–4 页。课程源码：https://gitee.com/mingqcn/spring-fundamentals，提交 fce17e7。',
 '[2] 《实验报告样例》，第 1–10 页。参考报告结构、负载档位与响应目标；数据来自本次实验。',
 '[3] Apache JMeter. Generating Dashboard Report. https://jmeter.apache.org/usermanual/generating-dashboard.html',
 '[4] Prometheus. HTTP API. https://prometheus.io/docs/prometheus/latest/querying/api/'
]:para(text)
out=EV/'deliverables';out.mkdir(exist_ok=True)
p=out/('report-draft.docx' if args.draft else '实验三_MySQL读写性能测试报告.docx')
doc.save(p);print(p)
