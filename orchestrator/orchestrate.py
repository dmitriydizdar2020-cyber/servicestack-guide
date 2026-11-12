#!/usr/bin/env python3
"""AffiliateOS v1: deterministic zero-API task orchestrator.

Runs on Python standard library. This is a task-state engine, not an LLM runtime.
Only actual scheduled ChatGPT runs or authorized operators can execute role work.
"""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent
DEFAULT_STATE = ROOT / 'state' / 'tasks.json'
DEFAULT_EVENTS = ROOT / 'state' / 'events.jsonl'
VALID_STATES = {'ready','claimed','awaiting_qa','rework','qa_passed','rejected','published','blocked','cancelled'}
VALID_ROLES = {'CEO-01','ORC-01','SID-00','EDT-01','OPS-01','QAD-01','COM-01','ANA-01','AES-00'}
CLOSE_STATES = {'published','cancelled','rejected'}
ACTIVE_STATES = {'ready','rework','claimed','awaiting_qa','qa_passed','blocked'}
ROLE_ORDER = ('OPS-01','EDT-01','SID-00','COM-01','ANA-01','AES-00')

class OrchestrationError(Exception):
    pass

def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')

def load_state(path: pathlib.Path = DEFAULT_STATE) -> dict[str,Any]:
    with path.open(encoding='utf-8') as h: data=json.load(h)
    if not isinstance(data,dict) or not isinstance(data.get('tasks'),list):
        raise OrchestrationError('Missing tasks array')
    return data

def atomic_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.new')
    tmp.write_text(content,encoding='utf-8')
    os.replace(tmp,path)

def save_state(data:dict[str,Any],path:pathlib.Path=DEFAULT_STATE)->None:
    data['updated_at']=stamp()
    atomic_write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def event_hash(event:dict[str,Any])->str:
    normalized=json.dumps(event,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    return hashlib.sha256(normalized).hexdigest()[:16]

def log_event(event:dict[str,Any],path:pathlib.Path=DEFAULT_EVENTS)->str:
    event=dict(event)
    event.setdefault('at',stamp())
    event['id']=event_hash(event)
    with path.open('a',encoding='utf-8') as h:h.write(json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n')
    return event['id']

def task_by_id(data:dict[str,Any],tid:str)->dict[str,Any]:
    matches=[x for x in data['tasks'] if x.get('id')==tid]
    if len(matches)!=1:raise OrchestrationError(f'Task {tid} must exist exactly once')
    return matches[0]

def validate(data:dict[str,Any], base_dir:pathlib.Path|None=None)->list[dict[str,str]]:
    """Issues with severity CRITICAL / WARNING; no pretending QA has run."""
    issues=[]
    def issue(sev:str,code:str,msg:str):issues.append({'severity':sev,'code':code,'message':msg})
    if data.get('schema_version')!='1.0':issue('CRITICAL','SCHEMA','Unsupported schema')
    if data.get('external_spend_ceiling_usd')!=0:issue('CRITICAL','BUDGET','External spend ceiling must stay 0 before verified cash payout')
    tasks=data.get('tasks',[])
    ids=[t.get('id') for t in tasks]
    if len(ids)!=len(set(ids)):issue('CRITICAL','DUPLICATE_ID','Duplicate task IDs')
    known=set(ids)
    for task in tasks:
        tid=task.get('id','?')
        if task.get('status') not in VALID_STATES:issue('CRITICAL','STATUS',f'{tid}: invalid status')
        if task.get('owner') not in VALID_ROLES:issue('CRITICAL','OWNER',f'{tid}: unknown owner')
        if task.get('priority') not in {'P0','P1','P2','P3'}:issue('CRITICAL','PRIORITY',f'{tid}: bad priority')
        if task.get('spend_usd',0)!=0:issue('CRITICAL','SPEND',f'{tid}: nonzero spend in $0 mode')
        if task.get('attempts',0)>task.get('max_attempts',2) and task.get('status')=='claimed':
            issue('CRITICAL','RETRY_LIMIT',f'{tid}: too many active attempts')
        for dep in task.get('depends_on',[]):
            if dep==tid or dep not in known:issue('CRITICAL','BAD_DEP',f'{tid}: missing/self dependency {dep}')
        if task.get('status')=='qa_passed' and not task.get('qa',{}).get('decision')=='PASS':
            issue('CRITICAL','QA_BYPASS',f'{tid}: approved without QA PASS')
        if task.get('status')=='published':
            q=task.get('qa',{})
            if q.get('decision')!='PASS' or not q.get('evidence') or q.get('reviewer_role')!='QAD-01':
                issue('CRITICAL','PUBLISH_WITHOUT_QA',f'{tid}: no independent QA evidence')
            if not task.get('deployment_proof'):
                issue('CRITICAL','NO_DEPLOY_PROOF',f'{tid}: publication unverified')
        qa=task.get('qa',{})
        if qa.get('decision')=='PASS':
            if qa.get('reviewer_role')!='QAD-01' or qa.get('reviewer_run_id')==task.get('producer_run_id'):
                issue('CRITICAL','NO_INDEPENDENCE',f'{tid}: QA must use distinct independent run')
            if not qa.get('evidence'):
                issue('CRITICAL','QA_EVIDENCE',f'{tid}: QA PASS lacks evidence')
        if task.get('status')=='claimed' and not task.get('lock',{}).get('run_id'):
            issue('CRITICAL','MISSING_LOCK',f'{tid}: claimed without run lock')
        if base_dir and task.get('artifact_path') and (task.get('status') in ('awaiting_qa','qa_passed','published')):
            p=base_dir / task['artifact_path']
            if not p.exists():issue('CRITICAL','MISSING_ARTIFACT',f'{tid}: missing local artifact {p}')
    graph={t['id']:t.get('depends_on',[]) for t in tasks if t.get('id')}
    visiting=set();visited=set()
    def visit(n):
        if n in visiting:issue('CRITICAL','DEPENDENCY_CYCLE',f'Cycle through {n}');return
        if n in visited:return
        visiting.add(n)
        for dep in graph.get(n,[]):
            if dep in graph:visit(dep)
        visiting.remove(n);visited.add(n)
    for n in graph:visit(n)
    return issues

def dependency_ready(data:dict[str,Any], task:dict[str,Any])->bool:
    # A dependent task is ready only after an actual deploy or explicit completed non-public task.
    return all(task_by_id(data,dep)['status']=='published' for dep in task.get('depends_on',[]))

def next_task(data:dict[str,Any], role:str|None=None)->dict[str,Any]|None:
    candidates=[]
    for t in data['tasks']:
        if t['status'] not in {'ready','rework','blocked','qa_passed','awaiting_qa'}:continue
        if role and t['owner']!=role:continue
        if t['status']=='blocked' and not dependency_ready(data,t):continue
        if t['status'] in {'ready','rework','blocked'} and not dependency_ready(data,t):continue
        candidates.append(t)
    candidates.sort(key=lambda t:(int(t['priority'][1]), t['status']!='awaiting_qa',t['id']))
    return candidates[0] if candidates else None

def claim(data:dict[str,Any],tid:str,role:str,run_id:str)->dict[str,Any]:
    if not run_id or len(run_id)>100:raise OrchestrationError('Run ID required')
    t=task_by_id(data,tid)
    if role!=t['owner'] or role=='QAD-01':raise OrchestrationError('Only non-QA assigned owner can claim task')
    if t['status']=='claimed' and t.get('lock',{}).get('run_id')==run_id:return t
    if t['status'] not in {'ready','rework','blocked'}:raise OrchestrationError('Task is not claimable')
    if not dependency_ready(data,t):raise OrchestrationError('Dependencies not finished')
    if t['attempts']>=t['max_attempts']:raise OrchestrationError('Retry limit; escalate to CEO')
    t['status']='claimed';t['attempts']+=1;t['lock']={'run_id':run_id,'role':role,'claimed_at':stamp()}
    t['producer_run_id']=run_id
    return t

def handoff(data:dict[str,Any],tid:str,role:str,run_id:str,evidence:str,artifact:str,summary:str)->dict[str,Any]:
    t=task_by_id(data,tid)
    if t['status']!='claimed' or t.get('lock',{}).get('run_id')!=run_id or t['owner']!=role:
        raise OrchestrationError('Handoff requires actual owner + matching lock')
    if not evidence or not artifact or not summary:raise OrchestrationError('Evidence, artifact and concise summary required')
    t['status']='awaiting_qa';t['owner']='QAD-01';t['producer_role']=role;t['artifact_path']=artifact
    t['handoff']={'run_id':run_id,'from_role':role,'to_role':'QAD-01','evidence':evidence,'summary':summary[:500],'at':stamp()}
    t['lock']=None
    return t

def review(data:dict[str,Any],tid:str,review_run_id:str,decision:str,evidence:str,reason:str='',fix_owner:str='')->dict[str,Any]:
    t=task_by_id(data,tid)
    if t['status']!='awaiting_qa':raise OrchestrationError('QA can only review actual handoffs')
    if not review_run_id or review_run_id==t.get('producer_run_id'):
        raise OrchestrationError('Independent QA requires distinct real run id')
    if decision not in {'PASS','REWORK','REJECT'}:raise OrchestrationError('Bad decision')
    if not evidence:raise OrchestrationError('Real evidence required')
    if decision!='PASS' and not reason:raise OrchestrationError('Actionable reason required')
    t['qa']={'decision':decision,'reviewer_role':'QAD-01','reviewer_run_id':review_run_id,'evidence':evidence,'reason':reason,'at':stamp()}
    if decision=='PASS':
        t['status']='qa_passed';t['owner']='OPS-01';t['next_owner']='OPS-01';t['fix_request']=None
    elif decision=='REWORK':
        orig=t.get('producer_role') or fix_owner
        if orig not in VALID_ROLES or orig=='QAD-01':raise OrchestrationError('Original author role unknown')
        t['status']='rework';t['owner']=orig;t['fix_request']={'reason':reason,'qa_evidence':evidence,'assigned_to':orig,'acceptance':'Resolve exactly this defect and provide changed artifact/source proof'}
        if t['attempts']>=t['max_attempts']:
            t['status']='blocked';t['owner']='CEO-01';t['fix_request']['escalation']='Retry limit reached; CEO redesign/reassign/kill'
    elif decision=='REJECT':
        t['status']='rejected';t['owner']='CEO-01';t['fix_request']={'reason':reason,'qa_evidence':evidence,'escalation':'CEO decides whether to stop or create a different validated task'}
    return t

def release(data:dict[str,Any],tid:str,role:str,commit:str,url:str,site_root:pathlib.Path|None=None)->dict[str,Any]:
    t=task_by_id(data,tid)
    if role!='OPS-01' or t['owner']!='OPS-01' or t['status']!='qa_passed':
        raise OrchestrationError('Only OPS can publish independently QA-passed task')
    if t.get('qa',{}).get('reviewer_role')!='QAD-01':raise OrchestrationError('Missing QA reviewer')
    if not commit or not url.startswith('https://'):raise OrchestrationError('Verified commit and HTTPS URL required')
    if site_root and t.get('artifact_path'):
        p=site_root / t['artifact_path']
        if not p.is_file():raise OrchestrationError('Missing released article')
        if 'noindex' in p.read_text(encoding='utf-8').lower():raise OrchestrationError('Cannot mark a noindex article as indexable publication')
    t['status']='published';t['deployment_proof']={'commit':commit,'url':url,'recorded_at':stamp(),'live_http_check':'NOT_TESTED','note':'Set live_http_check to PASS only after real HTTP verification'}
    return t

def checkup(data:dict[str,Any],base_dir:pathlib.Path|None=None)->dict[str,Any]:
    issues=validate(data,base_dir)
    status_counts={s:sum(t['status']==s for t in data['tasks']) for s in sorted(VALID_STATES)}
    now=dt.datetime.now(dt.timezone.utc)
    for t in data['tasks']:
        lock=t.get('lock')
        if t['status']=='claimed' and lock and lock.get('claimed_at'):
            try:
                ts=dt.datetime.fromisoformat(lock['claimed_at'].replace('Z','+00:00'))
                if (now-ts).total_seconds()>6*3600:
                    issues.append({'severity':'WARNING','code':'STALE_LOCK','message':f"{t['id']}: lock >6h; do NOT auto-steal, escalate to CEO"})
            except ValueError:issues.append({'severity':'CRITICAL','code':'BAD_LOCK_TIME','message':f"{t['id']}: unparsable lock date"})
    selected=[]
    for role in ['QAD-01','OPS-01','EDT-01','SID-00','COM-01','ANA-01','AES-00']:
        t=next_task(data,role)
        if t:selected.append({'role':role,'task_id':t['id'],'status':t['status'],'priority':t['priority']})
    critical=[i for i in issues if i['severity']=='CRITICAL']
    return {'time_utc':stamp(),'engine':'AffiliateOS deterministic coordinator v1.0','safe':not critical,'metrics':{'task_count':len(data['tasks']),'by_status':status_counts,'critical_issues':len(critical),'warnings':len(issues)-len(critical)},'issues':issues,'next_routable_tasks':selected,'limitations':['This checkup does not invoke LLMs, prove agent execution, certify article facts or verify website visually.','Scheduled GitHub workflows generate artifacts; user-authorized role runs must still save handoffs.','Live HTTP and independent content QA remain separate evidence gates.']}

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',type=pathlib.Path,default=DEFAULT_STATE)
    p.add_argument('--events',type=pathlib.Path,default=DEFAULT_EVENTS)
    sub=p.add_subparsers(dest='cmd',required=True)
    c=sub.add_parser('checkup');c.add_argument('--out',type=pathlib.Path)
    n=sub.add_parser('next');n.add_argument('--role',choices=sorted(VALID_ROLES))
    cl=sub.add_parser('claim');cl.add_argument('--task',required=True);cl.add_argument('--role',required=True);cl.add_argument('--run-id',required=True)
    h=sub.add_parser('handoff');h.add_argument('--task',required=True);h.add_argument('--role',required=True);h.add_argument('--run-id',required=True);h.add_argument('--evidence',required=True);h.add_argument('--artifact',required=True);h.add_argument('--summary',required=True)
    q=sub.add_parser('review');q.add_argument('--task',required=True);q.add_argument('--run-id',required=True);q.add_argument('--decision',choices=['PASS','REWORK','REJECT'],required=True);q.add_argument('--evidence',required=True);q.add_argument('--reason',default='')
    rel=sub.add_parser('release');rel.add_argument('--task',required=True);rel.add_argument('--role',default='OPS-01');rel.add_argument('--commit',required=True);rel.add_argument('--url',required=True);rel.add_argument('--root',type=pathlib.Path)
    args=p.parse_args(argv)
    try:
        data=load_state(args.state)
        if args.cmd=='checkup':
            r=checkup(data,args.state.parent.parent.parent if args.state.resolve()==DEFAULT_STATE.resolve() else None)
            output=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
            if args.out:atomic_write(args.out,output)
            print(output,end='')
            return 0 if r['safe'] else 2
        if args.cmd=='next':
            res=next_task(data,args.role)
            print(json.dumps(res,ensure_ascii=False,indent=2) if res else 'NO_READY_TASK');return 0
        # role transitions require existing healthy state
        issues=validate(data)
        if any(x['severity']=='CRITICAL' for x in issues):raise OrchestrationError('Fix existing critical state issues first')
        if args.cmd=='claim':t=claim(data,args.task,args.role,args.run_id)
        elif args.cmd=='handoff':t=handoff(data,args.task,args.role,args.run_id,args.evidence,args.artifact,args.summary)
        elif args.cmd=='review':t=review(data,args.task,args.run_id,args.decision,args.evidence,args.reason)
        elif args.cmd=='release':t=release(data,args.task,args.role,args.commit,args.url,args.root)
        else:raise OrchestrationError('Unknown command')
        after=validate(data)
        if any(x['severity']=='CRITICAL' for x in after):raise OrchestrationError('Invalid state transition: '+str(after))
        save_state(data,args.state)
        event={'task_id':t['id'],'operation':args.cmd,'role':getattr(args,'role','QAD-01'),'run_id':getattr(args,'run_id',None),'status':t['status'],'revision':data['updated_at']}
        eid=log_event(event,args.events)
        print(json.dumps({'ok':True,'task_id':t['id'],'status':t['status'],'event_id':eid,'revision':data['updated_at']},ensure_ascii=False))
        return 0
    except (OrchestrationError,OSError,ValueError) as ex:
        print(json.dumps({'ok':False,'error':str(ex)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())