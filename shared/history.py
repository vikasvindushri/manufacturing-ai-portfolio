from datetime import datetime,timezone
def add_history(state,product,record,limit=25):
    history=state.setdefault("history",[])
    history.insert(0,{"timestamp_utc":datetime.now(timezone.utc).isoformat(),"product":product,"record":record})
    del history[limit:]
    return history
def drafts(state): return state.setdefault("drafts",{})
def save_draft(state,key,payload): drafts(state)[key]=payload; return payload
def load_draft(state,key): return drafts(state).get(key)
