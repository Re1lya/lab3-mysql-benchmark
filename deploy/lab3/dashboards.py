"""Generate JMeter HTML dashboards locally, without loading the benchmark nodes."""
import argparse, json, os, subprocess, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'output/playwright/lab3-comparison-20261018'

def main():
    global EV
    parser=argparse.ArgumentParser()
    parser.add_argument('--jmeter-home',required=True,type=Path)
    parser.add_argument('--java',default='java')
    parser.add_argument('--watch',action='store_true')
    parser.add_argument('--evidence',type=Path,default=EV)
    parser.add_argument('--expected',type=int,default=40)
    args=parser.parse_args()
    EV=args.evidence.resolve()
    (EV/'reports').mkdir(exist_ok=True)
    while True:
        if not (EV/'completed-runs.json').exists():
            if not args.watch:return
            time.sleep(10);continue
        rows=json.loads((EV/'completed-runs.json').read_text(encoding='utf8'))
        for row in rows:
            name=row['name'];dest=EV/'reports'/name
            if (dest/'index.html').exists():continue
            if dest.exists() and any(dest.iterdir()):
                raise RuntimeError('Incomplete report directory must be inspected: '+str(dest))
            command=[args.java,'-Xms256m','-Xmx1024m','-jar',str(args.jmeter_home/'bin/ApacheJMeter.jar'),
                     '-g',str(EV/'runs'/name/'samples.jtl'),'-o',str(dest),
                     '-j',str(EV/'logs'/('dashboard-'+name+'.log')),
                     '-Jjmeter.reportgenerator.overall_granularity=1000',
                     '-Jjmeter.reportgenerator.report_title='+name]
            result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=180)
            (EV/'logs'/('dashboard-'+name+'-console.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf8')
            if result.returncode:raise RuntimeError('Dashboard failed: '+name)
            assert (dest/'index.html').exists()
            print('REPORT',name,flush=True)
        if not args.watch or len(rows)==args.expected:break
        time.sleep(20)

if __name__=='__main__':main()
