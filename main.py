import streamlit as st
import random
import time
from traffic_ai import a_star_decision

# GUI Design & Aesthetic Configuration
st.set_page_config(page_title="AI Adaptive Traffic Control", layout="wide", page_icon="🚦")

# Custom CSS for Premium Aesthetics & Intersection Layout
st.markdown("""
<style>
/* Main Background Hook */
.stApp { background-color: #0d1117; color: #f8fafc; }

/* Intersection Container */
.intersection-container {
    display: grid;
    grid-template-columns: 220px 220px 220px;
    grid-template-rows: 220px 220px 220px;
    gap: 0px;
    justify-content: center;
    align-items: center;
    margin: 20px auto;
    background-color: #2e7d32; /* Grass background */
    padding: 60px;
    border-radius: 12px;
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
    position: relative;
}

/* Road Segments */
.road { background-color: #4b5563; position: relative; display: flex; align-items: center; justify-content: center; overflow: visible; }
.road-v { grid-column: 2; height: 100%; width: 100%; }
.road-h { grid-row: 2; width: 100%; height: 100%; }

/* Center Intersection Square */
.center-box { grid-column: 2; grid-row: 2; background-color: #312e81; z-index: 5; border: none; position: relative; }

/* Road Markings */
.road-v::after { content: ''; position: absolute; left: 50%; height: 100%; width: 6px; border-left: 2px solid #fbbf24; border-right: 2px solid #fbbf24; transform: translateX(-50%); }
.road-h::after { content: ''; position: absolute; top: 50%; width: 100%; height: 6px; border-top: 2px solid #fbbf24; border-bottom: 2px solid #fbbf24; transform: translateY(-50%); }

/* Crosswalks (Zebra Stripes) */
.crosswalk-v { position: absolute; width: 100%; height: 20px; background: repeating-linear-gradient(90deg, #fff, #fff 15px, transparent 15px, transparent 30px); z-index: 6; }
.crosswalk-h { position: absolute; height: 100%; width: 20px; background: repeating-linear-gradient(0deg, #fff, #fff 15px, transparent 15px, transparent 30px); z-index: 6; }

.cw-north { bottom: 0; }
.cw-south { top: 0; }
.cw-west { right: 0; }
.cw-east { left: 0; }

/* Traffic Light Styling */
.light-post {
    width: 24px; height: 65px; background: #111; border-radius: 4px; 
    display: flex; flex-direction: column; align-items: center; justify-content: space-evenly;
    padding: 4px; position: absolute; z-index: 10; border: 1px solid #333;
}
.bulb { width: 14px; height: 14px; border-radius: 50%; background: #222; }

/* Active Light Colors */
.red-active { background: #ff3b30; box-shadow: 0 0 12px #ff3b30; }
.yellow-active { background: #ffcc00; box-shadow: 0 0 12px #ffcc00; }
.green-active { background: #4cd964; box-shadow: 0 0 12px #4cd964; }

.light-north { bottom: 10px; right: -35px; }
.light-south { top: 10px; left: -35px; }
.light-east { left: 10px; bottom: -35px; transform: rotate(90deg); }
.light-west { right: 10px; top: -35px; transform: rotate(90deg); }

/* Vehicle Counter Label */
.car-label {
    position: absolute; background: white; color: black; font-weight: 900;
    padding: 2px 8px; border-radius: 3px; font-size: 16px; z-index: 20;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3); border: 1px solid #ccc;
}

.label-n { top: 20px; left: 20px; }
.label-s { bottom: 20px; right: 20px; }
.label-e { top: 20px; right: 20px; }
.label-w { bottom: 20px; left: 20px; }

/* Direction Labels */
.road-name {
    position: absolute; color: rgba(255,255,255,0.25); font-size: 18px; font-weight: 900; 
    letter-spacing: 3px; text-transform: uppercase; pointer-events: none; z-index: 1; font-family: sans-serif;
}

/* Ambulance Flashing Light Effect */
@keyframes siren {
    0% { filter: drop-shadow(0 0 5px red); }
    50% { filter: drop-shadow(0 0 15px red); transform: scale(1.1); }
    100% { filter: drop-shadow(0 0 5px red); }
}
.siren-active {
    animation: siren 0.4s infinite;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# 1. Title
st.title("🚦 AI Adaptive Traffic Simulation")

# 2. Sidebar
with st.sidebar:
    st.header("🎮 Controls")
    scenario = st.selectbox("Traffic Pattern", ["Normal", "Rush Hour", "Night"])
    arrival_rate = st.slider("Inflow Intensity", 0, 10, 5)
    
    st.markdown("---")
    st.header("🚑 Emergency Services")
    emergency_lane = None
    if st.button("Trigger Emergency (North)"): emergency_lane = "North"
    if st.button("Trigger Emergency (South)"): emergency_lane = "South"
    if st.button("Trigger Emergency (East)"): emergency_lane = "East"
    if st.button("Trigger Emergency (West)"): emergency_lane = "West"
    
    st.markdown("---")
    tick = st.button("🚀 NEXT SIGNAL CYCLE", use_container_width=True, type="primary")
    auto_run = st.checkbox("🏎️ Start Real-Time Simulation", value=True)

# 3. Initialize State
if 'cars' not in st.session_state:
    st.session_state.cars = {"North": 0, "South": 0, "East": 0, "West": 0}
if 'phase' not in st.session_state:
    st.session_state.phase = "North"
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'last_action' not in st.session_state:
    st.session_state.last_action = "Steady"
if 'phase_timer' not in st.session_state:
    st.session_state.phase_timer = 0

# 4. Simulation Step
def simulate_step(emergency):
    MIN_GREEN_TIME = 6 # Ticks before a light is ALLOWED to switch
    
    # Inflow logic
    multiplier = 2.0 if scenario == "Rush Hour" else 0.8
    for lane in st.session_state.cars:
        if random.random() < (arrival_rate * multiplier / 10):
            st.session_state.cars[lane] += random.randint(1, 4)

    # A* Decision
    start_time = time.perf_counter()
    new_phase, cost, all_costs = a_star_decision(st.session_state.cars, st.session_state.phase, scenario, emergency)
    decision_time = (time.perf_counter() - start_time) * 1000

    # PERFECT SIGNAL CONCEPTS:
    # 1. Emergency Preemption (Instant override)
    if emergency:
        st.session_state.phase = emergency
        st.session_state.last_action = "Emergency Preemption"
        st.session_state.phase_timer = 0
        cleared = min(st.session_state.cars[emergency], 3)
        st.session_state.cars[emergency] -= cleared
    
    # 2. Minimum Green Time (Stability)
    elif st.session_state.phase_timer < MIN_GREEN_TIME:
        # Prevent switching even if A* suggests it (to avoid rapid flickering)
        st.session_state.last_action = "Stable Green"
        cleared = min(st.session_state.cars[st.session_state.phase], 3)
        st.session_state.cars[st.session_state.phase] -= cleared
        st.session_state.phase_timer += 1
    
    # 3. Adaptive AI Decision (After Min Green)
    else:
        if new_phase == st.session_state.phase:
            st.session_state.last_action = "Clearing"
            cleared = min(st.session_state.cars[new_phase], 3)
            st.session_state.cars[new_phase] -= cleared
            st.session_state.phase_timer += 1
        else:
            # AI Decided to switch - Reset timer for new phase
            st.session_state.last_action = "Switching" 
            st.session_state.phase = new_phase
            st.session_state.phase_timer = 0

    log_entry = {
        "time": time.strftime('%H:%M:%S'), 
        "phase": st.session_state.phase, 
        "cost": cost, 
        "all_choices": all_costs,
        "latency": decision_time
    }
    st.session_state.logs.insert(0, log_entry)

if tick or auto_run:
    simulate_step(emergency_lane)

# 5. Render Visualizer (MINIFIED/FLUSH)
def get_light_html(lane_name, active_phase, action):
    is_active = (lane_name == active_phase)
    is_switching = (action == "Switching")
    red = "red-active" if not is_active else "bulb"
    yellow = "yellow-active" if is_active and is_switching else "bulb"
    green = "green-active" if is_active and not is_switching else "bulb"
    return f'<div class="light-post light-{lane_name.lower()}"><div class="bulb {red}"></div><div class="bulb {yellow}"></div><div class="bulb {green}"></div></div>'

def draw_v(count, is_emergency):
    res = ""
    if is_emergency:
        res += '<span class="siren-active" style="font-size: 45px;">🚑</span>'
    if count > 0:
        res += "🚗" * min(count, 3)
    return res

st.markdown(f"""
<div class="intersection-container">
<!-- North Lane -->
<div class="road road-v" style="grid-row: 1; grid-column: 2;">
<div class="road-name" style="top: 20px; right: 20px;">NORTH</div>
<div class="car-label label-n">{st.session_state.cars['North']}</div>
<div style="position:absolute; bottom:60px; font-size:35px;">{draw_v(st.session_state.cars['North'], emergency_lane == 'North')}</div>
{get_light_html('North', st.session_state.phase, st.session_state.last_action)}
<div class="crosswalk-v cw-north"></div>
</div>
<!-- West Lane -->
<div class="road road-h" style="grid-row: 2; grid-column: 1;">
<div class="road-name" style="top: 20px; left: 20px;">WEST</div>
<div class="car-label label-w">{st.session_state.cars['West']}</div>
<div style="position:absolute; right:60px; font-size:35px;">{draw_v(st.session_state.cars['West'], emergency_lane == 'West')}</div>
{get_light_html('West', st.session_state.phase, st.session_state.last_action)}
<div class="crosswalk-h cw-west"></div>
</div>
<!-- Center -->
<div class="center-box"></div>
<!-- East Lane -->
<div class="road road-h" style="grid-row: 2; grid-column: 3;">
<div class="road-name" style="bottom: 20px; right: 20px;">EAST</div>
<div class="car-label label-e">{st.session_state.cars['East']}</div>
<div style="position:absolute; left:60px; font-size:35px;">{draw_v(st.session_state.cars['East'], emergency_lane == 'East')}</div>
{get_light_html('East', st.session_state.phase, st.session_state.last_action)}
<div class="crosswalk-h cw-east"></div>
</div>
<!-- South Lane -->
<div class="road road-v" style="grid-row: 3; grid-column: 2;">
<div class="road-name" style="bottom: 20px; left: 20px;">SOUTH</div>
<div class="car-label label-s">{st.session_state.cars['South']}</div>
<div style="position:absolute; top:60px; font-size:35px;">{draw_v(st.session_state.cars['South'], emergency_lane == 'South')}</div>
{get_light_html('South', st.session_state.phase, st.session_state.last_action)}
<div class="crosswalk-v cw-south"></div>
</div>
</div>
""", unsafe_allow_html=True)

# 6. Metrics & Logs
col1, col2, col3 = st.columns(3)
col1.metric("Status", st.session_state.last_action)
col2.metric("Phase Timer", f"{st.session_state.phase_timer}s")
if st.session_state.logs:
    col3.metric("A* Cost", f"{st.session_state.logs[0]['cost']:.0f}")

st.markdown("---")
with st.expander("📝 View AI Decision Logs", expanded=True):
    for log in st.session_state.logs[:5]:
        c = log['all_choices']
        st.write(f"[{log['time']}] -> Decision: **{log['phase']} Green**")
        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;**Costs:** North: `{c['North']:.0f}` | South: `{c['South']:.0f}` | East: `{c['East']:.0f}` | West: `{c['West']:.0f}`")
        st.markdown("---")

if auto_run:
    time.sleep(1.0)
    st.rerun()
