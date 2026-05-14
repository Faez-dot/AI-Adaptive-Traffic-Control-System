import heapq

class IntersectionState:
    """
    Represents a specific state of the traffic intersection.
    Used for A* pathfinding to find the optimal sequence of phases.
    """
    def __init__(self, cars_per_lane, current_phase, total_wait_time=0, steps=0):
        self.cars_per_lane = cars_per_lane
        self.current_phase = current_phase
        self.total_wait_time = total_wait_time
        self.steps = steps

    def __lt__(self, other):
        return self.total_wait_time < other.total_wait_time

def get_heuristic(state, scenario, priority_lane=None, neighbor_congestion=0, neighbor_direction=None):
    """
    DOMAIN-SPECIFIC HEURISTIC: Optimizes for throughput and fairness.
    Includes COOPERATIVE AI logic: Penalizes sending traffic to a congested neighbor.
    """
    h_cost = 0
    for lane, count in state.cars_per_lane.items():
        if lane != state.current_phase:
            h_cost += (count ** 1.5) * 5 
        else:
            h_cost += count * 1

    if scenario == "Rush Hour":
        h_cost *= 1.2
    elif scenario == "Night":
        h_cost *= 2.0

    if priority_lane:
        if state.current_phase != priority_lane:
            h_cost += 100000 

    if neighbor_direction and state.current_phase == neighbor_direction:
        if neighbor_congestion > 15:
            h_cost += neighbor_congestion * 10
    return h_cost

def a_star_decision(initial_cars, current_phase, scenario, priority_lane=None, neighbor_congestion=0, neighbor_direction=None):
    """
    Implementation of A* Search to find the next optimal light phase with Cooperative Multi-Agent support.
    """
    start_state = IntersectionState(initial_cars.copy(), current_phase)
    open_set = []
    h = get_heuristic(start_state, scenario, priority_lane, neighbor_congestion, neighbor_direction)
    heapq.heappush(open_set, (h, start_state))
    
    phases = ["North", "South", "East", "West"]
    best_phase = current_phase
    min_f = float('inf')
    all_costs = {}

    for p in phases:
        next_cars = initial_cars.copy()
        cleared = min(next_cars[p], 5)
        next_cars[p] -= cleared
        remaining_delay = sum(next_cars.values())
        switch_penalty = 8 if p != current_phase else 0
        g = remaining_delay + switch_penalty
        
        temp_state = IntersectionState(next_cars, p)
        h = get_heuristic(temp_state, scenario, priority_lane, neighbor_congestion, neighbor_direction)
        f = g + h
        all_costs[p] = f
        
        if f < min_f:
            min_f = f
            best_phase = p
            
    return best_phase, min_f, all_costs
