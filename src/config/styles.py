import streamlit as st

def apply_styles():
    """Applies the page configuration and custom CSS for the premium dashboard aesthetic."""
    st.set_page_config(
        page_title="Multi-Agent Traffic Control", 
        layout="wide", 
        page_icon="🚦"
    )

    st.markdown("""
    <style>
    /* Main Background Hook */
    .stApp { background-color: #0d1117; color: #f8fafc; }
    
    /* Intersection Container */
    .intersection-container {
        display: grid;
        grid-template-columns: 180px 180px 180px;
        grid-template-rows: 180px 180px 180px;
        gap: 0px;
        justify-content: center;
        align-items: center;
        margin: 10px auto;
        background-color: #2e7d32; /* Grass background */
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
        position: relative;
        transform: scale(0.85);
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
