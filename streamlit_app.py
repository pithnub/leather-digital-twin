import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: THE TANNER'S ENCYCLOPEDIA ---
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

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, veg_off, 
                 duration, rpm, diam, width, load_kg, float_pct, furniture, 
                 temp_fat, temp_retan, vac_temp, dry_method, climate, pickle_type, is_wp):
        
        total_oil = off1 + off2 + off3
        if total_oil == 0: return None
        
        # 1. DRUM PHYSICS & MECHANICAL ENERGY
        drum_vol = math.pi * ((diam/2)**2) * width
        fill_pct = ((load_kg / 1000) / drum_vol) * 100
        # Fall efficiency peaks at 30-45% fill
        fall_efficiency = math.sin(math.radians(max(5, min(175, (fill_pct/100)*180))))
        
        v_periph = (math.pi * diam * rpm) / 60
        furn_mod = {"None": 0.45, "Pegs": 1.15, "Hybrid": 1.55}.get(furniture, 1.15)
        
        mech_punch = (v_periph * fall_efficiency * furn_mod * (duration / 45)) / (self.thick + 0.5)
        kinetic_oomph = (load_kg * 9.81 * (diam * 0.7) * fall_efficiency * (rpm * duration)) / 1000
        
        # 2. CHEMICAL BARRIERS & IONIC DRAG
        if pickle_type == "Chaser (Core Heavy)":
            eff_ph = self.ph + 0.45
            core_barrier = (self.cr_offer * 0.48) * (self.thick / 1.5)
            surface_drag, case_hard = 0.50, 1.55
        else:
            eff_ph = self.ph
            core_barrier = (self.cr_offer * 0.22)
            surface_drag, case_hard = 1.38, 1.0

        ph_stress = math.exp(max(0, 5.2 - eff_ph))
        base_charge = (self.cr_offer * 21.5) + (ph_stress * 27.0)
        soup_masking = (syn * 16.0) + (nsa * 48.0) + VEG_SPECS[veg]['zeta']
        eff_zeta = (base_charge * surface_drag) - soup_masking
        
        # 3. KINETIC PENETRATION
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        fixation_rate = 1.0 + (max(0, temp_fat - temp_retan) * 0.07)
        
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen']*off1) + (FATLIQUOR_SPECS[o2]['pen']*off2) + (FATLIQUOR_SPECS[o3]['pen']*off3)) / total_oil
        diff_res = (self.thick ** 2.70) * (1 + core_barrier) * case_hard * fixation_rate
        pen_score = 100 / (1 + ((eff_zeta * 0.042 * diff_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 4. QUALITY INDICATORS
        avg_cloud = ((FATLIQUOR_SPECS[o1]['cloud_point']*off1) + (FATLIQUOR_SPECS[o2]['cloud_point']*off2) + (FATLIQUOR_SPECS[o3]['cloud_point']*off3)) / total_oil
        spue_f = ((FATLIQUOR_SPECS[o1]['spue_f']*off1) + (FATLIQUOR_SPECS[o2]['spue_f']*off2) + (FATLIQUOR_SPECS[o3]['spue_f']*off3)) / total_oil
        grease_drag = ((FATLIQUOR_SPECS[o1]['grease_drag']*off1) + (FATLIQUOR_SPECS[o2]['grease_drag']*off2) + (FATLIQUOR_SPECS[o3]['grease_drag']*off3)) / total_oil
        
        climate_impact = 1.8 if climate == "Tropical" else 1.2
        spue_idx = (spue_f * total_oil * ph_stress * climate_impact) / (pen_score / 20)
        adhesion_idx = 100 - (spue_idx * 15) - (grease_drag * 12)
        
        # 5. AREA YIELD (Fixed VEG_SPECS call)
        swelling = max(0, (self.ph - 4.2) * 2.45)
        veg_gain = (veg_off * VEG_SPECS[veg]['fill']) * 0.28 if veg != "None" else 0
        astringency_hit = (veg_off * VEG_SPECS[veg]['astringency']) * 0.18 if self.ph < 5.0 else 0
        
        if dry_method == "Air Drying":
            yield_loss = self.thick * 0.45 * (1.7 if climate == "Tropical" else 1.0)
        else:
            temp_strict = (vac_temp - 25) / 35.0
            brace = 1 - (veg_off * 0.04)
            yield_loss = (self.thick * 2.5 * (1 + temp_strict) * (1 + self.cr_offer*0.20) * brace) + 2.6
            
        area_yield = 94.0 + swelling + veg_gain - astringency_hit - (total_oil * 1.15) - yield_loss

        return {
            "Yield": round(area_yield, 2), "Pen": round(min(100, pen_score), 1),
            "Spue": round(min(5, spue_idx), 2), "Adhesion": round(max(0, adhesion_idx), 1),
            "Punch": round(mech_punch, 2), "Fill": round(fill_pct, 1), "Fall": round(fall_efficiency * 100, 1),
            "Break": round(max(1, min(5, 5.6 - (pen_score/17) + (ph_stress*0.55))), 1),
            "Cloud": round(avg_cloud, 1), "Oomph": round(kinetic_oomph, 2), "Zeta": round(eff_zeta, 1)
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v12.4", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v12.4)")

with st.sidebar:
    st.header("🥁 1. Drum & Load Geometry")
    diam = st.slider("Drum Diameter (m)", 1.5, 4.5, 3.5)
    width = st.slider("Drum Width (m)", 1.0, 4.0, 3.0)
    load_kg = st.number_input("Load Weight (kg)", 500, 12000, 3000)
    rpm = st.slider("RPM", 2, 20, 12)
    duration = st.slider("Process Time (min)", 30, 360, 120)
    furniture = st.selectbox("Internal Furniture", ["None", "Pegs", "Hybrid"], index=2)

    st.header("🥣 2. Triple-Oil Recipe")
    o1 = st.selectbox("Oil A (Primary)", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer A", 0.0, 15.0, 6.0)
    o2 = st.selectbox("Oil B (Filler)", list(FATLIQUOR_SPECS.keys()), index=5)
    off2 = st.number_input("% Offer B", 0.0, 15.0, 2.0)
    o3 = st.selectbox("Oil C (Fixer)", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.number_input("% Offer C", 0.0, 15.0, 1.0)
    
    st.header("🧪 3. Tanning & pH")
    veg = st.selectbox("Veg Type", list(VEG_SPECS.keys()), index=1)
    veg_off = st.slider("% Veg Offer", 0.0, 20.0, 5.0)
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.2)
    pickle_type = st.radio("Pickle Paradox", ["Equilibrium", "Chaser (Core Heavy)"])

    st.header("📐 4. Drying Science")
    dry_method = st.radio("Method", ["Air Drying", "Partial Vacuum"])
    vac_temp = st.slider("Vacuum Plate Temp (°C)", 25, 65, 30)
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 2.4)
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, 5.0, 1.0, veg, veg_off, duration, rpm, diam, width, load_kg, 100, furniture, 55, 35, vac_temp, dry_method, climate, pickle_type, True)

if res:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Area Yield", f"{res['Yield']}%")
    m2.metric("Adhesion Index", f"{res['Adhesion']}%")
    m3.metric("Spue Risk", res['Spue'])
    m4.metric("Fall Efficiency", f"{res['Fall']}%")
    m5.metric("Core Strike", f"{res['Pen']}%")

    st.divider()
    

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Cross-Section Dynamics")
        oil_grad = [1.0, 0.85, 0.4*(res['Pen']/100), 0.85, 1.0]
        st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'],
                                    'Oil Distribution': oil_grad}).set_index('Layer'))
    with col_r:
        st.subheader("📉 Mechanical & Chemical Verdict")
        if res['Fill'] > 65: st.error(f"🚨 **DRUM OVERLOAD:** Fill is {res['Fill']}%. Punch is failing.")
        if res['Adhesion'] < 60: st.warning("⚠️ **FINISHING RISK:** Surface grease detected.")
        st.write(f"**Mechanical Work:** {res['Oomph']} kJ")
        st.write(f"**Grain Break:** G{res['Break']} | **Zeta:** {res['Zeta']}")
