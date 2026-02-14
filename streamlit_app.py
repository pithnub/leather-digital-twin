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

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, pickle, dry_method, climate, rpm, diameter, weight, temp_retan, temp_fat, is_wp):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # Weighted Mixture Calculations based on absolute mass offers (w/w)
        mix_stability = ((FATLIQUOR_SPECS[o1]['stability'] * off1) + (FATLIQUOR_SPECS[o2]['stability'] * off2) + (FATLIQUOR_SPECS[o3]['stability'] * off3)) / total_offer
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        
        # 1. MECHANICAL WORK (Kinetic Oomph)
        v_peripheral = (math.pi * diameter * rpm) / 60
        drop_energy = (weight * 9.81 * (diameter * 0.75)) / 1000 
        kinetic_oomph = v_peripheral * drop_energy
        
        # 2. ELECTRICAL DRAG (Covington's Link-Lock)
        veg_map = {"None": 0, "Tara": 25, "Mimosa": -6, "Chestnut": -12}
        base_charge = (self.cr_sat * 100) + ((7.0 - self.ph) * 15)
        soup_masking = (syn * 10) + (nsa * 28) + veg_map.get(veg, 0)
        eff_zeta = base_charge - soup_masking
        
        # 3. THERMAL MOBILITY & FIXATION RATE 
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        temp_jump = temp_fat - temp_retan
        # Stability and mass volume both influence the fixation speed
        fixation_rate = 1.0 + (max(0, self.ph - 5.1) * temp_jump * (0.1 / (mix_stability * 0.5)) * (1 + total_offer/15))
        
        # 4. PENETRATION (Fick's Second Law + Mechanics)
        diffusion_path = self.thick ** 2 
        wall_res = 1.45 if pickle == "Chaser" else 0.85 
        pen_res = (max(0, eff_zeta) * 0.01 * diffusion_path * wall_res * fixation_rate)
        pen_score = 100 / (1 + (pen_res / (oil_mobility * mix_pen_base * kinetic_oomph + 0.1)))
        
        # 5. BREAK PREDICTION (Sample Correlation A/B/C)
        break_val = max(1.0, min(5.0, 5 - (pen_score / 25) + (fixation_rate * 0.3)))
        
        # 6. VAPOR BARRIER INDEX (VBI - Surface Loading)
        vbi = 1.0 + (total_offer / 12)
        if self.ph > 5.3 and mix_stability < 4: vbi *= 1.8 
        if self.free_cr > 1.0: vbi *= (1.2 + (self.free_cr * 0.06)) 
        if is_wp: vbi *= 1.35 
        
        # 7. DRYING THERMODYNAMICS
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
            "Break": round(break_val, 1),
            "Fix_Desc": method_desc,
            "Oil_Note": FATLIQUOR_SPECS[o1]['desc']
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v9.5", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v9.5)")
st.markdown("### Production Build: Absolute Mass Offer & Thermodynamics")

with st.sidebar:
    st.header("📋 1. Recipe Offers ($w/w$ %)")
    o1 = st.selectbox("Oil A", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 10.0, 3.0)
    o2 = st.selectbox("Oil B", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 10.0, 4.0)
    o3 = st.selectbox("Oil C", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.number_input("% Offer (C)", 0.0, 10.0, 0.0)

    st.header("🏗️ 2. Drum Engineering")
    diameter = st.number_input("Drum Diameter (m)", 1.5, 5.0, 3.0)
    rpm = st.slider("Drum RPM", 2, 20, 12)
    weight = st.number_input("Weight of Goods (kg)", 100, 10000, 1000)
    
    st.header("🌡️ 3. Thermal Control")
    temp_retan = st.slider("Retan Temp (°C)", 20, 45, 35)
    temp_fat = st.slider("Fatliquor Temp (°C)", 35, 65, 55)
    
    st.header("📐 4. Substrate & Tanning")
    thick = st.number_input("Shaved Thickness (mm)", 0.5, 6.0, 1.6)
    ph = st.slider("Neutralization pH", 4.0, 8.0, 5.7)
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    pickle = st.radio("Pickle Strategy", ["Equilibrium", "Chaser"])

    st.header("💨 5. Environment & Drying")
    is_wp = st.checkbox("Waterproofing?", value=True)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE SIMULATION
twin = PlatinumIndustrialTwin(thick, cr, ph)
res = twin.simulate(o1, off1, o2, off2, o3, off3, 5.0, 0.5, "None", pickle, dry_method, climate, rpm, diameter, weight, temp_retan, temp_fat, is_wp)

if res:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kinetic Oomph (kJ)", res['Oomph'], help="Total mechanical energy delivered.")
    c2.metric("Core Penetration", f"{res['Pen']}%")
    c3.metric("Break Grade", f"G{res['Break']}")
    c4.metric("Predicted Yield", f"{res['Yield']}%")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🥁 Emulsion Analysis")
        if res['Pen'] > 90:
            st.success(f"✨ **Full Penetration:** Process parameters successfully drove the blend through {thick}mm.")
        elif res['Pen'] < 45:
            st.error(f"🚨 **EMULSION CRASH:** Chemistry fixed too rapidly.")
        else:
            st.warning(f"⚖️ **Saturation Warning:** Incomplete migration.")

        st.info(f"**Primary Oil Note:** {res['Oil_Note']}")
        st.write(f"**Total Offer:** {off1+off2+off3}% w/w")
        st.write(f"**Electrical Drag (Zeta):** {res['Zeta']} mV")
        st.write(f"**Peripheral Velocity:** {res['Velocity']} m/s")

    with col_r:
        st.subheader("🌡️ Fixation & Drying")
        st.metric("Vapor Barrier (VBI)", res['VBI'])
        st.write(f"**Drying Profile:** {res['Fix_Desc']}")
        
        if res['Fixation'] > 2.0:
            st.error(f"⚠️ **FIXATION ALERT:** Fixation rate ({res['Fixation']}) is too aggressive. Risk of coarse break.")
        
        if res['Complexity'] > 35 and climate == "Tropical":
            st.error("🚨 **DRYING STALL:** High humidity + surface loading = stagnant evaporation.")
        else:
            st.success("💨 **Open Path:** Moisture transmission is optimal.")

st.caption("v9.5 Platinum Build | Full Industrial Physics Engine | IULTCS Technical Toolkit")
