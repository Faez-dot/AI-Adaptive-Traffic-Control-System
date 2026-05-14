import streamlit as st
import random
import pandas as pd
from src.logic.a_star import a_star_decision

def run_performance_comparison(scenario, arrival_rate, comp_cycles):
    """
    Runs a side-by-side comparison between the A* Adaptive System and a 
    Traditional Fixed-Time signal controller.
    """
    st.markdown("---")
    st.header("🏆 Performance Comparison Results (Single Intersection)")
    st.write(f"Simulating **{comp_cycles} cycles** on a baseline single intersection to compare A* logic vs Fixed-Time.")
    
    with st.spinner("Running complex AI simulations..."):
        lanes = ["North", "South", "East", "West"]
        multiplier = 2.0 if scenario == "Rush Hour" else 0.8
        inflow_sequence = []
        for _ in range(comp_cycles):
            tick_arrivals = {}
            for l in lanes:
                if random.random() < (arrival_rate * multiplier / 10):
                    tick_arrivals[l] = random.randint(1, 4)
                else:
                    tick_arrivals[l] = 0
            inflow_sequence.append(tick_arrivals)

        # AI System Setup
        ai_cars = {l: 0 for l in lanes}
        ai_phase = "North"
        ai_phase_timer = 0
        ai_metrics = {"wait_time": 0, "cleared": 0, "max_congestion": 0, "switches": 0}
        ai_congestion_history = []

        # Fixed System Setup
        fixed_cars = {l: 0 for l in lanes}
        fixed_phase_idx = 0
        fixed_phase = lanes[fixed_phase_idx]
        fixed_phase_timer = 0
        FIXED_GREEN_TIME = 6
        fixed_metrics = {"wait_time": 0, "cleared": 0, "max_congestion": 0, "switches": 0}
        fixed_congestion_history = []

        for i in range(comp_cycles):
            arrivals = inflow_sequence[i]
            for l in lanes:
                ai_cars[l] += arrivals[l]
                fixed_cars[l] += arrivals[l]
                
            # Fixed Controller Logic
            if fixed_phase_timer >= FIXED_GREEN_TIME:
                fixed_phase_idx = (fixed_phase_idx + 1) % 4
                fixed_phase = lanes[fixed_phase_idx]
                fixed_phase_timer = 0
                fixed_metrics["switches"] += 1
            
            cleared_fixed = min(fixed_cars[fixed_phase], 3)
            fixed_cars[fixed_phase] -= cleared_fixed
            fixed_metrics["cleared"] += cleared_fixed
            fixed_phase_timer += 1
            
            current_fixed_congestion = sum(fixed_cars.values())
            fixed_metrics["wait_time"] += current_fixed_congestion
            fixed_metrics["max_congestion"] = max(fixed_metrics["max_congestion"], current_fixed_congestion)
            fixed_congestion_history.append(current_fixed_congestion)

            # AI Controller Logic (A*)
            new_phase, _, _ = a_star_decision(ai_cars, ai_phase, scenario, priority_lane=None)
            
            if ai_phase_timer < FIXED_GREEN_TIME: 
                cleared_ai = min(ai_cars[ai_phase], 3)
                ai_cars[ai_phase] -= cleared_ai
                ai_metrics["cleared"] += cleared_ai
                ai_phase_timer += 1
            else:
                if new_phase == ai_phase:
                    cleared_ai = min(ai_cars[new_phase], 3)
                    ai_cars[new_phase] -= cleared_ai
                    ai_metrics["cleared"] += cleared_ai
                    ai_phase_timer += 1
                else:
                    ai_phase = new_phase
                    ai_phase_timer = 0
                    ai_metrics["switches"] += 1
                    
            current_ai_congestion = sum(ai_cars.values())
            ai_metrics["wait_time"] += current_ai_congestion
            ai_metrics["max_congestion"] = max(ai_metrics["max_congestion"], current_ai_congestion)
            ai_congestion_history.append(current_ai_congestion)

        ai_metrics["avg_wait_time"] = ai_metrics["wait_time"] / comp_cycles
        fixed_metrics["avg_wait_time"] = fixed_metrics["wait_time"] / comp_cycles
        
    # UI Rendering of metrics
    render_metrics_ui(ai_metrics, fixed_metrics, ai_congestion_history, fixed_congestion_history)

def render_metrics_ui(ai_metrics, fixed_metrics, ai_history, fixed_history):
    st.subheader("📊 Key Metrics Comparison")
    
    def calc_improvement(ai_val, fixed_val, lower_is_better=True):
        if fixed_val == 0: return "0%"
        diff = fixed_val - ai_val if lower_is_better else ai_val - fixed_val
        percent = (diff / fixed_val) * 100
        return f"{percent:.1f}%"
    
    
    st.metric("Avg Waiting Cars", f"{ai_metrics['avg_wait_time']:.1f}")
    st.metric("Total Cars Cleared", ai_metrics['cleared'])
    st.metric("Max Congestion (Cars)", ai_metrics['max_congestion'])
    st.metric("Signal Switches", ai_metrics['switches'])
    

    st.subheader("📈 Congestion Over Time")
    chart_data = pd.DataFrame({
        "AI Adaptive System": ai_history,
        "Traditional Fixed-Time": fixed_history
    })
    st.line_chart(chart_data)
    
    st.subheader("🚗 Total Traffic Handled")
    bar_data = pd.DataFrame({
        "System": ["Traditional Fixed-Time", "AI Adaptive System"],
        "Cars Cleared": [fixed_metrics['cleared'], ai_metrics['cleared']]
    }).set_index("System")
    # i want to change bar chart color
    st.bar_chart(bar_data)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.subheader("📑 Raw Data Comparison")
        comp_df = pd.DataFrame({
            "Metric": ["Average Waiting Cars/Tick", "Total Cars Cleared", "Max Congestion Peak", "Signal Phase Switches"],
            "Fixed System": [f"{fixed_metrics['avg_wait_time']:.1f}", fixed_metrics['cleared'], fixed_metrics['max_congestion'], fixed_metrics['switches']],
            "AI System": [f"{ai_metrics['avg_wait_time']:.1f}", ai_metrics['cleared'], ai_metrics['max_congestion'], ai_metrics['switches']]
        })
        st.table(comp_df.set_index("Metric"))
