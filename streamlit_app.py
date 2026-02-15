import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: THE INDUSTRIAL CHEMICAL DATABASE ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9, "cloud_point": 18, "spue_f": 0.8, "grease_drag": 0.6},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7, "cloud_point": 5, "spue_f": 0.2, "grease_drag": 0.1},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "soft": 0.8, "cloud_point": 12, "spue_f": 0.4, "grease_drag": 0.3},
    "Synthetic Waterproofing": {"stability": 6, "pen": 0.7, "soft": 0.4, "cloud_point": 2, "spue_f": 0.1, "grease_drag": 0.4},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8, "cloud_point": 0, "spue_f": 0.05, "grease_drag": 0.05},
    "Raw/Neutral Oil": {"stability": 1, "pen": 0.2, "soft": 1.2, "cloud_point": 25, "spue_f": 1.2, "grease_drag": 0.9}
}

VEG_SPECS = {
    "None": {"zeta": 0, "fill": 0.0, "astringency": 0.0},
    "Tara": {"zeta": 25, "fill": 1.45, "astringency": 0.1},
    "Mimosa": {"zeta": -6, "fill": 1.15, "astringency": 0.5},
    "Chestnut": {"zeta": -18, "fill": 0.85, "astringency": 1.3}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick, self.cr_offer, self.ph = thick, cr_offer, ph_val

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, veg_off, duration, load_factor, furniture, rpm, diameter, weight, temp_fat, temp_retan, vac_temp, dry_method, climate, pickle_type, is_wp):
        total_oil = off1 + off2 + off3
        if total_oil == 0: return None
        
        # 1. TANNIN FILLING & BRACING
        v = VEG_SPECS[veg]
        veg_fill_gain = (veg_off * v['fill']) * 0.28 
        astringency_loss = (veg_off * v['astringency']) * 0.18 if self.ph < 5.0 else 0
        
        # 2. CHROME GRADIENT & CORE DAM (Pickle Logic)
        if pickle_type == "Chaser (Core Heavy)":
            eff_neutral_ph = self.ph + 0.45
            core_barrier = (self.cr_offer * 0.48) * (self.thick / 1.5)
            surface_drag, case_hard = 0.50, 1.55
        else: # Equilibrium
            eff_neutral_ph = self.ph
            core_barrier = (self.cr_offer * 0.22)
            surface_drag, case_hard = 1.38, 1.0

        # 3. ZETA POTENTIAL & ELECTRICAL DRAG
        ph_stress = math.exp(max(0, 5.2 - eff_neutral_ph)) 
        base_charge = (self.cr_offer * 21.5) + (ph_stress * 27.0)
        soup_masking = (syn * 16.0) + (nsa * 48.0) + v['zeta']
        eff_zeta = (base_charge * surface_drag) - soup_masking
        
        # 4. MECHANICAL ENERGY ENGINE
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_mod = {"None": 0.45, "Pegs": 1.15, "Hybrid": 1.55}.get(furniture, 1.15)
        drop_mod = max(0.1, 1.0 - ((load_factor - 40) / 100))
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * drop_mod * furn_mod) / 1000) * (duration / 60)
        mech_punch = (v_peripheral * furn_mod * (duration / 45)) / (self.thick + 0.5)
        
        # 5. THERMAL MOBILITY & FIXATION
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        temp_jump = max(0, temp_fat - temp_retan)
        fixation_rate = 1.0 + (temp_jump * 0.07)

        # 6. PENETRATION KINETICS (Strike Calculation)
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen']*off1) + (FATLIQUOR_SPECS[o2]['pen']*off2) + (FATLIQUOR_SPECS[o3]['pen']*off3)) / total_oil
        diff_res = (self.thick ** 2.70) * (1 + core_barrier) * case_hard * fixation_rate
        pen_score = 100 / (1 + ((eff_zeta * 0.042 * diff_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 7. SPUE & ADHESION QUALITY ENGINES
        avg_cloud = ((FATLIQUOR_SPECS[o1]['cloud_point']*off1) + (FATLIQUOR_SPECS[o2]['cloud_point']*off2) + (FATLIQUOR_SPECS[o3]['cloud_point']*off3)) / total_oil
        spue_f = ((FATLIQUOR_SPECS[o1]['spue_f']*off1) + (FATLIQUOR_SPECS[o2]['spue_f']*off2) + (FATLIQUOR_SPECS[o3]['spue_f']*off3)) / total_oil
        grease_drag = ((FATLIQUOR_SPECS[o1]['grease_drag']*off1) + (FATLIQUOR_SPECS[o2]['grease_drag']*off2) + (FATLIQUOR_SPECS[o3]['grease_drag']*off3)) / total_oil
        
        climate_impact = 1.8 if climate == "Tropical" else 1.2
        spue_index = (spue_f * total_oil * ph_stress * climate_impact) / (pen_score / 20)
        adhesion_index = 100 - (spue_index * 15) - (grease_drag * 12)

        # 8. AREA YIELD (The Cold Vacuum & Tannin Science)
        swelling = max(0, (self.ph - 4.2) * 2.45)
        climate_mod = 1.0 if climate == "Temperate" else 1.70
        base_yield = 94.0 + swelling + veg_fill_gain - astringency_loss - (total_oil * 1.15)
        
        if dry_method == "Air Drying":
            area_yield = base_yield - (self.thick * 0.45 * climate_mod)
        else: # Partial Vacuum
            temp_strict = (vac_temp - 25) / 35.0
            brace_effect = 1 - (veg_off * 0.04) # Tannin bracing
            striction_loss = (self.thick * 2.5 * (1 + temp_strict)) * (1 + (self.cr_offer * 0.20)) * brace_effect
            area_yield = base_yield - striction_loss - (2.6 * climate_mod)

        # 9. OUTPUT DICTIONARY
        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1),
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), "Punch": round(mech_punch, 2),
            "Barrier": round(core_barrier, 2), "Break": round(max(1, min(5, 5.6 - (pen_score/17) + (ph_stress*0.55))), 1),
            "Spue": round(min(5, spue_index), 2), "Adhesion": round(max(0, adhesion_index), 1),
            "Cloud": round(avg_cloud, 1), "Jump": temp_jump, "Swelling": round(swelling, 2), "Veg_Gain": round(veg_fill_gain, 2)
        }

# --- STREAMLIT UI: INDUSTRIAL CONSOLE ---
st.set_page_config(page_title="Platinum Master Twin v12.1", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v12.1)")

with st.sidebar:
    st.header("🌿 1. Tanning & Veg Fillers")
    veg = st.selectbox("Veg Type", list(VEG_SPECS.keys()))
    veg_off = st.slider("% Veg Offer", 0.0, 20.0, 5.0)
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.2)
    pickle_type = st.radio("Pickle Paradox", ["Equilibrium", "Chaser (Core Heavy)"])

    st.header("🥣 2. Triple-Oil Blend")
    o1 = st.selectbox("Oil A (Primary)", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer A", 0.0, 15.0, 6.0)
    o2 = st.selectbox("Oil B (Filler)", list(FATLIQUOR_SPECS.keys()), index=5) # Raw
    off2 = st.number_input("% Offer B", 0.0, 15.0, 2.0)
    o3 = st.selectbox("Oil C (Fixer)", list(FATLIQUOR_SPECS.keys()), index=4) # Ester
    off3 = st.number_input("% Offer C", 0.0, 15.0, 1.0)
    
    st.divider()
    syn = st.slider("Syntan (%)", 0.0, 15.0, 6.0)
    nsa = st.slider("NSA / Surfactant (%)", 0.0, 4.0, 1.0)

    st.header("🥁 3. Mechanical Physics")
    rpm = st.slider("RPM", 2, 22, 14)
    duration = st.slider("Process Time (min)", 30, 300, 120)
    furniture = st.selectbox("Drum Furniture", ["None", "Pegs", "Hybrid"], index=2)

    st.header("📐 4. Drying & Climate")
    dry_method = st.radio("Method", ["Air Drying", "Partial Vacuum"])
    vac_temp = st.slider("Vacuum Plate Temp (°C)", 25, 65, 30)
    temp_fat = st.slider("Fatliquor Temp (°C)", 35, 65, 55)
    temp_retan = st.slider("Hide Temp (°C)", 20, 45, 35)
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 2.4)
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE SIMULATION
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, veg_off, duration, 40, furniture, rpm, 3.5, 2000, temp_fat, temp_retan, vac_temp, dry_method, climate, pickle_type, True)

if res:
    # Top Level Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Area Yield", f"{res['Yield']}%", delta=f"{res['Veg_Gain']}% Fill")
    m2.metric("Adhesion Index", f"{res['Adhesion']}%")
    m3.metric("Spue Risk", res['Spue'])
    m4.metric("Core Strike", f"{res['Pen']}%")
    m5.metric("Grain Break", f"G{res['Break']}")

    st.divider()
    

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Internal Anatomical Profile")
        cr_grad = [0.7, 0.9, 1.5, 0.9, 0.7] if pickle_type == "Chaser (Core Heavy)" else [1.0, 1.0, 1.0, 1.0, 1.0]
        oil_grad = [1.0, 0.85, 0.4*(res['Pen']/100), 0.85, 1.0]
        st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'],
                                    'Chrome Profile': cr_grad, 'Oil Profile': oil_grad}).set_index('Layer'))
    with col_r:
        st.subheader("📉 Technical Verdict")
        if res['Adhesion'] < 65:
            st.error(f"🚨 **ADHESION CRITICAL:** Surface grease will likely cause finish peeling. Increase pH or mechanical strike.")
        if res['Spue'] > 2.0:
            st.warning(f"⚠️ **SPUE DANGER:** Batch Cloud Point ({res['Cloud']}°C) is unstable for this climate.")
        
        st.write(f"**Mechanical Work (Oomph):** {res['Oomph']} kJ")
        st.write(f"**Osmotic Swelling:** +{res['Swelling']}%")
        st.write(f"**Thermal Shock (Jump):** {res['Jump']}°C")
        st.caption(f"v12.1 Unified Platinum | Zeta: {res['Zeta']} | Punch: {res['Punch']}")
