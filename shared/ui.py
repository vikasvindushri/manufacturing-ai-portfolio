import streamlit as st
CSS="""
<style>
.block-container{padding-top:1.4rem;max-width:1250px}.hero{padding:1.7rem 2rem;border-radius:22px;background:linear-gradient(120deg,#062F3A,#087F8C);color:white;box-shadow:0 14px 35px #062f3a25;margin-bottom:1.2rem}.hero h1{margin:0;font-size:2.25rem}.hero p{opacity:.9;margin:.5rem 0 0}.card{background:white;border:1px solid #dbe5eb;border-radius:16px;padding:1rem 1.2rem;box-shadow:0 7px 20px #2030400d}.badge{display:inline-block;padding:.25rem .55rem;border-radius:999px;background:#dff6f4;color:#006c70;font-weight:700;font-size:.78rem}.risk{border-left:5px solid #f5a623;background:#fff8e8;padding:.8rem 1rem;border-radius:10px}.stButton>button{border-radius:10px;font-weight:700}.stDownloadButton>button{border-radius:10px}
</style>"""
def page(title,subtitle,icon="AI"):
 st.markdown(CSS,unsafe_allow_html=True)
 st.markdown(f'<div class="hero"><span class="badge">{icon}</span><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)
def governance_note(text="AI output is decision support. A qualified person must verify evidence and approve actions."):
 st.markdown(f'<div class="risk"><b>Human-in-the-loop control</b><br>{text}</div>',unsafe_allow_html=True)
def metric_row(items):
 cols=st.columns(len(items))
 for c,(label,value,delta) in zip(cols,items): c.metric(label,value,delta)
