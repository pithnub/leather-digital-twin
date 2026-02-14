import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: INDUSTRIAL KINETICS ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "soft": 0.4},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8},
    "Raw/Neutral Oil": {"stability": 1, "pen": 0.2, "soft": 1.2}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_offer = cr_offer

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_retan, temp_fat, dry_method, climate, pickle_type, is_wp):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. THE FIBER SWELLING LOGIC (pH Impact on Area)
        # As pH moves toward 6.5, osmotic swelling increases, potentially 'opening' area.
        swelling_factor = (self.ph - 4.0) * 1.85 
        
        # 2. CHROME GRADIENT & CORE DAMS
        if pickle_type == "Chaser (Core Heavy)":
            eff_neutral_ph = self.ph + 0.4
            core_barrier = (self.cr_offer * 0.35) * (self.thick / 1.5)
            surface_drag, case_hardening = 0.55, 1.3
        else:
            eff_neutral_ph = self.ph
            core_barrier = (self.cr_offer * 0.15)
            surface_drag, case_hardening = 1.35, 1.0

        # 3. ELECTRICAL DRAG
        ph_stress = math.exp(max(0, 5.2 - eff_neutral_ph)) 
        base_charge = (self.cr_offer * 19.0) + (ph_stress * 23.0)
        soup_masking = (syn * 12.0) + (nsa * 35.0) + {"None": 0, "Tara": 25, "Mimosa": -8, "Chestnut": -15}.get(veg, 0)
        eff_zeta = (base_charge * surface_drag) - soup_masking
        
        # 4. MECHANICAL & THERMAL ENGINE
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_mod = {"None (Smooth)": 0.45, "Pegs or Shelves": 1.15, "Both (Hybrid)": 1.55}.get(furniture, 1.0)
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * 0.6 * furn_mod) / 1000) * (duration / 60)
        mech_punch = (v_peripheral * furn_mod * (duration / 45)) / (self.thick + 0.5)
        
        # 5. PENETRATION (Coupled Logic)
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        fix_rate = 1.0 + (max(0, temp_fat - temp_retan) * 0.05)
        
        diffusion_res = (self.thick ** 2.4) * (1 + core_barrier) * case_hardening * fix_rate
        pen_score = 100 / (1 + ((eff_zeta * 0.03 * diffusion_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 6. UPDATED AREA YIELD (Swelling vs Striction)
        climate_mod = 1.0 if climate == "Temperate" else 1.5
        base_yield = 95.0 + swelling_factor - (total_offer * 0.8)
        
        if dry_method == "Air Drying":
            area_yield = base_yield - (self.thick * 0.35 * climate_mod)
            yield_note = "Fiber Relaxation: Maximum area gain from swelling preserved."
        else: # Partial Vacuum
            # Striction kills the gain from swelling
            striction_loss = (self.thick * 1.8) * (1 + (self.cr_offer * 0.1))
            area_yield = base_yield - striction_loss - (climate_mod * 2.0)
            yield_note = "Grain Setting (Striction): Vacuum 'sets' the grain but compresses fibers."

        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1),
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), 
            "Punch": round(mech_punch, 2), "Barrier": round(core_barrier, 2),
            "Break": round(max(1, min(5, 5 - (pen_score/18) + (ph_stress*0.5))), 1),
            "Note": yield_note, "Swelling": round(swelling_factor, 2)
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v11.1", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v11.1)")

with st.sidebar:
    st.header("🥣 1. Recipe: Triple-Oil Blend")
    o1 = st.selectbox("Primary Oil", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 15.0, 6.0)
    o2 = st.selectbox("Secondary Oil", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 15.0, 2.0)
    o3 = st.selectbox("Functional Oil", list(FATLIQUOR_SPECS.keys()), index=4)
    off3 = st.number_input("% Offer (C)", 0.0, 15.0, 0.0)
    
    st.header("🧪 2. Chemical Modifiers")
    cr = st.slider("Chrome Offer (%)", 0.0, 8.0, 4.5)
    pickle_type = st.radio("Pickle Type", ["Equilibrium", "Chaser (Core Heavy)"])
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.5) # Increased default
    syn = st.slider("Syntan (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA (%)", 0.0, 3.0, 0.5)

    st.header("🥁 3. Mechanical Physics")
    furniture = st.radio("Furniture", ["None (Smooth)", "Pegs or Shelves", "Both (Hybrid)"], index=1)
    duration = st.slider("Run Time", 30, 240, 120)
    rpm = st.slider("RPM", 2, 20, 12)
    diameter = st.number_input("Diameter (m)", 1.5, 5.0, 3.5)
    weight = st.number_input("Load (kg)", 100, 5000, 2000)

    st.header("📐 4. Thermal & Drying")
    temp_fat = st.slider("Fatliquor Temp (°C)", 35, 65, 50)
    temp_retan = st.slider("Hide Temp (°C)", 20, 45, 30)
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 2.4)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, "None", duration, 40, furniture, rpm, diameter, weight, temp_retan, temp_fat, dry_method, climate, pickle_type, True)

if res:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Core Strike", f"{res['Pen']}%")
    m2.metric("Area Yield", f"{res['Yield']}%")
    m3.metric("Osmotic Swelling", f"+{res['Swelling']}%")
    m4.metric("Mechanical Work", f"{res['Oomph']} kJ")
    m5.metric("Grain Break", f"G{res['Break']}")

    st.divider()
    

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Anatomical Profile")
        cr_grad = [0.7, 0.9, 1.4, 0.9, 0.7] if pickle_type == "Chaser (Core Heavy)" else [1.0, 1.0, 1.0, 1.0, 1.0]
        oil_grad = [1.0, 0.8, 0.3*(res['Pen']/100), 0.8, 1.0]
        st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'],
                                    'Chrome Profile': cr_grad, 'Oil Profile': oil_grad}).set_index('Layer'))
    with col_r:
        st.subheader("📉 Process Verdict")
        st.write(f"**Yield Note:** {res['Note']}")
        if dry_method == "Partial Vacuum":
            st.warning("⚠️ **STRICTION RISK:** Vacuum setting is counteracting pH-induced area gains.")
        if res['Pen'] < 60:
            st.error(f"🚨 **BARRIER:** Core Dam ({res['Barrier']}) is resisting strike.")

    st.caption(f"v11.1 Platinum | Zeta: {res['Zeta']} | Mech Punch: {res['Punch']}")
