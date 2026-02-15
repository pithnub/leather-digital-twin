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

        # 1. DRUM VOLUME & PHYSICS (CENTRIFUGAL FIX)
        drum_vol = math.pi * ((diam/2)**2) * width
        fill_pct = ((load_kg / 1000) / drum_vol) * 100
        
        # Froude Number Logic: At Critical RPM, gravity = centrifugal force (leather sticks)
        crit_rpm = 42.3 / math.sqrt(diam / 2)
        rpm_ratio = rpm / crit_rpm
        # Efficiency is a bell curve: sliding below 15% crit, pegging above 80% crit
        rpm_impact = math.exp(-0.5 * ((rpm_ratio - 0.35) / 0.15)**2) 
        
        base_fall = math.sin(math.radians(max(5, min(175, (fill_pct/100)*180))))
        fall_eff = base_fall * rpm_impact
        
        v_periph = (math.pi * diam * rpm) / 60
        furn_mod = {"None": 0.45, "Pegs": 1.15, "Hybrid": 1.55}.get(furniture, 1.15)

        # 2. MECHANICAL & THERMAL ENERGY
        mech_punch = (v_periph * fall_eff * furn_mod * (duration / 45)) / (self.thick + 0.5)
        kinetic_oomph = (load_kg * 9.81 * (diam * 0.7) * fall_eff * (rpm * duration)) / 1000
        temp_jump = abs(temp_fat - temp_retan)
        fixation_shock = 1.0 + (temp_jump * 0.085)
        oil_mobility = 1.0 + ((temp_fat - 35) / 60.0)

        # 3. CHEMICAL BARRIERS & IONIC DRAG
        base_charge = 12.0 - self.ph - (self.cr_offer * 0.5)
        soup_masking = (nsa * 0.4) + (syn * 0.25)
        veg_ast = VEG_SPECS[veg]['astringency']
        case_hard = 1.0 + (veg_off * veg_ast * 0.12)
        surface_drag = 1.0 + (is_wp * 0.8)
        core_barrier = (self.thick * 0.15) + (veg_off * 0.05)
        eff_zeta = (base_charge * surface_drag) - soup_masking

        # 4. KINETIC PENETRATION (CORE STRIKE)
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen']*off1) + (FATLIQUOR_SPECS[o2]['pen']*off2) + (FATLIQUOR_SPECS[o3]['pen']*off3)) / total_oil
        diff_res = (self.thick ** 2.70) * (1 + core_barrier) * case_hard * fixation_shock
        pen_score = 100 / (1 + ((eff_zeta * 0.042 * diff_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))

        # 5. QUALITY INDICATORS
        avg_cloud = ((FATLIQUOR_SPECS[o1]['cloud_point']*off1) + (FATLIQUOR_SPECS[o2]['cloud_point']*off2) + (FATLIQUOR_SPECS[o3]['cloud_point']*off3)) / total_oil
        spue_f = ((FATLIQUOR_SPECS[o1]['spue_f']*off1) + (FATLIQUOR_SPECS[o2]['spue_f']*off2) + (FATLIQUOR_SPECS[o3]['spue_f']*off3)) / total_oil
        grease_drag = ((FATLIQUOR_SPECS[o1]['grease_drag']*off1) + (FATLIQUOR_SPECS[o2]['grease_drag']*off2) + (FATLIQUOR_SPECS[o3]['grease_drag']*off3)) / total_oil

        climate_impact = 1.8 if climate == "Tropical" else 1.2
        ph_stress = max(0, 4.0 - self.ph)
        spue_idx = (spue_f * total_oil * ph_stress * climate_impact) / (pen_score / 20)
        vbi = (grease_drag * (1.5 if pickle_type == "Chaser (Core Heavy)" else 1.0)) * (1 + (self.thick/10))

        if dry_method == "Air Drying":
            yield_loss = self.thick * 0.45 * (1.7 if climate == "Tropical" else 1.0)
        else: # Vacuum logic
            temp_strict = (vac_temp - 25) / 35.0
            brace = 1 - (veg_off * 0.04)
            yield_loss = (self.thick * 2.5 * (1 + temp_strict) * (1 + self.cr_offer*0.20) * brace) + 2.6

        return {
            "Pen": round(pen_score, 1), "Spue": round(spue_idx, 2), "Yield": round(yield_loss, 1),
            "Punch": round(mech_punch, 2), "Fill": round(fill_pct, 1), "Fall": round(fall_eff * 100, 1),
            "Break": round(max(1, min(5, 5.6 - (pen_score/17) + (ph_stress*0.55))), 1),
            "Cloud": round(avg_cloud, 1), "Oomph": round(kinetic_oomph, 2), "Zeta": round(eff_zeta, 1),
            "Jump": round(temp_jump, 1), "VBI": round(vbi, 2)
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v12.9", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v12.9)")



with st.sidebar:
    st.header("🥁 1. Drum & Load")
    diam = st.slider("Diameter (m)", 1.5, 4.5, 3.5)
    width = st.slider("Width (m)", 1.0, 4.0, 3.0)
    load_kg = st.number_input("Load Weight (kg)", 500, 12000, 3000)
    rpm = st.slider("RPM", 2, 24, 12)
    furniture = st.selectbox("Furniture", ["None", "Pegs", "Hybrid"], index=2)

    st.header("🌡️ 2. Thermal Transition")
    temp_retan = st.slider("Retanning Temp (°C)", 20, 60, 35)
    temp_fat = st.slider("Fatliquor Temp (°C)", 35, 65, 55)

    st.header("🥣 3. Triple-Oil Recipe")
    o1 = st.selectbox("Oil A", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.slider("Offer A (%)", 0.0, 15.0, 4.0)
    o2 = st.selectbox("Oil B", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.slider("Offer B (%)", 0.0, 15.0, 2.0)
    o3 = st.selectbox("Oil C", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.slider("Offer C (%)", 0.0, 10.0, 1.0)

    st.header("🧪 4. Chemistry & pH")
    ph_val = st.slider("Final Float pH", 3.0, 6.0, 3.8)
    thick = st.slider("Hide Thickness (mm)", 0.8, 6.0, 2.2)
    cr_offer = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    veg = st.selectbox("Vegetable Extract", list(VEG_SPECS.keys()))
    veg_off = st.slider("Veg Offer (%)", 0.0, 15.0, 0.0)
    syn = st.slider("Syntan Offer (%)", 0.0, 10.0, 3.0)
    nsa = st.slider("Dispersant/NSA (%)", 0.0, 4.0, 1.0)
    pickle_type = st.radio("Pickle/Basification", ["Standard", "Chaser (Core Heavy)"])
    is_wp = st.checkbox("Waterproof Process?")

    st.header("⏱️ 5. Process & Climate")
    duration = st.number_input("Duration (mins)", 30, 240, 60)
    dry_method = st.selectbox("Drying Method", ["Air Drying", "Vacuum Drying"])
    vac_temp = st.slider("Vacuum Plate Temp (°C)", 25, 80, 45)
    climate = st.selectbox("Target Climate", ["Temperate", "Tropical"])

# Execution
twin = PlatinumIndustrialTwin(thick, cr_offer, ph_val)
res = twin.simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, veg_off, duration, rpm, diam, width, load_kg, 100, furniture, temp_fat, temp_retan, vac_temp, dry_method, climate, pickle_type, is_wp)

if res:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Internal Anatomical Scan")
        oil_grad = [1.0, 0.85, 0.4*(res['Pen']/100), 0.85, 1.0]
        st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'], 'Oil Profile': oil_grad}).set_index('Layer'))
    with col_r:
        st.subheader("📉 Technical Verdict")
        if res['Jump'] > 15: st.error(f"🚨 **THERMAL SHOCK:** {res['Jump']}°C delta is crashing oil too fast.")
        if res['Fill'] > 65: st.warning(f"⚠️ **OVERLOAD:** Drum fill ({res['Fill']}%) prevents the 'fall' punch.")
        if res['Fall'] < 10: st.error(f"🚨 **ZERO FALL:** RPM ({rpm}) is causing pegging or sliding. No punch.")
        st.write(f"**VBI:** {res['VBI']} | **Zeta Potential:** {res['Zeta']}")
        st.write(f"**Mechanical Work:** {res['Oomph']} kJ | **Fall Eff:** {res['Fall']}%")

    st.divider()
    cols = st.columns(4)
    cols[0].metric("Penetration (Core %)", f"{res['Pen']}%")
    cols[1].metric("Spue Risk Index", res['Spue'])
    cols[2].metric("Estimated Break (1-5)", res['Break'])
    cols[3].metric("Yield Loss (%)", f"{res['Yield']}%")
