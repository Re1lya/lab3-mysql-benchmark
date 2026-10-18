"""Final report: exclusively teacher-version data, with explicit source adaptations."""
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
hp=s.header.paragraphs[0];hp.text='Spring 框架课程实验三  |  教师版本 fce17e7';hp.runs[0].font.size=Pt(8)
fp=s.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER;fp.add_run('第 ')
f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');fp._p.append(f);fp.add_run(' 页')
for r in fp.runs:r.font.size=Pt(9)

doc.add_paragraph('MySQL 读写性能测试',style='Title')
doc.add_paragraph('基于教师测试计划的 JPA 与 MyBatis 对照实验',style='Subtitle')
para('实验日期  2026 年 10 月 18 日     |     四节点 Docker Swarm')
if args.draft:para(f'排版草稿：当前 {d["completed"]}/36 组，不作为最终提交结果。')
heading('摘要')
para('本实验依据《实验三：MySQL读写性能测试》及教师仓库最新提交 fce17e7，在四台 Ubuntu 18.04.6 云服务器上完成 Spring Data JPA 与 MyBatis 两种持久层的商品读取和新建测试。应用、MySQL、JMeter 和 Prometheus 分别位于独立节点，使用教师的随机写入内容、业务断言、单次循环和监控公式。')
para(f'正式矩阵为两种实现、两个接口、100/400/1000 个总线程各三次重复；所有组均为 10 秒升压、1 次循环。当前核验 {d["completed"]} 组、{d["samples"]:,} 次请求、{d["errors"]} 次失败。两种实现各 16 项真实 MySQL 功能测试全部通过；每组写入后的新增行数与成功请求数一致，读后数据量不变。')
table(['操作','实现','1000 线程吞吐量 req/s','平均响应 ms','P95 ms'],[
 ['读' if g['operation']=='ReadProduct' else '写',g['profile'].upper(),f"{g['success_rps_mean']:.1f} ± {g['success_rps_sd']:.1f}",f"{g['mean_ms_mean']:.2f}",f"{g['p95_ms_mean']:.2f}"] for g in groups if g['threads']==1000],[.45,.8,2.45,1.5,1.5])
para('表中为三次重复的均值，± 为吞吐量样本标准差；P95 列是三次 P95 的平均。该负载约每秒启动 100 个单次请求线程，主要比较此请求节奏下的响应表现，不能据此宣称测得最大吞吐量或支持 1000 个持续并发用户。CPU 指标遵循教师的 5 分钟平滑公式。')
para('本报告只采用教师版本重新采集的数据及截图。前期自定义 35 秒循环测试已停止并单独归档，没有混入下表、曲线或最终结论。')
para('关键词：MySQL；Spring Data JPA；MyBatis；JMeter；Prometheus')
para('程序地址：https://github.com/Re1lya/lab3-mysql-benchmark')

page('1 教师源码与版本核对')
para('本次正式来源为教师 Gitee 仓库提交 fce17e7dd6a204b91bbe89181ad6a30b09aa0270。已将最新版完整同步到独立本地工作区 spring-fundamentals-upstream，未向教师仓库上传任何改动。个人实验代码保存在公开 GitHub 仓库，凭据和私人项目不进入版本库。')
para('与前期 934bbaf 基线比较，SpringAOP 的 36 个主程序 Java 文件、Maven POM、clonefactory 和商品 CSV 内容一致；教师将目录 5.SpringAOP 改为 4.SpringAOP，并更新部署、JMeter 和监控配置。正式批次已采用这些最新配置，不仅更新目录名称。')
table(['教师内容','正式批次处理'],[
 ['读计划','保留 CSV 数据、GET 路径、HTTP 200 与 errno=0 断言'],
 ['写计划','保留随机中文与数值载荷、POST /shops/1/products、HTTP 201 断言'],
 ['循环方式','按参数给定总线程数，10 秒升压，每线程 1 次循环'],
 ['监控规则','13 条记录规则原文件应用，SHA-256 与教师原件一致'],
 ['采集设置','scrape 2s；全局evaluation 5s，规则组30s；timeout 1s'],
 ['应用资源参数','Tomcat max300/min100；Druid max300/min100/initial100'],
 ['日志','保留教师的业务 DEBUG 与 JPA show-sql=true']],[1.2,5.5])
sub('必要的执行适配')
para('指导书允许修改 hostname、端口及按实际内存调整 JVM。除此之外，修复原脚本 -D 与 __P 所需 -J 不一致、写 JMX 的 rump-up.period 拼写，并清除教师电脑的 Windows 结果绝对路径。否则“1000/10/1”可能不会按指导书意图执行。这些属于参数传递和路径修正，没有替换随机业务载荷。')
para('原件和适配件同时保存，reference/teacher-fce17e7/ 附哈希清单；正式执行的线程数量进一步由每组 JTL 请求数核验。数据库与监控密码改用外部私有配置，避免公开凭据。')

page('2 四节点环境与构建')
para('保留已购买服务器，每台 2 核 / 2 GiB、40 GiB 系统盘，实际可见内存约 1800 MiB，Ubuntu 18.04.6、Docker 20.10.21。内存高于指导书第 1 页的 1G 示例，报告如实披露；未修改机器规格。')
table(['节点','私网地址','主要任务'],[['CDWY3','172.31.12.156','编译及 JMeter，对应服务器 A'],['CDWY1','172.31.1.202','应用与 Swarm Manager，对应 B'],['CDWY2','172.31.8.46','MySQL，对应 C'],['CDWY4','172.31.1.19','Prometheus，对应 D']],[.8,1.55,4.35])
table(['组件','版本或参数'],[
 ['编译与运行','JDK 21.0.12.1；Maven 3.9.16；容器 Java 21.0.6'],['应用','Spring Boot 4.1.1；MyBatis 3.5.19；MyBatis-Spring 4.0.0'],
 ['数据库与负载','MySQL 9.2.0；JMeter 5.6.3'],['监控','Prometheus 3.7.3；node-exporter 1.10.2'],
 ['应用 JVM','堆 256–512 MiB；Xss 512 KiB；容器内存上限 1 GiB'],['JMeter JVM','堆 256–768 MiB；Xss 512 KiB；Metaspace 上限 192 MiB'],
 ['报告粒度','jmeter.reportgenerator.overall_granularity=1000']],[1.2,5.5])
para('先安装 clonefactory，再对 core 执行 Maven install，随后打包应用并构建镜像。使用 package + docker build 完成相同打包目的，避开会删除受保护历史镜像的课程脚本阶段。正式镜像为 lab3-teacher-20261018，同一镜像按 profile 切换持久层。')
para('镜像 ID：sha256:b2e12d68ea0cd4154ab9604b48b474b84cf7b91407f558a89df875e48e9074dc。构建节点和应用节点归档校验和相同。部署入口为 4. SpringAOP/conf/docker/productdemoaop-docker.yml。')

page('3 持久层实现与功能验证')
para('读接口为 GET /shops/{shopId}/products/{id}，写接口为 POST /shops/{shopId}/products。两种 profile 共用 Controller、Service、DAO、DTO、数据库结构和业务事务边界。写路径新增商品后读取记录和关联信息构造响应，比较的是完整业务接口。')
table(['部分','JPA','MyBatis'],[['仓库','Spring Data Repository','同接口的 MyBatis Repository'],['SQL','Hibernate 生成','Lab3Mapper.xml'],['事务','JPA 事务管理器','DataSourceTransactionManager'],['会话','持久化上下文','SqlSessionTemplate'],['生成字段','数据库生成创建时间回读','插入后读取数据库记录']],[1.1,2.7,2.9])
para('MyBatis profile 关闭 Hibernate 与 JPA 仓库自动配置，使用 Spring 管理的 SqlSessionTemplate。[2] JPA 创建时间标记为数据库生成并回读，以保持响应语义；GoodsPo 去掉写死的旧库 schema，使关联查询使用当前实验库。原测试的 VO 类型错误已修正；删除测试改为新建无外键关联的商品。')
picture(EV/'screenshots/tests-final.png','图 1  教师数据库和配置下，JPA、MyBatis 各 16 项功能测试通过。真实 SSH 输出渲染截图。',6.5)
para('功能测试使用真实 MySQL 并通过事务回滚。完整日志保留在 logs/test-jpa.log 和 logs/test-mybatis.log；它们是功能验证材料，不计入性能样本。')

page('4 数据基线与过程控制')
para('从教师原始 product.sql 导入新建专用库 oomall_lab3_teacher：商品 3912 行、关联关系 30660 行、上架记录 3914 行，商品最大 ID 5461，自增起点 5609。原 oomall_demo 保持 3913 行，未用实验数据覆盖。')
picture(EV/'screenshots/teacher-database-init.png','图 2  教师 SQL 导入后基线行数核验。真实 SSH 输出渲染截图。',6.3)
para('每组前删除专用实验库中本轮新增记录，恢复基线和自增起点；每组后核对写入增长量与成功请求数，读后数量保持不变。所有检查语句、返回值和每组 metadata.json 均留存。')
picture(EV/'screenshots/prometheus-targets.png','图 3  教师配置下的 Prometheus Targets 实际页面，6 个目标均为 UP。',6.3)
para('正式采集前停止独立 demo 容器，结束后恢复；控制器有心跳与异常恢复措施。采集中不在发压节点编译或生成 HTML，HTML 和统计在本机离线生成。')

page('5 实验设计与监控口径')
table(['因素','设置'],[['实现','JPA、MyBatis'],['接口','读取、新建商品'],['总线程','100、400、1000'],['升压与循环','全部 10 秒升压、1 次循环'],['重复','每个组合 3 次，共 36 组、18000 次请求'],['次序','第1/3轮 JPA→MyBatis，第2轮 MyBatis→JPA；组内固定种子打乱'],['间隔','首组前等待5分钟；每组前空闲15秒，组后等待12秒采集监控']],[1.15,5.55])
para('1000/10/1 直接对应指导书第 3 页示例，400 对应教师 JMX 默认线程数量，100 是相同计划的低负载对照。没有沿用前期 35 秒循环或固定写载荷，也没有向正式请求加入额外后处理器。')
sub('请求统计')
para('全程吞吐量为成功请求数除以“最后完成时间−首次发起时间”。延迟直接使用原始 JTL 的 elapsed；不扣除连接时间，不剔除升压、慢请求或异常请求。P50/P90/P95/P99 使用线性插值，重复试验以每轮为观察单位，报告均值、样本标准差与范围。JMeter HTML 采用全程样本；分位数估计器差异可能造成小幅不同。[3]')
sub('教师监控公式')
para('CPU 使用各主机 idle CPU 时间的 rate[5m] 除以全部 CPU 时间 rate[5m]，再计算 1−该比值。内存使用率为 1−(MemFree+Buffers+Cached)/MemTotal。JVM 活跃线程直接来自 spring:jvm_threads_live_threads。规则文件保持教师原件。')
para('CPU 是最近 5 分钟平滑值，包含组前与相邻组负载，不能解释为单组 10 秒的瞬时峰值；内存公式与 MemAvailable 口径不同，不能混用前期数据。教师的两个规则组显式每30秒评估，覆盖全局5秒设置。query_range 每2秒导出只是对已记录值取样，重复时间点不代表新的独立测量；10秒组内可能没有新规则样本，图中保留这一限制。原始12类时序JSON全部保存。[4]')

page('6 正式读写结果')
para('下表汇总三次重复；吞吐量为均值 ± 样本标准差，单位 req/s。延迟各列为每轮对应统计量的平均，单位 ms。P95 均值不等于把三轮请求合并后的整体 P95。')
table(['操作','实现','线程','吞吐量 req/s','均值 ms','P95 ms','P99 ms'],[
 ['读' if g['operation']=='ReadProduct' else '写',g['profile'].upper(),g['threads'],f"{g['success_rps_mean']:.1f} ± {g['success_rps_sd']:.1f}",f"{g['mean_ms_mean']:.2f}",f"{g['p95_ms_mean']:.2f}",f"{g['p99_ms_mean']:.2f}"] for g in groups],[.45,.8,.55,1.7,.9,.9,.9])
para(f'累计 {d["samples"]:,} 次请求、{d["errors"]} 次失败。写测试的数据库增量与成功请求数逐组一致；读测试没有改变商品行数。所有逐次统计见 analysis/all-runs.csv。')
picture(EV/'analysis/throughput.png','图 4  教师单循环计划的成功吞吐量。请求节奏受 10 秒升压约束，不能作为饱和容量曲线。',6.5)

page('7 延迟与重复波动')
picture(EV/'analysis/p95.png','图 5  各组 P95 的三轮均值和样本标准差。',6.5)
records=[]
for g in groups:
 a={r['repeat']:r for r in rows if (r['profile'],r['operation'],r['threads'])==(g['profile'],g['operation'],g['threads'])}
 records.append([('读 ' if g['operation']=='ReadProduct' else '写 ')+g['profile'].upper(),g['threads'],*[f"{a[i]['mean_ms']:.2f}" if i in a else '未完成' for i in [1,2,3]],f"{g['mean_ms_sd']:.2f}"])
table(['操作与实现','线程','第1轮均值','第2轮均值','第3轮均值','标准差'],records,[1.3,.6,1.2,1.2,1.2,1.2])
para('表中延迟单位 ms。每个实现块重新部署，未额外加入教师计划之外的长时间预热；冷启动、JIT 和缓存积累可能影响早期请求。保留三轮全部结果，以显示这种波动，不挑选最好的一轮代替总体。')

page('8 响应分布与监控曲线')
picture(EV/'analysis/ReadProduct-latency.png','图 6  第3轮1000线程读取的完整延迟分布与每秒平均响应耗时。',6.5)
picture(EV/'analysis/WriteProduct-latency.png','图 7  第3轮1000线程写入的完整延迟分布与每秒平均响应耗时。',6.5)
para('展示条件固定为第3轮1000线程，未按结果高低挑选。线程分10秒依次启动、完成一次请求后退出，因此配置线程总数与实际同时活跃线程不同。')

page('9 教师指标的时间变化')
picture(EV/'analysis/ReadProduct-monitoring.png','图 8  读取示例的线程、应用CPU、应用内存及发压CPU；CPU保留教师5分钟口径。',6.1)
picture(EV/'analysis/WriteProduct-monitoring.png','图 9  写入示例同类指标。横轴各自对齐首个请求，两种实现不是同时发压。',6.1)

page('10 JMeter 原始报告与截图')
para('以下为本次教师计划运行后，从未经修改的 JTL 生成的 JMeter HTML 实际页面截图。HTML 汇总粒度为1000ms，完整报告36份分别保存。表格中的成功率和请求数量与本次元数据核验。')
picture(EV/'screenshots/jmeter-jpa-read-full.png','图 10  JPA 第3轮1000线程读取，JMeter实际HTML报告页面。完整分辨率原图另附。',5.6)
picture(EV/'screenshots/jmeter-mybatis-write-statistics.png','图 11  MyBatis 第3轮1000线程写入，JMeter实际统计区域截图。',6.5)
para('1000/10/1 各组必须恰有1000条样本。完整截图还包括JPA写入、MyBatis读取及Prometheus三个课程查询，均存于screenshots/。截图区分实际网页和真实日志渲染页面，不将补拍图称为实时压测现场。')

page('11 结果解释与适用范围')
for op,label in [('ReadProduct','读取'),('WriteProduct','写入')]:
 if all((p,op,1000) in by for p in ['jpa','mybatis']):
  a=by['jpa',op,1000];b=by['mybatis',op,1000]
  para(f'在1000线程、10秒升压、1次循环的{label}条件下，JPA平均响应为{a["mean_ms_mean"]:.2f} ms，MyBatis为{b["mean_ms_mean"]:.2f} ms；对应P95均值为{a["p95_ms_mean"]:.2f} ms与{b["p95_ms_mean"]:.2f} ms。三次重复的样本标准差已在表中给出，均值差异仅描述本次运行。')
para('如果两者吞吐量都接近总请求数除以10秒，首先说明测试受线程启动节奏约束，不能据此判定二者极限吞吐量相等。这里更适合结合响应延迟、尾延迟和实际活动线程比较当前负载表现。')
para('JVM线程包含工作线程和维护线程，不等于JMeter并发。CPU的5分钟窗口覆盖邻近测试和部署活动，适合观察整体趋势；不能凭该曲线单独推断某条SQL、锁竞争或磁盘是唯一瓶颈。本实验没有采集火焰图或锁等待证据。')
para('结果仅适用于本次2核/2GiB云主机、3912条商品、教师随机数据及应用路径。没有执行持续并发饱和测试、混合读写、长期稳定性或大规模数据测试，不外推为所有JPA/MyBatis系统的排名。零错误表示本次计划断言和行数核验通过，不等于不存在任何程序缺陷。')
sub('恢复与留存')
para('结束后恢复JPA应用到原oomall_demo，恢复demo原运行状态，核验服务副本、应用健康、6个监控目标及专用库基线。原始JTL以gzip无损压缩发布，附SHA-256；统计CSV、HTML和图表均为衍生材料，复核以原始JTL及监控JSON为准。')
para('回滚材料在各节点 /root/backups/20261018-lab3-teacher；前期镜像与源码备份均保留。本机原改动备份在 .codex/backups/spring-fundamentals/20261018-before-upstream-sync。')

page('12 指导书对应与提交材料')
table(['页码','指导书要求','本次材料'],[
 ['1','SpringBoot、MySQL、RESTful读写','两种profile、相同接口、真实MySQL功能测试'],
 ['1','四台Ubuntu主机分工','第2节；内存规格差异已披露'],['2','JMeter5.6.3、PATH、内存参数','环境日志与截图、运行脚本'],
 ['2','1000ms报告粒度、目标IP端口','user.properties、JMX与生成日志'],['3','clonefactory、core、应用与镜像','重新构建日志和镜像校验和'],
 ['3','私网监控、targets/rules','6个UP目标、13条教师规则、真实页面截图'],['3','三个课程查询','教师公式、时序JSON与监控截图'],
 ['3','1000/10/1示例与JTL/HTML','包含12组原例，另有100/400线程参数对照'],['4','Git地址、原始数据、报告','个人公开仓库、原始数据包、本报告'],
 ['4','教师认可程序及原始数据','待教师实际审核，不代为宣称已通过']],[.5,2.55,3.65])
para('Git地址：https://github.com/Re1lya/lab3-mysql-benchmark')
para('正式证据目录：output/playwright/lab3-teacher-20261018。前期探索批次单独保存在lab3-comparison-20261018，不参与本报告计算。')
sub('参考资料')
for text in ['[1] 《实验三：MySQL读写性能测试》，第1–4页；教师源码 https://gitee.com/mingqcn/spring-fundamentals，提交fce17e7。',
 '[2] MyBatis-Spring，Using an SqlSession。https://mybatis.org/spring/sqlsession.html',
 '[3] Apache JMeter，Generating Dashboard Report。https://jmeter.apache.org/usermanual/generating-dashboard.html',
 '[4] Prometheus，HTTP API。https://prometheus.io/docs/prometheus/latest/querying/api/','在线文档核对日期：2026年10月18日。']:
 para(text)
out=EV/'deliverables';out.mkdir(exist_ok=True)
p=out/('teacher-report-draft.docx' if args.draft else '实验三_MySQL读写性能测试_教师版本.docx')
doc.save(p);print(p)
