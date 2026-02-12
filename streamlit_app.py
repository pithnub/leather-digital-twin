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

    def simulate(self, fat_name, syn, nsa, veg, pickle, dry_method, climate, rpm, diameter, weight, temp_retan, temp_fat, is_wp):
        spec = FATLIQUOR_SPECS[fat_name]
        
        # 1. MECHANICAL WORK (Kinetic Oomph)
        v_peripheral = (math.pi * diameter * rpm) / 60
        drop_energy = (weight * 9.81 * (diameter * 0.75)) / 1000 
        kinetic_oomph = v_peripheral * drop_energy
        
        # 2. ELECTRICAL DRAG (Covington's Link-Lock)
        veg_map = {"None": 0, "Tara": 25, "Mimosa": -6, "Chestnut": -12}
        veg_power = veg_map.get(veg, 0)
        base_charge = (self.cr_sat * 100) + ((7.0 - self.ph) * 15)
        soup_masking = (syn * 10) + (nsa * 28) + veg_power
        eff_zeta = base_charge - soup_masking
        
        # 3. THERMAL MOBILITY & FIXATION RATE
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        temp_jump = temp_fat - temp_retan
        fixation_rate = 1.0 + (max(0, self.ph - 5.1) * temp_jump * 0.05)
        
        # 4. PENETRATION (Fick's Second Law + Mechanics)
        diffusion_path = self.thick ** 2 
        wall_res = 1.45 if pickle == "Chaser" else 0.85 
        
        pen_res = (max(0, eff_zeta) * 0.01 * diffusion_path * wall_res * fixation_rate)
        pen_score = 100 / (1 + (pen_res / (oil_mobility * kinetic_oomph + 0.1)))
        
        # 5. VAPOR BARRIER INDEX (VBI - Surface Loading)
        vbi = 1.0
        if self.ph > 5.3 and spec['stability'] < 4: vbi *= 2.1 
        if self.free_cr > 1.0: vbi *= (1.2 + (self.free_cr * 0.06)) 
        if is_wp: vbi *= 1.35 
        
        # 6. DRYING THERMODYNAMICS
        climate_res = 1.0 if climate == "Temperate" else 2.7
        if dry_method == "Air Drying":
            complexity = (self.thick**2) * vbi * climate_res
            method_desc = "Natural capillary evaporation. High sensitivity to ambient humidity."
        else: # Partial Vacuum
            vbi_adj = vbi * 1.35 if self.ph > 5.4 else vbi * 0.75
            complexity = (self.thick**1.6) * vbi_adj * (climate_res * 0.55)
            method_desc = "Mechanical moisture extraction. Risk of 'Blinded Grain' at high pH."

        area_yield = max(78, 100 - ((vbi - 1.0) * 19))
        
        return {
            "Zeta": round(eff_zeta, 1),
            "Pen": round(min(100, pen_score), 1),
            "VBI": round(vbi, 2),
            "Complexity": round(complexity, 1),
            "Yield": round(area_yield, 1),
            "Fixation": round(fixation_rate, 2),
            "Oomph": round(kinetic_oomph, 2),
            "Velocity": round(v_peripheral, 2),
            "Oil_Note": spec['desc'],
            "Fixation_Desc": method_desc
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v8.7", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v8.7)")
st.markdown("### The Predictor: Overcoming Chemical Fixation with Drum Mechanics")

with st.sidebar:
    st.header("🏗️ 1. Drum Engineering")
    diameter = st.number_input("Drum Diameter (m)", 1.5, 5.0, 3.0)
    rpm = st.slider("Drum RPM", 2, 20, 12)
    weight = st.number_input("Weight of Goods (kg)", 100, 10000, 1000)
    
    st.header("🌡️ 2. Thermal Control")
    temp_retan = st.slider("Retan Temp (°C)", 20, 45, 35)
    temp_fat = st.slider("Fatliquor Temp (°C)", 35, 65, 55)
    
    st.header("📐 3. Substrate & Tanning")
    thick = st.number_input("Shaved Thickness (mm)", 0.5, 6.0, 1.6)
    ph = st.slider("Neutralization pH", 4.0, 8.0, 5.7)
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    pickle = st.radio("Pickle Strategy", ["Equilibrium", "Chaser"])

    st.header("🥣 4. Chemical Recipe")
    fat_choice = st.selectbox("Oil Chemistry", list(FATLIQUOR_SPECS.keys()))
    syn = st.slider("Syntan Offer (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA Offer (%)", 0.0, 3.0, 0.5)
    veg = st.selectbox("Veg Type", ["None", "Tara", "Mimosa", "Chestnut"])

    st.header("💨 5. Environment")
    is_wp = st.checkbox("Apply Waterproofing?", value=True)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE SIMULATION
twin = PlatinumIndustrialTwin(thick, cr, ph)
res = twin.simulate(fat_choice, syn, nsa, veg, pickle, dry_method, climate, rpm, diameter, weight, temp_retan, temp_fat, is_wp)

# DASHBOARD
c1, c2, c3, c4 = st.columns(4)
c1.metric("Kinetic Oomph (kJ)", res['Oomph'], help="Total mechanical energy delivered to the load.")
c2.metric("Core Penetration", f"{res['Pen']}%", help="Calculated saturation of the core center.")
c3.metric("Surface Loading (VBI)", res['VBI'], help="Vapor Barrier Index: >1.8 indicates an emulsion crash.")
c4.metric("Drying Complexity", res['Complexity'], help="Energy required to dry based on surface oil and climate.")

st.divider()

col_l, col_r = st.columns(2)
with col_l:
    st.subheader("🥁 Emulsion Stability Analysis")
    
    # DYNAMIC LOGIC: MATCHING THEORY TO RESULT
    if res['Pen'] > 90:
        st.success(f"✨ **Full Penetration (ø):** Process parameters successfully drove the {fat_choice} through the {thick}mm substance.")
    elif res['Pen'] < 45:
        st.error(f"🚨 **EMULSION CRASH:** Chemistry fixed too rapidly. The center of the {thick}mm substance is starving for lubricant.")
    else:
        st.warning(f"⚖️ **Saturation Warning:** Incomplete migration. The oil has stalled before reaching the center.")

    st.info(f"**Chemical Property:** {res['Oil_Note']}")
    st.write(f"**Electrical Drag (Zeta):** {res['Zeta']} mV")
    st.write(f"**Peripheral Velocity:** {res['Velocity']} m/s")

with col_r:
    st.subheader("🌡️ Fixation & Break Analysis")
    st.metric("Predicted Area Yield", f"{res['Yield']}%")
    st.write(f"**Drying Profile:** {res['Fixation_Desc']}")
    
    if res['Fixation'] > 1.6:
        st.error(f"⚠️ **RAPID FIXATION RISK:** Fixation rate ({res['Fixation']}) is too aggressive. High risk of grain distension (Coarse Break).")
    
    if res['Complexity'] > 35 and climate == "Tropical":
        st.error("🚨 **DRYING STALL:** High humidity + surface loading = stagnant evaporation.")
    elif dry_method == "Partial Vacuum" and ph > 5.4:
        st.warning("⚠️ **BLINDED GRAIN:** Vacuum heat is ironing un-fixed oil into the pores.")
    else:
        st.success("💨 **Open Path:** Fixation is internal; moisture transmission is optimal.")

st.caption(f"v8.7 Platinum Build | IULTCS Technical Toolkit | Models: Covington (Link-Lock) & Zhang (Saturation)")
