import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: MULTI-OIL KINETICS ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9, "desc": "High surface nourishment; prone to grain crash."},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7, "desc": "Inherently salt stable; deep penetration."},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "soft": 0.8, "desc": "Standard grain-focused lubrication."},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "soft": 0.4, "desc": "Polymer-based; high stand, lower yield."},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8, "desc": "Superior electrolyte stability; maximum yield."},
    "Raw/Neutral Oil (Neatsfoot)": {"stability": 1, "pen": 0.2, "soft": 1.2, "desc": "High crash risk; requires high NSA."}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_offer = cr_offer

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_fat, dry_method, climate, pickle_type):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. THE CHROME GRADIENT PARADOX (Your Specification)
        # Chaser Pickle = Surface is light/easy to neutralize, but Core is a 'Chrome Dam'
        if pickle_type == "Chaser (Core Heavy)":
            effective_ph = self.ph + 0.35  # Surface feels more 'open' to neutralization
            core_barrier = (self.cr_offer * 0.28) * (self.thick / 1.5)
            surface_drag = 0.65 
            yield_mod = 1.15 # Internal tension is higher
        else: # Equilibrium
            effective_ph = self.ph
            core_barrier = (self.cr_offer * 0.14)
            surface_drag = 1.25 # Chrome is more present on the surface
            yield_mod = 1.0

        # 2. ELECTRICAL DRAG & ZETA POTENTIAL
        ph_stress = math.exp(max(0, 5.2 - effective_ph)) 
        base_charge = (self.cr_offer * 18) + (ph_stress * 22)
        soup_masking = (syn * 12) + (nsa * 32) + {"None": 0, "Tara": 25, "Mimosa": -6, "Chestnut": -12}.get(veg, 0)
        eff_zeta = (base_charge * surface_drag) - soup_masking
        
        # 3. MECHANICAL ENGINE (Direct Coupling)
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_mod = {"None (Smooth)": 0.45, "Pegs or Shelves": 1.15, "Both (Hybrid)": 1.55}.get(furniture, 1.0)
        drop_mod = max(0.1, 1.0 - ((load_factor - 40) / 100))
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * drop_mod * furn_mod) / 1000) * (duration / 60)
        mech_punch = (v_peripheral * furn_mod * (duration / 45)) / (self.thick + 0.5)
        
        # 4. PENETRATION (Fick's Second Law with Structural Dam)
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        
        diffusion_res = (self.thick ** 2.2) * (1 + core_barrier)
        pen_score = 100 / (1 + ((eff_zeta * 0.025 * diffusion_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 5. AREA RETENTION & DRYING
        climate_res = 1.0 if climate == "Temperate" else 1.35
        base_yield = 100 - (total_offer * 1.3)
        dry_mod = 1.55 if dry_method == "Partial Vacuum" else 0.45
        area_yield = base_yield - (self.thick * dry_mod * climate_res) - (self.cr_offer * 0.5 * yield_mod)

        # 6. QUALITY INDICATORS
        break_val = max(1.0, min(5.0, 5 - (pen_score / 22) + (ph_stress * 0.45)))
        
        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1), 
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), 
            "Punch": round(mech_punch, 2), "Barrier": round(core_barrier, 2),
            "Break": round(break_val, 1), "Oil_Note": FATLIQUOR_SPECS[o1]['desc']
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v10.9", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v10.9)")

with st.sidebar:
    st.header("🥣 1. Recipe: Triple-Oil Blend")
    o1 = st.selectbox("Primary Oil", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 15.0, 4.0)
    o2 = st.selectbox("Secondary Oil", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 15.0, 2.0)
    o3 = st.selectbox("Stability Oil", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.number_input("% Offer (C)", 0.0, 15.0, 0.0)
    
    st.header("🧪 2. Chemical Modifiers")
    syn = st.slider("Syntan (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA / Surfactant (%)", 0.0, 3.0, 0.5)
    veg = st.selectbox("Veg Type", ["None", "Tara", "Mimosa", "Chestnut"])
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    pickle_type = st.radio("Pickle Type", ["Equilibrium (Uniform)", "Chaser (Core Heavy)"])

    st.header("🥁 3. Mechanical Engineering")
    furniture = st.radio("Drum Furniture", ["None (Smooth)", "Pegs or Shelves", "Both (Hybrid)"], index=1)
    duration = st.slider("Run Time (min)", 30, 240, 90)
    rpm = st.slider("Drum Speed (RPM)", 2, 20, 10)
    diameter = st.number_input("Drum Diameter (m)", 1.5, 5.0, 3.0)
    weight = st.number_input("Total Load (kg)", 100, 5000, 1000)

    st.header("📐 4. Substrate & Drying")
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 2.0)
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.2)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, 40, furniture, rpm, diameter, weight, 55, dry_method, climate, pickle_type)

if res:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Core Strike", f"{res['Pen']}%")
    m2.metric("Area Yield", f"{res['Yield']}%")
    m3.metric("Mechanical Work", f"{res['Oomph']} kJ")
    m4.metric("Corium Dam", res['Barrier'])
    m5.metric("Grain Break", f"G{res['Break']}")

    st.divider()
    

    st.subheader("📍 Anatomical Process Profile")
    if pickle_type == "Chaser (Core Heavy)":
        cr_grad, oil_grad = [0.6, 0.8, 1.2, 0.8, 0.6], [1.0, 0.8, 0.3*(res['Pen']/100), 0.8, 1.0]
    else:
        cr_grad, oil_grad = [1.0, 1.0, 1.0, 1.0, 1.0], [1.0, 0.85, 0.6*(res['Pen']/100), 0.85, 1.0]
    
    st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'],
                                'Chrome Profile': cr_grad, 'Oil Profile': oil_grad}).set_index('Layer'))

    st.info(f"**Technician's Note:** {res['Oil_Note']} in use. Effective Zeta at surface: {res['Zeta']}")
