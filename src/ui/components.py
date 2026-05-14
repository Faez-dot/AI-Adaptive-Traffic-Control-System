import streamlit as st

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
        res += '<span class="siren-active" style="font-size: 35px;">🚑</span>'
    if count > 0:
        res += "🚗" * min(count, 3)
    return res

def render_intersection(name, cars, phase, action, emerg):
    if name == "A":
        lbl_n, lbl_s, lbl_w, lbl_e = "NORTH-WEST", "SOUTH-WEST", "FAR-WEST", "CENTRAL"
    else:
        lbl_n, lbl_s, lbl_w, lbl_e = "NORTH-EAST", "SOUTH-EAST", "CENTRAL", "FAR-EAST"

    return f"""
    <div style="text-align:center; margin-bottom:-20px;"><h3>Intersection {name}</h3></div>
    <div class="intersection-container">
    <div class="road road-v" style="grid-row: 1; grid-column: 2;">
    <div class="road-name" style="top: 10px; right: 10px; font-size:14px;">{lbl_n}</div>
    <div class="car-label label-n" style="top:10px; left:10px;">{cars['North']}</div>
    <div style="position:absolute; bottom:50px; font-size:25px;">{draw_v(cars['North'], emerg == 'North')}</div>
    {get_light_html('North', phase, action)}
    <div class="crosswalk-v cw-north"></div>
    </div>
    <div class="road road-h" style="grid-row: 2; grid-column: 1;">
    <div class="road-name" style="top: 10px; left: 10px; font-size:14px;">{lbl_w}</div>
    <div class="car-label label-w" style="bottom:10px; left:10px;">{cars['West']}</div>
    <div style="position:absolute; right:50px; font-size:25px;">{draw_v(cars['West'], emerg == 'West')}</div>
    {get_light_html('West', phase, action)}
    <div class="crosswalk-h cw-west"></div>
    </div>
    <div class="center-box"></div>
    <div class="road road-h" style="grid-row: 2; grid-column: 3;">
    <div class="road-name" style="bottom: 10px; right: 10px; font-size:14px;">{lbl_e}</div>
    <div class="car-label label-e" style="top:10px; right:10px;">{cars['East']}</div>
    <div style="position:absolute; left:50px; font-size:25px;">{draw_v(cars['East'], emerg == 'East')}</div>
    {get_light_html('East', phase, action)}
    <div class="crosswalk-h cw-east"></div>
    </div>
    <div class="road road-v" style="grid-row: 3; grid-column: 2;">
    <div class="road-name" style="bottom: 10px; left: 10px; font-size:14px;">{lbl_s}</div>
    <div class="car-label label-s" style="bottom:10px; right:10px;">{cars['South']}</div>
    <div style="position:absolute; top:50px; font-size:25px;">{draw_v(cars['South'], emerg == 'South')}</div>
    {get_light_html('South', phase, action)}
    <div class="crosswalk-v cw-south"></div>
    </div>
    </div>
    """
