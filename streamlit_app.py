import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: EMULSION DYNAMICS & CHEMISTRY ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9, "desc": "Large emulsions; surface-active lubrication."},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7, "desc": "Small emulsions; deep core migration kinetics."},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "soft": 0.8, "desc": "Standard grain lubrication; moderate filling."},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "soft": 0.4, "desc": "Polymer barrier; provides 'stand' but limits yield."},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8, "desc": "Electrolyte king; maximum area retention."},
    "Raw/Neutral Oil": {"stability": 1, "pen": 0.2, "soft": 1.2, "desc": "Non-ionic; risk of grain crash without NSA support."}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_offer = cr_offer

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_fat, temp_retan, vac_temp, dry_method, climate, pickle_type, is_wp):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. FIBER SWELLING (pH Dependent Area Gain)
        swelling_factor = max(0, (self.ph - 4.2) * 2.35)
        
        # 2. CHROME GRADIENT & CORE DAM (The G5 Culprit Logic)
        if pickle_type == "Chaser (Core Heavy)":
            eff_neutral_ph = self.ph + 0.45
            core_barrier = (self.cr_offer * 0.45) * (self.thick / 1.5)
            surface_drag, case_hardening = 0.50, 1.50
        else: # Equilibrium
            eff_neutral_ph = self.ph
            core_barrier = (self.cr_offer * 0.20)
            surface_drag, case_hardening = 1.35, 1.0

        # 3. ZETA POTENTIAL & ELECTRICAL DRAG
        ph_stress = math.exp(max(0, 5.2 - eff_neutral_ph)) 
        base_charge = (self.cr_offer * 21.0) + (ph_stress * 26.0)
        veg_mod = {"None": 0, "Tara": 25, "Mimosa": -10, "Chestnut": -22}.get(veg, 0)
        soup_masking = (syn * 15.0) + (nsa * 45.0) + veg_mod
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
        fixation_rate = 1.0 + (temp_jump * 0.06)

        # 6. PENETRATION KINETICS (Fighting the Core Dam)
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        diffusion_res = (self.thick ** 2.65) * (1 + core_barrier) * case_hardening * fixation_rate
        pen_score = 100 / (1 + ((eff_zeta * 0.04 * diffusion_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 7. AREA YIELD (The Cold Vacuum Science)
        climate_mod = 1.0 if climate == "Temperate" else 1.65
        base_yield = 94.0 + swelling_factor - (total_offer * 1.1)
        
        if dry_method == "Air Drying":
            area_yield = base_yield - (self.thick * 0.42 * climate_mod)
            yield_note = "Capillary Relaxation: Swelling gains preserved."
        else: # Partial Vacuum
            temp_striction = (vac_temp - 25) / 35.0 
            striction_loss = (self.thick * 2.4 * (1 + temp_striction)) * (1 + (self.cr_offer * 0.18))
            area_yield = base_yield - striction_loss - (climate_mod * 2.5)
            yield_note = f"Mechanical Set at {vac_temp}°C. Striction active."

        # 8. QUALITY INDICATORS
        vbi = (1.0 + (total_offer / 12)) * (1.35 if is_wp else 1.0)
        break_grade = max(1, min(5, 5.5 - (pen_score / 18) + (ph_stress * 0.5)))
        spue_risk = (ph_stress * 0.6) + (climate_mod * 0.5) if dry_method == "Air Drying" else 0.1

        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1), "VBI": round(vbi, 2),
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), "Punch": round(mech_punch, 2),
            "Barrier": round(core_barrier, 2), "Break": round(break_grade, 1), "Spue": round(spue_risk, 1),
            "Swelling": round(swelling_factor, 2), "Jump": temp_jump, "Note": yield_note, "Oil_Note": FATLIQUOR_SPECS[o1]['desc']
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v11.5", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v11.5)")

with st.sidebar:
    st.header("🥣 1. Recipe: Triple-Oil Blend")
    o1 = st.selectbox("Primary Oil", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 15.0, 6.0)
    o2 = st.selectbox("Secondary Oil", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 15.0, 2.0)
    o3 = st.selectbox("Functional Oil", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.number_input("% Offer (C)", 0.0, 15.0, 0.0)
    
    st.divider()
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    pickle_type = st.radio("Pickle Type", ["Equilibrium", "Chaser (Core Heavy)"])
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.2)
    syn = st.slider("Syntan (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA (%)", 0.0, 4.0, 1.0)
    veg = st.selectbox("Veg Type", ["None", "Tara", "Mimosa", "Chestnut"])

    st.header("🥁 2. Mechanical Physics")
    furniture = st.radio("Furniture", ["None", "Pegs", "Hybrid"], index=2)
    rpm = st.slider("RPM", 2, 22, 12)
    duration = st.slider("Run Time", 30, 300, 90)

    st.header("📐 3. Substrate & Drying")
    vac_temp = st.slider("Vacuum Plate Temp (°C)", 25, 65, 30)
    temp_fat = st.slider("Fatliquor Temp (°C)", 35, 65, 55)
    temp_retan = st.slider("Retan Temp (°C)", 20, 45, 35)
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 2.4)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, 40, furniture, rpm, 3.5, 2000, temp_fat, temp_retan, vac_temp, dry_method, climate, pickle_type, True)

if res:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Core Strike", f"{res['Pen']}%")
    m2.metric("Grain Break", f"G{res['Break']}")
    m3.metric("Area Yield", f"{res['Yield']}%")
    m4.metric("Osmotic Swelling", f"+{res['Swelling']}%")
    m5.metric("Mechanical Punch", res['Punch'])

    st.divider()
    

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Internal Structural Scan")
        cr_grad = [0.7, 0.9, 1.5, 0.9, 0.7] if pickle_type == "Chaser (Core Heavy)" else [1.0, 1.0, 1.0, 1.0, 1.0]
        oil_grad = [1.0, 0.8, 0.4*(res['Pen']/100), 0.8, 1.0]
        st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'],
                                    'Chrome Profile': cr_grad, 'Oil Profile': oil_grad}).set_index('Layer'))
    with col_r:
        st.subheader("📉 Technical Verdict")
        st.write(f"**Yield Note:** {res['Note']}")
        st.write(f"**VBI:** {res['VBI']} | **Spue Risk:** {res['Spue']}")
        if res['Jump'] > 20: st.warning(f"⚠️ **THERMAL JUMP:** {res['Jump']}°C shock detected. High fixation risk.")
        if res['Pen'] < 60:
            st.error(f"🚨 **CORE DAM:** Barrier ({res['Barrier']}) is winning. Break will be coarse.")
        else:
            st.success("✨ **Strike Through:** Mechanical punch has overcome the Chrome barrier.")

    st.caption(f"v11.5 Platinum Industrial | Effective Zeta: {res['Zeta']} | Oomph: {res['Oomph']} kJ")
