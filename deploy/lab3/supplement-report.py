"""Add the sample-inspired experiment to the report only after collection completes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'output/playwright/lab3-supplement-20261018'

def append(layout):
    d=json.loads((EV/'analysis/results.json').read_text())
    assert d['complete'] and len(d['rows'])==54 and d['samples']==93600
    assert (EV/'restored.json').exists()
    page,para,sub,table,picture=layout.page,layout.para,layout.sub,layout.table,layout.picture
    page('2.12 扩展负载实验设计')
    para('在基本读写性能测试的基础上，进一步采用连续线程档位观察负载增加后的变化。读取设置 1000、1050、1100、1150、1200 个总线程，10 秒升压，每线程循环 2 次；写入设置 1000、1100、1200、1300 个总线程，10 秒升压，每线程循环 1 次。JPA 与 MyBatis 均完成全部组合，每组重复 3 次。')
    table(['接口','线程档位','循环','每轮总请求','测试组数'],[
        ['读','1000/1050/1100/1150/1200',2,'2000/2100/2200/2300/2400',30],
        ['写','1000/1100/1200/1300',1,'1000/1100/1200/1300',24]],[.45,2.15,.5,2.9,.7])
    para(f'扩展实验共完成 {d["completed"]} 组、{d["samples"]:,} 次请求，其中失败 {d["errors"]} 次。该批次独立保存原始数据，与前述 36 组基本测试分别统计。应用镜像、测试计划、数据库初始状态、随机载荷规则、断言和监控规则保持一致，每组结束后核验数据库行数。')
    sub('响应时间目标与判断方法')
    para('将“至少 80% 的全部请求成功且响应时间不超过 40 ms”设为扩展实验的比较目标。[5] 每轮按满足条件的请求数除以该轮全部请求数计算比例，失败请求不算达标；三轮均达到 80% 时，才将该档位标记为本次重复测试均满足目标。该目标不作为所有应用通用的标准，亦不与 JMeter HTML 默认的 Apdex 阈值混用。')
    sub('连接时间与完整响应时间')
    para('主要统计使用 JTL 的原始 elapsed，保留连接建立、响应接收和慢请求。为便于观察建立连接的影响，另外计算 max(elapsed−Connect, 0) 的辅助统计，两种口径分别列出。扣除 Connect 不能消除所有网络开销，也不能得到纯 SQL 或服务端执行时间。响应分布和时间趋势图均以原始 elapsed 为主。')
    sub('控制条件与可解释范围')
    para('两种实现按轮次交替先后顺序，各轮组合使用固定种子打乱。循环次数改变请求序列和连接复用，因此基本测试的 1000-10-1 与扩展读取的 1000-10-2 分开分析。扩展读写循环数不同，主要比较各操作内部的档位变化及同接口的框架差异；相同请求模型下的读写效率比较见第 2.7 节。线程总数不是瞬时并发数。')
    para('每轮切换实现时重新部署应用，通过健康检查后等待空闲窗口，未额外发送业务预热请求。首组与后续组的JIT和缓存状态可能不同；轮间波动必须与执行顺序一起解释，不能仅凭某轮未达标认定容量不足。')
    for idx,(op,label) in enumerate([('ReadProduct','读取'),('WriteProduct','写入')],13):
        page(f'2.{idx} 扩展{label}测试结果')
        para('线程设置均为 10 秒升压；响应均值和 P95 是三次重复对应统计量的平均，单位 ms。“≤40 ms”列为成功且满足响应目标的请求比例，三轮范围展示重复稳定性。“扣连接”列为 elapsed−Connect 口径的三轮平均达标比例。')
        values=sorted([g for g in d['groups'] if g['operation']==op],key=lambda g:(g['threads'],g['profile']))
        table(['线程','实现','均值 ms','P95 ms','≤40 ms均值','三轮比例范围','扣连接比例'],[[g['threads'],'JPA' if g['profile']=='jpa' else 'MyBatis',f'{g["mean_ms_mean"]:.2f}',f'{g["p95_ms_mean"]:.2f}',f'{g["within40_pct_mean"]:.1f}%',f'{g["within40_pct_min"]:.1f}–{g["within40_pct_max"]:.1f}%',f'{g["within40_adjusted_pct_mean"]:.1f}%'] for g in values],[.6,.75,.85,.85,1.05,1.45,1.15])
        for profile in ['jpa','mybatis']:
            a=[g for g in values if g['profile']==profile];passed=[str(g['threads']) for g in a if g['within40_all_repeats_pass']]
            name='JPA' if profile=='jpa' else 'MyBatis'
            para(f'{name} {label}在三轮均满足目标的线程档位为：'+('、'.join(passed) if passed else '无')+'。'+f'最高已测档位 {a[-1]["threads"]} 线程的平均响应为 {a[-1]["mean_ms_mean"]:.2f} ms，≤40 ms 比例三轮范围为 {a[-1]["within40_pct_min"]:.1f}%–{a[-1]["within40_pct_max"]:.1f}%。')
        para('逐轮响应分位数、吞吐量、实际活动线程峰值、连接时间和监控统计均保存在扩展实验的 all-runs.csv。表中指标保留全部请求；单次异常值和未达标轮次均未剔除。')
    fig=14
    for op,label in [('ReadProduct','读取'),('WriteProduct','写入')]:
        for part in [1,2]:
            page(f'2.{15+(fig-14)} 扩展{label}响应曲线 {part}')
            picture(EV/f'analysis/{op}-detail-{part}.png',f'图 {fig}  第3轮{label}各线程档位的响应时间百分比分布和1秒响应趋势。',6.5)
            ns=([1000,1050,1100] if part==1 else [1150,1200]) if op=='ReadProduct' else ([1000,1100] if part==1 else [1200,1300])
            for n in ns:
                a=next(r for r in d['rows'] if r['profile']=='jpa' and r['operation']==op and r['threads']==n and r['repeat']==3)
                b=next(r for r in d['rows'] if r['profile']=='mybatis' and r['operation']==op and r['threads']==n and r['repeat']==3)
                para(f'{n}线程：JPA与MyBatis的P95分别为{a["p95_ms"]:.2f}和{b["p95_ms"]:.2f} ms，40 ms内成功比例分别为{a["within40_pct"]:.1f}%和{b["within40_pct"]:.1f}%。这是图示第3轮的数据，完整三轮统计见前表。')
            para('标签依次为总线程数、升压秒数、循环次数。左图相同比例下曲线越低，响应越快；右图按请求发起时间划分1秒区间，两种实现各自对齐首个请求。曲线保留连接时间与全部慢请求，局部波动不能单独证明某种数据库瓶颈。')
            fig+=1
    page('2.19 响应目标与负载边界')
    picture(EV/'analysis/within40-target.png','图 18  各档位40 ms内成功请求比例。粗线为三轮均值，细线为各轮，虚线为80%目标。',6.5)
    for profile in ['jpa','mybatis']:
        for op,label in [('ReadProduct','读'),('WriteProduct','写')]:
            a=sorted([g for g in d['groups'] if g['profile']==profile and g['operation']==op],key=lambda g:g['threads'])
            flags=[g['within40_all_repeats_pass'] for g in a]
            prefix=('JPA' if profile=='jpa' else 'MyBatis')+label+'操作：'
            if all(flags):msg=f'全部已测档位均满足目标，最高已测档位为 {a[-1]["threads"]} 线程；范围内未找到失效边界。'
            elif not any(flags):msg=f'最低已测档位 {a[0]["threads"]} 线程也未在三轮中稳定满足目标，不能据此确定更低负载的临界值。'
            elif flags==sorted(flags,reverse=True):
                i=flags.index(False);msg=f'{a[i-1]["threads"]} 线程三轮均达标，而相邻 {a[i]["threads"]} 线程未全部达标，可将两档之间作为后续细化测试区间；当前点测尚不足以确定精确容量。'
            else:msg='达标情况随档位并非单调变化，重复波动影响结论，当前测试无法给出唯一负载临界点。'
            para(prefix+msg)
    para('上述判断仅针对本次预设响应目标和有限循环的请求模型。持续并发、长期稳定性和混合读写容量不在本轮测试范围内。原始 elapsed 与扣连接口径出现差异时，以完整响应时间作为主要判断依据。')
    page('2.20 扩展测试运行指标')
    picture(EV/'analysis/ReadProduct-monitoring.png','图 19  第3轮1200线程双循环读取的运行指标，按各组首个请求对齐。',6.0)
    picture(EV/'analysis/WriteProduct-monitoring.png','图 20  第3轮1300线程单循环写入的运行指标，按各组首个请求对齐。',6.0)
    para('监控规则与基本实验一致。CPU为5分钟平均变化率，记录规则每30秒评估，不能精确定位十余秒测试内的瞬时峰值；JVM线程包含维护线程，不能直接等同于JMeter活动线程。每组的12类完整时序均已保存。')
    page('2.21 扩展测试原始报告截图')
    para('扩展实验的54组原始JTL分别生成独立JMeter HTML报告，并逐组保存真实浏览器截图。以下选取MyBatis第3轮最高已测读写档位的Statistics区域，与前文的统计表和响应曲线对应。完整页面、图表和报告原文件随材料提供。')
    picture(EV/'screenshots/mybatis-r3-read-statistics.png','图 21  MyBatis第3轮1200线程读取，2循环，共2400次请求的实际JMeter统计区域。',6.5)
    picture(EV/'screenshots/mybatis-r3-write-statistics.png','图 22  MyBatis第3轮1300线程写入，1循环，共1300次请求的实际JMeter统计区域。',6.5)
    para('独立分析使用JTL的全部请求，样本数、失败数、平均响应时间、最小值、最大值和吞吐量逐组与JMeter报告核对。两者的分位数估计方法可能产生小幅差异，报告中的P95统一使用线性插值统计。40 ms目标比例由原始请求逐条计算，不使用HTML的Apdex得分代替。')
