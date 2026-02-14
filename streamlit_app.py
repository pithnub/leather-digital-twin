import streamlit as st
import math

# --- KNOWLEDGE BASE: INDUSTRIAL CHEMISTRY ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "desc": "Typically rapid fixation and surface focused."},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "desc": "Inherently salt stable with deep penetration."},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "desc": "Standard grain-focused lubrication property."},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "desc": "Polymer-based with reactive barrier logic."},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "desc": "Superior electrolyte stability; stays mobile easily."},
    "Raw/Neutral Oil (Neatsfoot)": {"stability": 1, "pen": 0.2, "desc": "High crash risk without significant NSA/Surfactants."}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_sat = min(1.0, cr_offer / 3.0)
        self.free_cr = max(0, cr_offer - 3.0)

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_retan, temp_fat, pickle, dry_method, climate, is_wp):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. ELECTRICAL DRAG & ZETA POTENTIAL
        veg_map = {"None": 0, "Tara": 25, "Mimosa": -6, "Chestnut": -12}
        base_charge = (self.cr_sat * 100) + ((7.0 - self.ph) * 15)
        soup_masking = (syn * 10) + (nsa * 28) + veg_map.get(veg, 0)
        eff_zeta = base_charge - soup_masking
        
        # 2. MECHANICAL ENERGY (Furniture Logic)
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_map = {"None (Smooth)": 0.45, "Pegs or Shelves": 1.15, "Both (Hybrid)": 1.55}
        furn_mod = furn_map.get(furniture, 1.0)
        drop_mod = max(0.1, 1.0 - ((load_factor - 40) / 100))
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * drop_mod * furn_mod) / 1000) * (duration / 60)
        
        # 3. CHEMICAL MIXTURE & THERMAL MOBILITY
        mix_stability = ((FATLIQUOR_SPECS[o1]['stability'] * off1) + (FATLIQUOR_SPECS[o2]['stability'] * off2) + (FATLIQUOR_SPECS[o3]['stability'] * off3)) / total_offer
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        
        # Thermodynamics: Temp Fat increases mobility, but Temp Jump increases fixation speed
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        temp_jump = max(0, temp_fat - temp_retan)

        # 4. FIXATION RATE (Thermodynamic Stress Logic)
        fixation_rate = 1.0 + (max(0, self.ph - 5.1) * temp_jump * (0.1 / (mix_stability * 0.5)) * (1 + total_offer/12) * (1 + load_factor/100))
        
        # 5. PENETRATION (Fick's Second Law)
        diffusion_path = self.thick ** 2 
        wall_res = 1.45 if pickle == "Chaser" else 0.85 
        pen_res = (max(0, eff_zeta) * 0.01 * diffusion_path * wall_res * fixation_rate)
        pen_score = 100 / (1 + (pen_res / (oil_mobility * mix_pen_base * kinetic_oomph + 0.1)))
        
        # 6. QUALITY INDICATORS
        break_val = max(1.0, min(5.0, 5 - (pen_score / 25) + (fixation_rate * 0.3)))
        vbi = (1.0 + (total_offer / 12)) * (1.35 if is_wp else 1.0)
        
        # 7. DRYING COMPLEXITY
        climate_res = 1.0 if climate == "Temperate" else 2.7
        if dry_method == "Air Drying":
            complexity = (self.thick**2) * vbi * climate_res
            method_desc = "Natural capillary evaporation. High sensitivity to ambient humidity."
            advice = "Ensure airflow; risk of salt spue in tropical conditions."
        else: # Partial Vacuum
            vbi_adj = vbi * 1.35 if self.ph > 5.4 else vbi * 0.75
            complexity = (self.thick**1.6) * vbi_adj * (climate_res * 0.55)
            method_desc = "Mechanical moisture extraction. Vacuum pulls oil to the surface."
            advice = "High VBI may lead to grain darkening during extraction."

        area_yield = max(78, 100 - ((vbi - 1.0) * 19))
        
        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1), "VBI": round(vbi, 2),
            "Complexity": round(complexity, 1), "Yield": round(area_yield, 1), "Fix": round(fixation_rate, 2),
            "Oomph": round(kinetic_oomph, 2), "Velocity": round(v_peripheral, 2), "Break": round(break_val, 1),
            "Fix_Desc": method_desc, "Advice": advice, "Oil_Note": FATLIQUOR_SPECS[o1]['desc'], "Total_Oil": round(total_offer, 2),
            "Temp_Jump": temp_jump
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v10.3", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v10.3)")

with st.sidebar:
    st.header("🥣 1. Recipe & Auxiliaries")
    o1 = st.selectbox("Oil A (Primary)", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 10.0, 3.0)
    o2 = st.selectbox("Oil B (Secondary)", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 10.0, 4.0)
    o3 = st.selectbox("Oil C (Stability)", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.number_input("% Offer (C)", 0.0, 10.0, 0.0)
    
    st.header("🧪 2. Chemical Modifiers")
    syn = st.slider("Syntan (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA / Surfactant (%)", 0.0, 3.0, 0.5)
    veg = st.selectbox("Veg Type", ["None", "Tara", "Mimosa", "Chestnut"])
    cr = st.slider("Chrome (%)", 0.0, 8.0, 4.5)

    st.header("🥁 3. Drum Engineering")
    furniture = st.radio("Mechanical Furniture", ["None (Smooth)", "Pegs or Shelves", "Both (Hybrid)"], index=1)
    duration = st.slider("Run Time (min)", 30, 240, 90)
    load_factor = st.slider("Drum Loading (%)", 10, 90, 40)
    rpm = st.slider("RPM", 2, 20, 12)
    diameter = st.number_input("Diameter (m)", 1.5, 5.0, 3.0)
    weight = st.number_input("Weight (kg)", 100, 5000, 1000)

    st.header("📐 4. Physical & Thermal Controls")
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 1.6)
    ph = st.slider("Neutralization pH", 4.0, 8.0, 5.7)
    temp_retan = st.slider("Retan Temperature (°C)", 20, 45, 35)
    temp_fat = st.slider("Fatliquor Temperature (°C)", 35, 65, 55)
    pickle = st.radio("Pickle Strategy", ["Equilibrium", "Chaser"])

    st.header("💨 5. Drying")
    is_wp = st.checkbox("Waterproofing logic active?", value=True)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_retan, temp_fat, pickle, dry_method, climate, is_wp)

if res:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Core Penetration", f"{res['Pen']}%")
    c2.metric("Break Grade", f"G{res['Break']}")
    c3.metric("Cumulative Energy", f"{res['Oomph']} kJ")
    c4.metric("Thermal Jump (ΔT)", f"{res['Temp_Jump']} °C")

    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🥁 Process Analysis")
        if res['Pen'] > 90: st.success("✨ **Optimal Migration:** Full penetration achieved.")
        elif res['Pen'] < 45: st.error("🚨 **FIXATION CRASH:** Oil fixed on grain before core migration.")
        else: st.warning("⚖️ **Marginal Result:** Poor core lubrication risk.")
        
        st.write(f"**Total Mass Offer:** {res['Total_Oil']}% w/w")
        st.info(f"**Primary Oil:** {res['Oil_Note']}")

    with col_r:
        st.subheader("🌡️ Fixation & Drying")
        st.metric("Vapor Barrier (VBI)", res['VBI'])
        st.write(f"**Fixation Delta:** {res['Fix']}")
        
        if res['Temp_Jump'] > 25:
            st.error("⚠️ **THERMAL SHOCK:** Large ΔT causing premature fixation.")
        if res['Fix'] > 2.0:
            st.error("⚠️ **COARSE GRAIN:** High fixation rate likely to cause loose break.")

st.caption("v10.3 Platinum | Thermal Delta Fixed | Absolute Offer Physics")
