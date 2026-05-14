import streamlit as st
import random
import time
from src.logic.a_star import a_star_decision

def map_label(agent, phase):
    if agent == "A":
        labels = {"North": "NORTH-WEST", "South": "SOUTH-WEST", "West": "FAR-WEST", "East": "CENTRAL"}
    else:
        labels = {"North": "NORTH-EAST", "South": "SOUTH-EAST", "West": "CENTRAL", "East": "FAR-EAST"}
    return labels.get(phase, phase)

def simulate_step(scenario, arrival_rate, amb_freq=5):
    """
    Executes one cycle of the traffic simulation, updating vehicle counts 
    and signal phases for both intersections.
    """
    MIN_GREEN_TIME = 6
    
    # Calculate initial congestions
    congestion_A = sum(st.session_state.cars_A.values())
    congestion_B = sum(st.session_state.cars_B.values())

    # Inflow logic (external sources)
    multiplier = 2.0 if scenario == "Rush Hour" else 0.8
    prob = arrival_rate * multiplier / 10

    # Random Ambulance Spawning
    if random.random() < (amb_freq / 100):
        lane = random.choice(["North", "South", "East", "West"])
        # Only spawn if no emergency currently active to avoid overriding
        if not st.session_state.emerg_A:
            st.session_state.emerg_A = lane
            st.session_state.cars_A[lane] += 1 # Ensure at least one vehicle
        if not st.session_state.emerg_B:
            st.session_state.emerg_B = lane
            st.session_state.cars_B[lane] += 1
    
    # External inflow to A (North, South, West)
    for l in ["North", "South", "West"]:
        if random.random() < prob:
            st.session_state.cars_A[l] += random.randint(1, 4)
            
    # External inflow to B (North, South, East)
    for l in ["North", "South", "East"]:
        if random.random() < prob:
            st.session_state.cars_B[l] += random.randint(1, 4)

    # Agent A Decision
    new_phase_A, cost_A, all_costs_A = a_star_decision(
        st.session_state.cars_A, st.session_state.phase_A, scenario, 
        priority_lane=st.session_state.emerg_A, 
        neighbor_congestion=congestion_B, neighbor_direction="West"
    )

    # Agent B Decision
    new_phase_B, cost_B, all_costs_B = a_star_decision(
        st.session_state.cars_B, st.session_state.phase_B, scenario, 
        priority_lane=st.session_state.emerg_B, 
        neighbor_congestion=congestion_A, neighbor_direction="East"
    )

    cleared_A = 0
    cleared_B = 0
    cleared_lane_A = None
    cleared_lane_B = None

    # Apply Logic for A
    if st.session_state.emerg_A:
        st.session_state.phase_A = st.session_state.emerg_A
        st.session_state.action_A = "Emergency Preemption"
        st.session_state.timer_A = 0
        cleared_A = min(st.session_state.cars_A[st.session_state.emerg_A], 3)
        st.session_state.cars_A[st.session_state.emerg_A] -= cleared_A
        cleared_lane_A = st.session_state.emerg_A
        if st.session_state.cars_A[st.session_state.emerg_A] == 0:
            st.session_state.emerg_A = None
            if cleared_lane_A == "West":
                st.session_state.emerg_B = "West"
    elif st.session_state.timer_A < MIN_GREEN_TIME:
        st.session_state.action_A = "Stable Green"
        cleared_A = min(st.session_state.cars_A[st.session_state.phase_A], 3)
        st.session_state.cars_A[st.session_state.phase_A] -= cleared_A
        cleared_lane_A = st.session_state.phase_A
        st.session_state.timer_A += 1
    else:
        if new_phase_A == st.session_state.phase_A:
            st.session_state.action_A = "Clearing"
            cleared_A = min(st.session_state.cars_A[new_phase_A], 3)
            st.session_state.cars_A[new_phase_A] -= cleared_A
            cleared_lane_A = new_phase_A
            st.session_state.timer_A += 1
        else:
            st.session_state.action_A = "Switching" 
            st.session_state.phase_A = new_phase_A
            st.session_state.timer_A = 0

    # Apply Logic for B
    if st.session_state.emerg_B:
        st.session_state.phase_B = st.session_state.emerg_B
        st.session_state.action_B = "Emergency Preemption"
        st.session_state.timer_B = 0
        cleared_B = min(st.session_state.cars_B[st.session_state.emerg_B], 3)
        st.session_state.cars_B[st.session_state.emerg_B] -= cleared_B
        cleared_lane_B = st.session_state.emerg_B
        if st.session_state.cars_B[st.session_state.emerg_B] == 0:
            st.session_state.emerg_B = None
            if cleared_lane_B == "East":
                st.session_state.emerg_A = "East"
    elif st.session_state.timer_B < MIN_GREEN_TIME:
        st.session_state.action_B = "Stable Green"
        cleared_B = min(st.session_state.cars_B[st.session_state.phase_B], 3)
        st.session_state.cars_B[st.session_state.phase_B] -= cleared_B
        cleared_lane_B = st.session_state.phase_B
        st.session_state.timer_B += 1
    else:
        if new_phase_B == st.session_state.phase_B:
            st.session_state.action_B = "Clearing"
            cleared_B = min(st.session_state.cars_B[new_phase_B], 3)
            st.session_state.cars_B[new_phase_B] -= cleared_B
            cleared_lane_B = new_phase_B
            st.session_state.timer_B += 1
        else:
            st.session_state.action_B = "Switching" 
            st.session_state.phase_B = new_phase_B
            st.session_state.timer_B = 0

    # Traffic Flow between agents
    if cleared_lane_A == "West":
        st.session_state.cars_B["West"] += cleared_A
    if cleared_lane_B == "East":
        st.session_state.cars_A["East"] += cleared_B

    # Logging
    log_msg_A = f"A prioritized {map_label('A', st.session_state.phase_A)}."
    log_msg_B = f"B prioritized {map_label('B', st.session_state.phase_B)}."
    
    if congestion_B > 15 and st.session_state.action_A == "Switching":
        log_msg_A += " (Avoided FAR-WEST Green due to B's congestion)"
    if congestion_A > 15 and st.session_state.action_B == "Switching":
        log_msg_B += " (Avoided FAR-EAST Green due to A's congestion)"

    log_entry = {
        "time": time.strftime('%H:%M:%S'), 
        "msg_A": log_msg_A,
        "msg_B": log_msg_B,
        "cong_A": congestion_A,
        "cong_B": congestion_B
    }
    st.session_state.logs.insert(0, log_entry)

