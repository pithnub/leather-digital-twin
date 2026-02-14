import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: INDUSTRIAL CHEMISTRY ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9, "desc": "High surface nourishment; prone to grain crash."},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7, "desc": "Inherently salt stable with deep penetration."},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "soft": 0.8, "desc": "Standard grain-focused lubrication property."},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "soft": 0.4, "desc": "Polymer-based with reactive barrier logic."},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8, "desc": "Superior electrolyte stability; stays mobile easily."},
    "Raw/Neutral Oil (Neatsfoot)": {"stability": 1, "pen": 0.2, "soft": 1.2, "desc": "High crash risk without significant NSA/Surfactants."}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_offer = cr_offer  # Chrome now acts as a structural anchor (barrier)
        self.cr_sat = min(1.0, cr_offer / 3.0)

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_fat, dry_method, climate, is_wp):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. ENHANCED ZETA POTENTIAL & ELECTRICAL DRAG
        veg_map = {"None": 0, "Tara": 25, "Mimosa": -6, "Chestnut": -12}
        # Exponential 'pH Stress' models the chemical wall below pH 5.2
        ph_stress = math.exp(max(0, 5.2 - self.ph)) 
        base_charge = (self.cr_offer * 18) + (ph_stress * 22)
        soup_masking = (syn * 12) + (nsa * 32) + veg_map.get(veg, 0)
        eff_zeta = base_charge - soup_masking
        
        # 2. THE MECHANICAL ENGINE (Direct Coupling to Penetration)
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_map = {"None (Smooth)": 0.45, "Pegs or Shelves": 1.15, "Both (Hybrid)": 1.55}
        furn_mod = furn_map.get(furniture, 1.0)
        drop_mod = max(0.1, 1.0 - ((load_factor - 40) / 100))
        
        # Kinetic Oomph (Total Energy) and Mech Pressure (Instantaneous Force)
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * drop_mod * furn_mod) / 1000) * (duration / 60)
        # Mechanical 'Punch' scales with RPM and Time, but is resisted by thickness
        mech_punch = (v_peripheral * furn_mod * (duration / 45)) / (self.thick + 0.5)
        
        # 3. CHEMICAL MIXTURE & THERMAL MOBILITY
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)

        # 4. PENETRATION LOGIC (Coupled Mechanical/Chemical Resistance)
        # Chrome Offer increases structural 'stickiness', making penetration harder.
        diffusion_barrier = (self.thick ** 2) * (1 + (self.cr_offer * 0.2))
        pen_res = (max(0, eff_zeta) * 0.025 * diffusion_barrier)
        # The core formula: Mech Punch must overcome the Pen Resistance
        pen_score = 100 / (1 + (pen_res / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 5. AREA RETENTION & DRYING (Climate/Method Interaction)
        climate_res = 1.0 if climate == "Temperate" else 1.35
        base_yield = 100 - (total_offer * 1.3)
        
        if dry_method == "Air Drying":
            area_yield = base_yield - (self.thick * 0.45 * climate_res)
            method_desc = "Capillary Evaporation: Natural fiber relaxation."
            advice = "Safest for area yield; risk of salt spue in tropical humid zones."
        else: # Partial Vacuum
            # High pH + High Chrome + Vacuum = Maximum Striction (Area Loss)
            striction_mod = 1.9 if self.ph > 5.5 else 1.3
            area_yield = base_yield - (self.thick * 1.5 * striction_mod * climate_res) - (self.cr_offer * 0.5)
            method_desc = "Mechanical Striction: High pressure moisture extraction."
            advice = "Significant area loss likely. Monitor vacuum temperature closely."

        # 6. QUALITY INDICATORS
        break_val = max(1.0, min(5.0, 5 - (pen_score / 22) + (ph_stress * 0.45)))
        
        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1), 
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), 
            "Break": round(break_val, 1), "Dry_Note": method_desc, 
            "Advice": advice, "Oil_Note": FATLIQUOR_SPECS[o1]['desc'],
            "Punch": round(mech_punch, 2)
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v10.6", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v10.6)")

with st.sidebar:
    st.header("🥣 1. Recipe: Triple-Oil Blend")
    o1 = st.selectbox("Oil A (Primary)", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 10.0, 4.0)
    o2 = st.selectbox("Oil B (Filler)", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 10.0, 2.0)
    o3 = st.selectbox("Oil C (Fixation/WP)", list(FATLIQUOR_SPECS.keys()), index=3)
    off3 = st.number_input("% Offer (C)", 0.0, 10.0, 0.0)
    
    st.header("🧪 2. Chemical Modifiers")
    syn = st.slider("Syntan (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA / Surfactant (%)", 0.0, 3.0, 0.5)
    veg = st.selectbox("Veg Type", ["None", "Tara", "Mimosa", "Chestnut"])
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)

    st.header("🥁 3. Mechanical Physics")
    furniture = st.radio("Drum Furniture", ["None (Smooth)", "Pegs or Shelves", "Both (Hybrid)"], index=1)
    duration = st.slider("Run Time (min)", 30, 240, 90)
    rpm = st.slider("RPM Speed", 2, 20, 10)
    diameter = st.number_input("Drum Diameter (m)", 1.5, 5.0, 3.0)
    weight = st.number_input("Load Weight (kg)", 100, 5000, 1000)

    st.header("📐 4. Substrate & Climate")
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 1.8)
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.2)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, 40, furniture, rpm, diameter, weight, 55, dry_method, climate, True)

if res:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Core Penetration", f"{res['Pen']}%")
    c2.metric("Area Yield", f"{res['Yield']}%")
    c3.metric("Mechanical Work", f"{res['Oomph']} kJ")
    c4.metric("Mech Punch", res['Punch'])
    c5.metric("Grain Break", f"G{res['Break']}")

    st.divider()
    

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🥁 Mechanical/Chemical Balance")
        if res['Pen'] < 55:
            st.error(f"🚨 **FIXATION CRASH:** Mech Punch ({res['Punch']}) is too low to overcome Zeta potential ({res['Zeta']}).")
        else:
            st.success(f"✨ **Balanced:** Mechanical energy successfully navigated the Chrome/pH barrier.")
        st.info(f"**Oil Note:** {res['Oil_Note']}")

    with col_r:
        st.subheader("💨 Yield & Advice")
        st.write(f"**Method:** {res['Dry_Note']}")
        st.write(f"**Strategic Advice:** {res['Advice']}")
        if res['Yield'] < 88:
            st.warning("⚠️ **High Striction Alert:** Check Chrome offer and Neutralization pH to prevent area loss.")
