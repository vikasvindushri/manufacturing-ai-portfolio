import streamlit as st

def source_banner(record):
    p=record.get("provenance",{});notice=p.get("user_notice","Result source unavailable.")
    if p.get("gemini_used"):st.success("AI enhancement completed");st.write(notice)
    elif p.get("gemini_status")=="failed":st.warning("Optional AI enhancement unavailable");st.write(notice);st.caption("The local result remains available for review and export.")
    else:st.info("Local analysis");st.write(notice)

def readiness_panel(info,title="Record readiness"):
    st.subheader(title);st.progress(info["score"]/100);a,b,c=st.columns(3)
    a.metric("Readiness",f"{info['score']}%");b.metric("Completed",f"{info['complete_count']}/{info['total_count']}");c.metric("Level",info["label"])
    x,y=st.columns(2)
    with x:
        st.markdown("**Available information**")
        for q in info["completed"]:st.write(f"✓ {q}")
    with y:
        st.markdown("**Information still needed**")
        if info["missing"]:
            for q in info["missing"]:st.write(f"! {q}")
        else:st.write("✓ No required intake items are missing.")

def analysis_sections(facts,gaps,hypotheses,recommendations):
    tabs=st.tabs(["Verified inputs","Evidence gaps","Hypotheses","Recommendations"])
    with tabs[0]:
        st.success("Information entered by the user or obtained from local evidence.")
        for x in facts:st.write(f"• {x}")
    with tabs[1]:
        if gaps:
            st.warning("Additional information is required before confirming conclusions.")
            for x in gaps:st.write(f"• {x}")
        else:st.success("No required intake gaps were detected.")
    with tabs[2]:
        st.info("Investigation hypotheses — not confirmed causes.")
        for x in hypotheses:st.write(f"• {x}")
    with tabs[3]:
        st.caption("Recommendations require qualified human review.")
        for x in recommendations:st.write(f"• {x}")

def report_header(title,record_id,status,owner,source,version="0.4"):
    st.markdown(f"### {title}");a,b,c,d=st.columns(4)
    a.metric("Record",record_id or "Not assigned");b.metric("Status",status);c.metric("Owner",owner or "Not assigned");d.metric("Version",version)
    st.caption(f"Analysis source: {source}")
