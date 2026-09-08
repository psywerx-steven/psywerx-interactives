"""Run only the repository-defined governance suites plus Layer closeout gates."""
from __future__ import annotations
import datetime
import re
import shutil
import subprocess
import sys
import time
import closeout_psychological_layer_v1 as c

PATTERNS = [
    'test_migration_v0_3.py','test_relationship_intervention_v1.py',
    'test_bio_f01_pilot.py','test_bio_f01_governance_001.py','test_bio_f01_activation_001.py',
    'test_actions_events_v1.py','test_audit_family.py',
    'test_inf_f03_pilot.py','test_inf_f03_governance_001.py',
    'test_inf_f03_activation_audit_001.py','test_inf_f03_activation_001.py',
    'test_soc_f07_pilot.py','test_soc_f07_governance_001.py','test_network_state_vnext.py',
    'test_relational_state_v1.py','test_source_verification_v1.py',
    'test_psychological_layer*.py','test_soc_f07_completion.py']


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    results=[]
    def run(name,args,cwd=c.p.ROOT):
        started=time.monotonic()
        proc=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace')
        count=sum(int(x) for x in re.findall(r'Ran (\d+) tests?',proc.stdout))
        results.append({'name':name,'command':args,'exitCode':proc.returncode,
                        'tests':count,'seconds':round(time.monotonic()-started,3)})
        print(f'{name}: {"PASS" if not proc.returncode else "FAIL"}; tests={count}',flush=True)
        print(proc.stdout[-1600:],flush=True)
        if proc.returncode:raise RuntimeError(name)
    try:
        run('migration deterministic regeneration',[sys.executable,'scripts/build_migration_preview_v0_3.py'])
        for pattern in PATTERNS:
            run(pattern,[sys.executable,'-m','unittest','discover','-s','tests','-p',pattern])
        for script,args in [('relationship_intervention_v1.py',['--validate-repository']),
                            ('actions_events_v1.py',['--validate-repository']),
                            ('actions_events_synthetic.py',[]),('network_state_integrity.py',[])]:
            run(script,[sys.executable,'scripts/'+script,*args])
        run('scenario-service',[shutil.which('npm') or 'npm','test'],c.p.ROOT/'scenario-service')
        run('Python compilation',[sys.executable,'-m','compileall','-q','scripts','tests','experiments/network-state-vnext'])
        javascript=c.p.git('ls-files','--','*.js','*.mjs','*.cjs').splitlines()
        for path in javascript:run('JavaScript '+path,[shutil.which('node') or 'node','--check',path])
        run('git diff check',['git','diff','--check'])
        run('complete branch diff check',['git','diff','--check',c.p.BASELINE])
        c.validate();links=c.link_check();protected=c.p.check_protected()
        report={'status':'PASS','validatedWorkingTreeBasedOn':c.p.git('rev-parse','HEAD'),
                'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'requiredSteps':results,'pythonTests':sum(x['tests'] for x in results),
                'javascriptFilesParsed':len(javascript),'localLinks':links,'protectedScience':protected,
                'ci':'Final pushed head must independently pass both repository Linux and Windows jobs; local results are not CI results.',
                'noncanonicalCatchAllDiscoveryRun':False,'scientificGovernanceAuthorized':False}
        c.p.write(c.p.STORE/'validation-results.json',report)
        c.render()
        print(c.p.encode({k:v for k,v in report.items() if k!='requiredSteps'}),flush=True)
    except Exception:
        c.p.write(c.p.STORE/'validation-failure.json',{'steps':results,'status':'FAIL'})
        raise


if __name__=='__main__':main()
