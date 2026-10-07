
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Job Scheduling Simulator", page_icon="⚙️", layout="wide")

st.title("⚙️ Job Scheduling Simulator")
st.caption("Single-machine, non-preemptive scheduling • FCFS • SPT • EDD • Priority")

DEFAULT = pd.DataFrame({
    "Job": ["A","B","C","D"],
    "Arrival": [0.00, 0.25, 0.50, 0.75],
    "Processing": [4.00, 2.00, 6.00, 1.00],
    "Due": [7.00, 4.00, 9.00, 6.00],
    "Priority": [3,1,4,2],
})

with st.sidebar:
    st.header("Controls")
    st.write("Enter times in decimal hours. Example: 9:30 AM = 9.5.")
    selected_rules = st.multiselect(
        "Rules to compare",
        ["FCFS","SPT","EDD","Priority"],
        default=["FCFS","SPT","EDD","Priority"]
    )
    st.info("Priority convention: 1 = highest priority.")

st.subheader("1. Enter job data")
edited = st.data_editor(
    DEFAULT,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Job": st.column_config.TextColumn("Job", required=True),
        "Arrival": st.column_config.NumberColumn("Arrival (hr)", min_value=0.0, step=0.25),
        "Processing": st.column_config.NumberColumn("Processing (hr)", min_value=0.01, step=0.25),
        "Due": st.column_config.NumberColumn("Due (hr)", min_value=0.0, step=0.25),
        "Priority": st.column_config.NumberColumn("Priority (1=High)", min_value=1, step=1),
    },
    hide_index=True,
)

def schedule_jobs(df, rule):
    d = df.copy()
    if d.empty:
        return d

    # Remove incomplete rows
    d = d.dropna(subset=["Job","Arrival","Processing","Due","Priority"]).copy()
    d["Job"] = d["Job"].astype(str)

    if rule == "FCFS":
        d = d.sort_values(["Arrival","Job"], kind="stable")
    elif rule == "SPT":
        d = d.sort_values(["Processing","Arrival","Job"], kind="stable")
    elif rule == "EDD":
        d = d.sort_values(["Due","Arrival","Job"], kind="stable")
    elif rule == "Priority":
        d = d.sort_values(["Priority","Arrival","Job"], kind="stable")

    current = 0.0
    rows = []
    for seq, (_, r) in enumerate(d.iterrows(), start=1):
        start = max(current, float(r["Arrival"]))
        completion = start + float(r["Processing"])
        waiting = start - float(r["Arrival"])
        flow = completion - float(r["Arrival"])
        lateness = completion - float(r["Due"])
        tardiness = max(0.0, lateness)
        earliness = max(0.0, -lateness)
        on_time = int(completion <= float(r["Due"]))
        rows.append({
            "Sequence": seq,
            "Job": r["Job"],
            "Arrival": float(r["Arrival"]),
            "Processing": float(r["Processing"]),
            "Due": float(r["Due"]),
            "Priority": int(r["Priority"]),
            "Start": start,
            "Completion": completion,
            "Waiting": waiting,
            "Flow Time": flow,
            "Lateness": lateness,
            "Delay / Tardiness": tardiness,
            "On-Time": "Yes" if on_time else "No",
            "Earliness": earliness,
        })
        current = completion

    out = pd.DataFrame(rows)
    first_arrival = out["Arrival"].min()
    makespan = out["Completion"].max() - first_arrival
    total_processing = out["Processing"].sum()
    utilisation = total_processing / makespan if makespan > 0 else 0
    metrics = {
        "Average Waiting": out["Waiting"].mean(),
        "Average Flow Time": out["Flow Time"].mean(),
        "Average Delay": out["Delay / Tardiness"].mean(),
        "Maximum Delay": out["Delay / Tardiness"].max(),
        "On-Time %": out["On-Time"].eq("Yes").mean(),
        "Utilisation": utilisation,
        "Makespan": makespan,
        "Total Processing": total_processing,
        "Late Jobs": (out["On-Time"] == "No").sum(),
    }
    return out, metrics

if not selected_rules:
    st.warning("Select at least one scheduling rule.")
    st.stop()

results = {}
for rule in selected_rules:
    results[rule] = schedule_jobs(edited, rule)

st.subheader("2. Dashboard comparison")
metric_rows = []
for rule, (table, m) in results.items():
    metric_rows.append({
        "Rule": rule,
        "Avg Waiting": m["Average Waiting"],
        "Avg Flow Time": m["Average Flow Time"],
        "Avg Delay": m["Average Delay"],
        "Max Delay": m["Maximum Delay"],
        "On-Time %": m["On-Time %"],
        "Utilisation": m["Utilisation"],
        "Makespan": m["Makespan"],
        "Late Jobs": m["Late Jobs"],
    })
comparison = pd.DataFrame(metric_rows)

c1,c2,c3,c4 = st.columns(4)
best_wait = comparison.loc[comparison["Avg Waiting"].idxmin(), "Rule"]
best_delay = comparison.loc[comparison["Avg Delay"].idxmin(), "Rule"]
best_ontime = comparison.loc[comparison["On-Time %"].idxmax(), "Rule"]
best_util = comparison.loc[comparison["Utilisation"].idxmax(), "Rule"]
c1.metric("Lowest Avg Waiting", best_wait)
c2.metric("Lowest Avg Delay", best_delay)
c3.metric("Best On-Time %", best_ontime)
c4.metric("Highest Utilisation", best_util)

display_comp = comparison.copy()
for col in ["Avg Waiting","Avg Flow Time","Avg Delay","Max Delay","Makespan"]:
    display_comp[col] = display_comp[col].round(2)
for col in ["On-Time %","Utilisation"]:
    display_comp[col] = (display_comp[col]*100).round(1).astype(str) + "%"
st.dataframe(display_comp, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    fig = px.bar(comparison, x="Rule", y="Avg Waiting", title="Average Waiting Time")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.bar(comparison, x="Rule", y="Avg Delay", title="Average Delay / Tardiness")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig = px.bar(comparison, x="Rule", y="On-Time %", title="On-Time Performance")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.bar(comparison, x="Rule", y="Utilisation", title="Machine Utilisation")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("3. Detailed schedules")
tabs = st.tabs(selected_rules)
for tab, rule in zip(tabs, selected_rules):
    with tab:
        table, metrics = results[rule]
        st.markdown(f"### {rule} schedule")
        st.dataframe(table.round(2), use_container_width=True, hide_index=True)

        # Gantt-style timeline
        gantt = table.copy()
        gantt["Duration"] = gantt["Processing"]
        fig = px.bar(
            gantt,
            x="Duration",
            y="Job",
            base="Start",
            orientation="h",
            text="Job",
            title=f"{rule} — Machine Timeline"
        )
        fig.update_layout(showlegend=False, xaxis_title="Time (hours)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("4. Managerial interpretation")
st.write(
    "Use the dashboard to discuss trade-offs rather than declaring one rule universally best. "
    "SPT is typically useful for reducing waiting/flow time; EDD focuses on due-date performance; "
    "Priority moves urgent jobs earlier; FCFS is simple and transparent."
)

# Download current comparison
csv = comparison.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download comparison CSV",
    data=csv,
    file_name="job_scheduling_comparison.csv",
    mime="text/csv"
)
