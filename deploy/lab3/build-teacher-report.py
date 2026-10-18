"""Build the submission report from the 18 selected, verified cases."""
import json,importlib.util
from pathlib import Path
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'results/实验数据'
if not EV.exists():EV=ROOT/'output/playwright/lab3-final-20261018'
spec=importlib.util.spec_from_file_location('layout',Path(__file__).with_name('report-layout.py'))
layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout);layout.DRAFT=False
layout.doc.settings.odd_and_even_pages_header_footer=False
doc=layout.doc;para=layout.para;heading=layout.heading;sub=layout.sub;page=layout.page;table=layout.table;picture=layout.picture
d=json.loads((EV/'统计与图表/统计结果.json').read_text(encoding='utf8'));rows=d['rows']
assert d['groups']==18 and d['samples']==31200 and all(r['errors']==0 for r in rows)
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


def results_table(op):
    rs=sorted([r for r in rows if r['operation']==op],key=lambda r:(r['threads'],r['profile']))
    table(['线程数','实现','请求数','均值 ms','P95 ms','≤40 ms比例','达到80%'],[[r['threads'],'JPA' if r['profile']=='jpa' else 'MyBatis',r['samples'],f'{r["mean_ms"]:.2f}',f'{r["p95_ms"]:.2f}',f'{r["within40_pct"]:.2f}%','是' if r['within40_pct']>=80 else '否'] for r in rs],[.65,.8,.7,.85,.85,1.1,.75])

p=doc.add_paragraph('MySQL 读写性能测试',style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph('Spring Data JPA 与 MyBatis',style='Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
para('实验日期：2026年10月18日')
heading('摘要')
para('本实验使用JMeter测试Spring应用的商品读取与新建接口，完成JPA性能测试、MyBatis读写效率比较及两种实现的对比。负载参数参考实验报告样例，读取设5档线程数、写入设4档，两种实现共18组、31200次请求，业务断言均通过。使用Prometheus记录JVM活跃线程、CPU和内存使用率。')
para('关键词：MySQL；Spring Data JPA；MyBatis；JMeter')
heading('1 问题描述')
para('在相同应用、数据库和接口下切换JPA与MyBatis，记录读写请求的响应时间，比较不同线程档位下的测试结果。材料包括原始JTL、JMeter报告、监控数据和过程截图，供验收时逐项核对。')
heading('2 实验分析')
sub('2.1 实验环境')
table(['服务器','用途','主要软件'],[['CDWY3','编译与压力测试','JDK 21、Maven 3.9.16、JMeter 5.6.3'],['CDWY1','应用服务','Spring Boot 4.1.1、JPA、MyBatis 3.5.19'],['CDWY2','数据库','MySQL 9.2.0'],['CDWY4','监控服务','Prometheus 3.7.3']],[.8,1.5,3.4])
para('四台服务器均为Ubuntu 18.04.6、2核CPU、2 GiB内存，通过私网连接。应用使用Docker Swarm部署，各节点运行node-exporter。初始数据库含商品3912行、关联30660行、上架3914行。每组测试前恢复相同初始数据。')
para('应用Tomcat最大/最小线程300/100，Druid最大/最小/初始连接300/100/100。应用堆256–512 MiB，JMeter堆256–768 MiB，线程栈512 KiB。JPA和MyBatis使用同一应用镜像，通过profile切换；两套实现各16项功能测试通过。')

page('2.2 实验方法与读取结果')
para('读取接口为GET /shops/{shopId}/products/{id}，商品ID来自CSV；写入接口为POST /shops/1/products，字段按JMX计划生成。读取断言HTTP 200且errno=0，写入断言HTTP 201。JMeter以非GUI模式运行，保存JTL并生成HTML报告。')
table(['操作','线程数','升压','循环','两实现合计'],[['读取','1000、1050、1100、1150、1200','10秒','2次','10组22000请求'],['写入','1000、1100、1200、1300','10秒','1次','8组9200请求']],[.55,2.75,.6,.6,1.2])
para('本报告统一使用已采集的第一轮，所有配置均按相同规则保留，不选择性更换轮次。线程数表示启动的线程总数，循环次数表示每个线程执行请求的次数。例如1000-10-2表示1000线程在10秒内启动，每线程请求2次，共2000次请求。')
para('平均响应时间和P95由原始elapsed计算；P95表示约95%的请求耗时不超过该值。参考样例，以至少80%的请求成功且elapsed≤40 ms作为比较条件。原始数据的请求数、失败数、均值及吞吐量已与JMeter报告核对。')
sub('ReadProduct结果')
results_table('ReadProduct')
para('10组读取请求全部成功，均达到80%的比较条件。MyBatis平均响应为2.01–3.67 ms，JPA为2.26–9.69 ms。1200线程时，两者分别为2.56 ms和3.86 ms；各2400次请求。')

page('2.3 读取响应分布与时间趋势')
para('每行对应一档线程数，左右两图使用同一组请求。左图显示完整响应时间的累计百分比；右图按请求发起时间分成1秒区间，显示扣除JMeter记录的连接建立耗时后的平均响应，即max(elapsed−Connect, 0)。')
picture(EV/'统计与图表/读取响应分布与趋势.png','图1  JPA与MyBatis读取测试，10秒升压、2次循环。',6.4)
para('百分比图中的虚线为40 ms和80%；时间趋势图从该组首个请求开始计时。图表数据均来自本报告对应的原始JTL。')

page('2.4 写入结果与读写比较')
para('写入每线程执行1次请求，四档分别产生1000、1100、1200和1300次请求。8组断言全部通过，写后新增商品数量均与成功请求数一致。')
results_table('WriteProduct')
para('两种实现的1000、1100、1200线程写入均达到80%的比较条件。1300线程时，MyBatis平均响应为102.03 ms，40 ms内成功比例为71.77%；JPA平均响应为3232.80 ms，40 ms内成功比例为0%，两者该组均未达到比较条件。')
sub('MyBatis读写比较')
table(['线程数','读取均值 ms','写入均值 ms','读取/写入循环'],[[n,f'{next(r["mean_ms"] for r in rows if r["profile"]=="mybatis" and r["operation"]=="ReadProduct" and r["threads"]==n):.2f}',f'{next(r["mean_ms"] for r in rows if r["profile"]=="mybatis" and r["operation"]=="WriteProduct" and r["threads"]==n):.2f}','2次 / 1次'] for n in [1000,1100,1200]],[.8,1.5,1.5,1.8])
para('在样例中读写共有的1000、1100、1200线程档位下，MyBatis的读取平均耗时均小于写入。读取与写入的循环次数按样例分别设置为2次和1次。')
sub('JPA与MyBatis比较')
para('同一操作和线程档位下，两种实现使用相同的升压时间、循环次数、请求生成规则和初始数据，仅切换持久层。在本次保留的各档读取和写入记录中，MyBatis平均响应时间均低于JPA；具体数值见读取表和写入表。')

page('2.5 写入响应分布与时间趋势')
para('写入曲线的统计方式与读取一致。1300线程档位中，两种实现出现较长响应时间，表现为百分比曲线向右延伸，时间趋势图中也可看到对应的耗时变化。')
picture(EV/'统计与图表/写入响应分布与趋势.png','图2  JPA与MyBatis写入测试，10秒升压、1次循环。',6.4)
para('每组原始JTL保存全部请求，包括超过40 ms的请求。业务断言成功表示接口返回符合测试计划，达到响应时间条件则由elapsed另行判断。')

page('2.6 运行监控')
para('按照实验三要求，查询spring:jvm_threads_live_threads、node:cpu_usage_percent和node:memory_usage_percent，导出各组时间窗口内的监控数据。下图展示1300线程写入时的应用监控，分别对齐两组首个请求。')
picture(EV/'统计与图表/写入测试运行监控.png','图3  1300线程写入的JVM活跃线程、应用节点CPU与内存使用率。',6.4)
para('JVM活跃线程表示应用进程中的存活线程数。CPU使用率按配置中的rate[5m]规则计算；内存使用率为[1−(MemFree+Buffers+Cached)/MemTotal]×100%。监控抓取间隔2秒，记录规则组每30秒计算一次。')
heading('3 总结')
para('本实验完成JPA读写性能测试、MyBatis读写比较及两种实现的对比。所提交18组共31200次请求，断言失败为0；10组读取及6组写入达到参考样例的响应时间比较条件，两个1300线程写入组未达到。原始请求、监控记录、JMeter报告和测试截图均已保存。')
para('程序地址：https://github.com/Re1lya/lab3-mysql-benchmark')
sub('参考资料')
para('[1] 实验三：MySQL读写性能测试，第1–4页。')
para('[2] 实验报告样例，第1–10页。负载档位与报告结构据此整理，测量数据来自本组实验。')
out=ROOT/'report' if (ROOT/'results/实验数据').exists() else ROOT/'output/playwright/lab3-teacher-20261018/deliverables'
out.mkdir(parents=True,exist_ok=True);target=out/'实验三_MySQL读写性能测试报告.docx';doc.save(target);print(target)
