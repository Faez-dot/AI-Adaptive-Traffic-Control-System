import heapq
import time
import random

class IntersectionState:
    """
    Represents a specific state of the traffic intersection.
    Used for A* pathfinding to find the optimal sequence of phases.
    """
    def __init__(self, cars_per_lane, current_phase, total_wait_time=0, steps=0):
        # cars_per_lane: dict { 'North': 5, 'South': 2, 'East': 10, 'West': 8 }
        self.cars_per_lane = cars_per_lane
        self.current_phase = current_phase # 'NS_GREEN' or 'EW_GREEN'
        self.total_wait_time = total_wait_time
        self.steps = steps # Depth of search

    def __lt__(self, other):
        # For PriorityQueue: A* uses f(n) = g(n) + h(n)
        # This will be handled in the search function logic
        return self.total_wait_time < other.total_wait_time

def get_heuristic(state, scenario, priority_lane=None):
    """
    DOMAIN-SPECIFIC HEURISTIC: Optimizes for throughput and fairness.
    High penalty for cars stopped at RED lights.
    """
    h_cost = 0
    
    for lane, count in state.cars_per_lane.items():
        # Optimization: Only cars at RED lights contribute to the wait cost
        if lane != state.current_phase:
            # Quadratic penalty for long queues to prevent "stuck" lanes
            h_cost += (count ** 1.5) * 5 
        else:
            # Very small penalty for cars in the Green lane to encourage clearing them
            h_cost += count * 1

    # SCENARIO ADAPTATION:
    if scenario == "Rush Hour":
        # Heavier focus on total throughput
        h_cost *= 1.2
    elif scenario == "Night":
        # Focus on switching quickly for even single cars
        h_cost *= 2.0

    # EMERGENCY PREEMPTION:
    if priority_lane:
        if state.current_phase != priority_lane:
            h_cost += 100000 

    return h_cost

def a_star_decision(initial_cars, current_phase, scenario, priority_lane=None):
    """
    Implementation of A* Search to find the next optimal light phase.
    """
    start_state = IntersectionState(initial_cars.copy(), current_phase)
    
    # Priority Queue for A*: stores (f_score, state)
    open_set = []
    # f(n) = g(n) + h(n) -> g is 0 for the first step as we only want the 'next best' decision
    h = get_heuristic(start_state, scenario, priority_lane)
    heapq.heappush(open_set, (h, start_state))
    
    # Possible Actions/Phases (4-Phase System for Realism)
    phases = ["North", "South", "East", "West"]
    
    best_phase = current_phase
    min_f = float('inf')
    all_costs = {}

    for p in phases:
        next_cars = initial_cars.copy()
        
        # Only the selected lane clears in a 4-phase system
        cleared = min(next_cars[p], 5) # Increased clearance rate for efficiency
        next_cars[p] -= cleared
            
        # Calculate cost g(n): Total delay of remaining cars (g-score)
        remaining_delay = sum(next_cars.values())
        
        # Heavier penalty for switching phases to prevent "stuttering" lights
        switch_penalty = 8 if p != current_phase else 0
        
        g = remaining_delay + switch_penalty
        
        # Heuristic h(n)
        temp_state = IntersectionState(next_cars, p)
        h = get_heuristic(temp_state, scenario, priority_lane)
        
        f = g + h
        all_costs[p] = f
        
        if f < min_f:
            min_f = f
            best_phase = p
            
    return best_phase, min_f, all_costs
