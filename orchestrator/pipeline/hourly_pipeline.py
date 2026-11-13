#!/usr/bin/env python3
"""AffiliateOS hourly conveyor planner: read-only, deterministic, no LLM calls.

One hourly production lane and one independent QA lane; scheduling is external.
This tool never publishes, claims or reviews a task and never unlocks stale jobs.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
DEFAULT_STATE=ROOT/"state/tasks.json"
TIMEZONE=ZoneInfo("Europe/Bucharest")
PRIORITIES={"P0":0,"P1":1,"P2":2,"P3":3}
QA_REQUIRED_STATES={"awaiting_qa","qa_passed"}
PUBLISHABLE_STATUSES={"qa_passed"}
INDEXABLE_STATUSES={"published"}
MAX_QA_BATCH=3
MAX_RELEASE_BATCH=4
MAX_REWORK_BATCH=2
MAX_NEW_DRAFT_BATCH=2
QA_BACKLOG_SOFT_LIMIT=6

def to_datetime(value):
    if not isinstance(value,str) or not value.strip():
        return None
    try:
        t=datetime.fromisoformat(value.replace("Z","+00:00"))
        if t.tzinfo is None:
            return None
        return t.astimezone(timezone.utc)
    except ValueError:
        return None

def when_entered(task):
    h=task.get("handoff") or {}
    q=task.get("qa") or {}
    if task.get("status")=="qa_passed":
        return to_datetime(q.get("at") or q.get("date"))
    if task.get("status")=="awaiting_qa":
        return to_datetime(h.get("at"))
    if task.get("status")=="rework":
        return to_datetime(q.get("at"))
    return None

def sort_jobs(tasks):
    return sorted(tasks,key=lambda x:(PRIORITIES.get(x.get("priority"),9),
        when_entered(x) or datetime.max.replace(tzinfo=timezone.utc),x.get("id","")))

def dependency_finished(task, index):
    return all(index.get(dep,{}).get("status") in {"published","completed"}
               for dep in task.get("depends_on",[]))

def audit_state(state, root=REPO, now=None):
    now=now or datetime.now(timezone.utc)
    issues=[]
    tasks=state.get("tasks",[])
    if not isinstance(tasks,list):
        return [{"severity":"CRITICAL","code":"BAD_TASKS","task_id":None,"detail":"tasks must be an array"}]
    ids=[t.get("id") for t in tasks]
    if len(set(ids))!=len(ids):
        issues.append({"severity":"CRITICAL","code":"DUPLICATE_ID","task_id":None,"detail":"Duplicate task IDs"})
    artifacts={}
    for t in tasks:
        tid=t.get("id")
        status=t.get("status")
        path=t.get("artifact_path")
        if path and str(path).startswith("articles/") and status in {"awaiting_qa","qa_passed","published"}:
            if path in artifacts and artifacts[path]!=tid:
                issues.append({"severity":"CRITICAL","code":"DUPLICATE_ARTICLE","task_id":tid,"detail":f"{path} also belongs to {artifacts[path]}"})
            artifacts[path]=tid
            article=root/path
            if not article.is_file():
                issues.append({"severity":"CRITICAL","code":"MISSING_ARTIFACT","task_id":tid,"detail":path})
            else:
                s=article.read_text(encoding="utf-8")
                # Only the META robots, not prose mentioning noindex.
                match=re.search(r'<meta\b[^>]*\bname=["\']robots["\'][^>]*>',s,re.I)
                robots=match.group() if match else ""
                blocked=bool(re.search(r'\bnoindex\b',robots,re.I))
                if status in QA_REQUIRED_STATES and not blocked:
                    issues.append({"severity":"CRITICAL","code":"EARLY_INDEXATION","task_id":tid,"detail":f"{path} cannot be indexable in {status}"})
                if status=="published" and blocked:
                    issues.append({"severity":"CRITICAL","code":"PUBLISHED_NOINDEX","task_id":tid,"detail":path})
        if status=="qa_passed":
            qa=t.get("qa") or {}
            if not (qa.get("decision")=="PASS" and qa.get("reviewer_role")=="QAD-01"
                    and qa.get("evidence") and qa.get("reviewer_run_id")!=t.get("producer_run_id")):
                issues.append({"severity":"CRITICAL","code":"UNVERIFIED_PASS","task_id":tid,"detail":"QA PASS must be separately evidenced"})
        if status=="awaiting_qa" and t.get("owner")!="QAD-01":
            issues.append({"severity":"CRITICAL","code":"QA_WRONG_OWNER","task_id":tid,"detail":"Awaiting QAD owner required"})
        if status=="claimed":
            lock=t.get("lock") or {}
            held=to_datetime(lock.get("claimed_at"))
            if held is None:
                issues.append({"severity":"WARNING","code":"CLAIM_TIME_UNKNOWN","task_id":tid,"detail":"Cannot infer claim age"})
            elif now-held>timedelta(minutes=90):
                issues.append({"severity":"WARNING","code":"STALE_CLAIM","task_id":tid,"detail":"Claim >90min; do not steal, route human/CEO triage"})
        if status=="awaiting_qa":
            entered=when_entered(t)
            if entered and now-entered>timedelta(hours=2):
                issues.append({"severity":"WARNING","code":"QA_WAIT_OVER_2H","task_id":tid,"detail":"Review queue aging >2h"})
        if status=="qa_passed":
            entered=when_entered(t)
            if entered and now-entered>timedelta(hours=2):
                issues.append({"severity":"WARNING","code":"RELEASE_WAIT_OVER_2H","task_id":tid,"detail":"Passed article awaiting OPS >2h"})
    return issues

def build_plan(state, root=REPO, now=None):
    now=now or datetime.now(timezone.utc)
    index={t["id"]:t for t in state["tasks"]}
    qa=sort_jobs([t for t in state["tasks"] if t.get("status")=="awaiting_qa" and t.get("owner")=="QAD-01"])
    release=sort_jobs([t for t in state["tasks"] if t.get("status")=="qa_passed" and t.get("owner")=="OPS-01"])
    rework=sort_jobs([t for t in state["tasks"] if t.get("status")=="rework" and t.get("owner")=="EDT-01" and dependency_finished(t,index)])
    drafts=sort_jobs([t for t in state["tasks"] if t.get("status")=="ready" and t.get("owner")=="EDT-01" and dependency_finished(t,index)])
    safety=audit_state(state,root,now)
    critical=[v for v in safety if v["severity"]=="CRITICAL"]
    return {
        "generated_at":now.isoformat(),
        "timezone":"Europe/Bucharest",
        "cadence":"production :00 every hour; independent QAD :30 every hour (subject to scheduler and actual task completion)",
        "safety_gate":"STOP mutations until critical conditions resolved" if critical else "No critical local state/indexation defects detected",
        "safe":not bool(critical),
        "queues":{"qa":len(qa),"approved_for_ops":len(release),"rework":len(rework),"ready_editorial":len(drafts)},
        "production":{
            "step_1_release_passed":[t["id"] for t in release[:MAX_RELEASE_BATCH]],
            "step_2_fix_qa_rework":[t["id"] for t in rework[:MAX_REWORK_BATCH]],
            "step_3_new_editorial":[t["id"] for t in drafts[:MAX_NEW_DRAFT_BATCH]] if len(qa)<QA_BACKLOG_SOFT_LIMIT else [],
            "new_editorial_paused_for_backpressure":len(qa)>=QA_BACKLOG_SOFT_LIMIT,
            "notes":"Release only independently PASSed, unchanged reviewed source; prove CI, deploy, sitemap, live URL. Reworks precede new articles. Observe max FIVE new distinct drafts per Bucharest calendar day across all hourly runs."
        },
        "independent_qa":{
            "review_next":[t["id"] for t in qa[:MAX_QA_BATCH]],
            "notes":"Each article needs separate source/visual/affiliate/factual judgment, real review artifact + distinct QAD run and commit. Reviewer never edits production files or deploys."
        },
        "alerts":safety,
        "limitations":[
            "Read-only planner: no LLM agents started, no autonomous publishing or SEO indexation claimed.",
            "Browser smoke/CI are technical tests, not independent factual or visual review.",
            "Unlogged review wait timestamps cannot be estimated reliably; UNKNOWN rather than invented lag.",
            "Schedulers can delay or skip actual start; verify run history and GitHub deploy by evidence."
        ]
    }

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state",type=Path,default=DEFAULT_STATE)
    parser.add_argument("--root",type=Path,default=REPO)
    parser.add_argument("--out",type=Path)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args(argv)
    try:
        data=json.loads(args.state.read_text(encoding="utf-8"))
        report=build_plan(data,args.root)
        rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(rendered,encoding="utf-8")
        else:print(rendered,end="")
        return 2 if args.check and not report["safe"] else 0
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as exc:
        print(f"Pipeline planner failure: {exc}",file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
