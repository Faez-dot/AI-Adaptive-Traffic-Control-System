import streamlit as st
import time
from src.config.styles import apply_styles
from src.logic.simulation import simulate_step
from src.ui.components import render_intersection
from src.analytics.comparison import run_performance_comparison

# 1. Page Config & CSS
apply_styles()

# 2. Sidebar & Global Controls
with st.sidebar:
    st.header("🎮 Controls")
    scenario = st.selectbox("Traffic Pattern", ["Normal", "Rush Hour", "Night"])
    arrival_rate = st.slider("Inflow Intensity", 0, 10, 5)
    
    st.markdown("---")
    st.header("🚑 Emergency Services")
    st.write("Route an emergency vehicle through the network.")
    emergency_trigger = None
    if st.button("Trigger Emergency (West to East)"): emergency_trigger = "West"
    if st.button("Trigger Emergency (East to West)"): emergency_trigger = "East"
    
    st.markdown("---")
    tick = st.button("🚀 NEXT SIGNAL CYCLE", use_container_width=True, type="primary")
    auto_run = st.checkbox("🏎️ Start Real-Time Simulation", value=True)
    
    st.markdown("---")
    st.header("📊 Performance Comparison")
    st.markdown("Compare AI vs Fixed-Time on a single intersection.")
    comp_cycles = st.slider("Simulation Cycles", 10, 200, 50)
    run_comp = st.button("Run Comparison 🚦", use_container_width=True)

# 3. Initialize Session State
def init_state():
    if 'cars_A' not in st.session_state:
        st.session_state.cars_A = {"North": 0, "South": 0, "East": 0, "West": 0}
    if 'cars_B' not in st.session_state:
        st.session_state.cars_B = {"North": 0, "South": 0, "East": 0, "West": 0}
    if 'phase_A' not in st.session_state:
        st.session_state.phase_A = "North"
    if 'phase_B' not in st.session_state:
        st.session_state.phase_B = "North"
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'action_A' not in st.session_state:
        st.session_state.action_A = "Steady"
    if 'action_B' not in st.session_state:
        st.session_state.action_B = "Steady"
    if 'timer_A' not in st.session_state:
        st.session_state.timer_A = 0
    if 'timer_B' not in st.session_state:
        st.session_state.timer_B = 0
    if 'emerg_A' not in st.session_state:
        st.session_state.emerg_A = None
    if 'emerg_B' not in st.session_state:
        st.session_state.emerg_B = None

init_state()

# 4. Handle Emergency Triggers
if emergency_trigger == "West":
    st.session_state.emerg_A = "West"
elif emergency_trigger == "East":
    st.session_state.emerg_B = "East"

# 5. Main Application Header
st.title("🚦 Multi-Agent Traffic System")
st.markdown("Intersection A (West) communicates with Intersection B (East) to optimize flow.")

# 6. Execute Simulation Step
if tick or auto_run:
    simulate_step(scenario, arrival_rate)

# 7. Render Visualizer
colA, colB = st.columns(2)
with colA:
    st.markdown(render_intersection("A", st.session_state.cars_A, st.session_state.phase_A, st.session_state.action_A, st.session_state.emerg_A), unsafe_allow_html=True)
    st.metric("Status Agent A", st.session_state.action_A, delta=f"Congestion: {sum(st.session_state.cars_A.values())}", delta_color="inverse")
with colB:
    st.markdown(render_intersection("B", st.session_state.cars_B, st.session_state.phase_B, st.session_state.action_B, st.session_state.emerg_B), unsafe_allow_html=True)
    st.metric("Status Agent B", st.session_state.action_B, delta=f"Congestion: {sum(st.session_state.cars_B.values())}", delta_color="inverse")

# 8. Cooperative Logs
st.markdown("---")
st.subheader("🤝 Multi-Agent Cooperative Decision Logs")
with st.expander("📝 View Real-time Agent Communication", expanded=True):
    for log in st.session_state.logs[:5]:
        if log['cong_A'] > 15 or log['cong_B'] > 15:
            st.warning(f"⚠️ High Congestion Detected (A: {log['cong_A']}, B: {log['cong_B']}) - Agents Cooperating")
        st.write(f"**[{log['time']}]**")
        st.write(f"- {log['msg_A']}")
        st.write(f"- {log['msg_B']}")
        st.markdown("---")

# 9. Performance Comparison
if run_comp:
    run_performance_comparison(scenario, arrival_rate, comp_cycles)

# 10. Auto-run Handling
if auto_run and not run_comp:
    time.sleep(1.0)
    st.rerun()
