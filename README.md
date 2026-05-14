# 🚦 AI Adaptive Traffic Control System

## 1. Project Overview
This project implements an **Adaptive Traffic Signal Control (ATSC)** system using the **A* (Informed Search)** algorithm. The primary objective is to replace traditional static traffic timers with a dynamic decision-making mechanism that adjusts signal phases based on real-time congestion levels.

**Key Goals:**
*   **Minimize Waiting Time:** Reduce cumulative vehicle delay across the intersection.
*   **Ensure Fairness:** Prevent starvation in low-traffic lanes using non-linear penalties.
*   **Emergency Priority:** Guarantee immediate preemption for emergency vehicles.

---

## 🛠️ 2. Execution Instructions

### 2.1 Prerequisites
The system requires:
*   **Python:** Version 3.8 or higher.
*   **Streamlit:** For the graphical user interface.

### 2.2 Installation
Install the required dependency via pip:
```bash
pip install streamlit
```

### 2.3 Running the Application
Navigate to the project directory and execute:
```bash
python -m streamlit run app.py
```
*The application will automatically launch in your default web browser (typically at http://localhost:8501).*

---

## 🏗️ 3. Project Structure
The project is organized into a modular structure for scalability:
- `app.py`: Main entry point and Streamlit UI layout.
- `src/logic/`: Core A* algorithm and simulation engine.
- `src/ui/`: Reusable UI components and visualizers.
- `src/analytics/`: Performance comparison and metrics logic.
- `src/config/`: Global styles and page configurations.

### 3.1 Normal Congestion Scenario
*   **Input:** Set Mode to `Normal` and Density slider to a medium value (e.g., `5`).
*   **Behavior:** 
    *   Signals switch every 6–10 seconds depending on relative congestion.
    *   The A* engine evaluates all four possible signal phases.
    *   The lane with the highest cumulative wait penalty is prioritized.
*   **Observation:** View the **Decision Log** in real-time to see computed $f(n)$ values for each action.

### 3.2 Emergency Vehicle Preemption
*   **Input:** Click any **"Trigger Emergency"** button (e.g., East).
*   **System Behavior:** 
    *   The selected lane immediately receives a green signal.
    *   Minimum green timer constraints are overridden.
    *   A massive penalty (+100,000) is applied to all non-emergency lanes.
*   **Observation:** Observe the immediate signal override and log output showing priority enforcement.

---

## 🧠 4. Technical Overview

### 4.1 Algorithmic Approach
The system is built on the **A* Search Algorithm**, navigating a transition-based state space.

**Evaluation Function:**  
$$f(n) = g(n) + h(n)$$

*   **$g(n)$ (Path Cost):** Represents the accumulated waiting cost and switch penalties.
*   **$h(n)$ (Heuristic):** Estimates future delay using the formula:
    $$h(n) = \sum (Count_{RedLane})^{1.5}$$

**Heuristic Logic:** The $1.5$ exponent applies a **non-linear penalty** to longer queues. This creates increasing "pressure" to switch as congestion builds, effectively preventing starvation and ensuring fairness.

### 4.2 Operational Constraints
To ensure realistic and stable behavior, the following constraints are enforced:
*   **Minimum Green Time (6s):** Prevents unsafe rapid signal switching (stuttering).
*   **Switch Penalty (Hysteresis):** A transition cost is added to $g(n)$ to discourage switching unless the benefit clearly exceeds the cost.
*   **Emergency Hard Constraint:** Emergency lanes receive absolute priority via state pruning.

---

## 🏗️ 5. System Architecture
The system is structured into four functional layers:
1.  **Perception Layer:** Monitors simulated traffic density and emergency triggers.
2.  **Search Engine:** Executes the A* decision logic to find the optimal phase.
3.  **Control Layer:** Applies operational constraints (timings) before execution.
4.  **UI Layer (Streamlit):** Displays the intersection state, car counts, and decision logs.

---

## 💻 6. Technology Stack
*   **Python:** Core algorithm and logic implementation.
*   **Streamlit:** High-performance reactive web interface.
*   **CSS Grid:** Optimized rendering of the 4-way intersection layout.

---
**Course:** AI2002: Artificial Intelligence  

