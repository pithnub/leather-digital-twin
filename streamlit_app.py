import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: INDUSTRIAL KINETICS ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9, "desc": "High surface nourishment; emulsion size >1 micron."},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7, "desc": "Salt stable; superior core migration kinetics."},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "soft": 0.8, "desc": "Standard grain lubrication; moderate filling."},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "soft": 0.4, "desc": "Reactive polymer; high 'stand' but restricts fiber movement."},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8, "desc": "Electrolyte king; provides maximum area retention."},
    "Raw/Neutral Oil (Neatsfoot)": {"stability": 1, "pen": 0.2, "soft": 1.2, "desc": "Non-ionic; risk of grain crash without surfactant support."}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_offer = cr_offer

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_fat, vac_temp, dry_method, climate, pickle_type):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. FIBER SWELLING (pH Dependent)
        swelling_factor = max(0, (self.ph - 4.2) * 2.25)
        
        # 2. CHROME GRADIENT & CORE DAMS (Pickle Strategy)
        if pickle_type == "Chaser (Core Heavy)":
            eff_neutral_ph = self.ph + 0.45
            core_barrier = (self.cr_offer * 0.40) * (self.thick / 1.5)
            surface_drag, case_hardening = 0.50, 1.40
        else: # Equilibrium
            eff_neutral_ph = self.ph
            core_barrier = (self.cr_offer * 0.18)
            surface_drag, case_hardening = 1.30, 1.0

        # 3. ZETA POTENTIAL & ELECTRICAL DRAG
        ph_stress = math.exp(max(0, 5.2 - eff_neutral_ph)) 
        base_charge = (self.cr_offer * 20.0) + (ph_stress * 25.0)
        soup_masking = (syn * 13.0) + (nsa * 40.0) + {"None": 0, "Tara": 25, "Mimosa": -10, "Chestnut": -20}.get(veg, 0)
        eff_zeta = (base_charge * surface_drag) - soup_masking
        
        # 4. MECHANICAL ENERGY ENGINE
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_mod = {"None": 0.45, "Pegs": 1.15, "Hybrid": 1.55}.get(furniture, 1.15)
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * 0.6 * furn_mod) / 1000) * (duration / 60)
        mech_punch = (v_peripheral * furn_mod * (duration / 45)) / (self.thick + 0.5)
        
        # 5. PENETRATION LOGIC (Coupled Diffusion)
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        oil_mobility = 1.0 + ((temp_fat - 35) / 55.0)
        diffusion_res = (self.thick ** 2.5) * (1 + core_barrier) * case_hardening
        pen_score = 100 / (1 + ((eff_zeta * 0.035 * diffusion_res) / (mix_pen_base * mech_punch * oil_mobility + 0.1)))
        
        # 6. UPDATED AREA YIELD (Cold Vacuum vs Heat Shock)
        climate_mod = 1.0 if climate == "Temperate" else 1.6
        base_yield = 94.0 + swelling_factor - (total_offer * 1.0)
        
        if dry_method == "Air Drying":
            area_yield = base_yield - (self.thick * 0.4 * climate_mod)
            yield_note = "Maximum relaxation; zero mechanical compression."
        else: # Partial Vacuum
            # THE ADVANCED VACUUM LOGIC
            # Striction is heavily temperature dependent. 30C = Modern Tech. 60C = Traditional.
            temp_striction = (vac_temp - 25) / 35.0 # Scale 0 to 1
            striction_loss = (self.thick * 2.2 * (1 + temp_striction)) * (1 + (self.cr_offer * 0.15))
            area_yield = base_yield - striction_loss - (climate_mod * 2.0)
            yield_note = f"Mechanical Set at {vac_temp}°C. Striction index: {round(temp_striction,2)}"

        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1),
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), 
            "Punch": round(mech_punch, 2), "Barrier": round(core_barrier, 2),
            "Break": round(max(1, min(5, 5 - (pen_score/15) + (ph_stress*0.5))), 1),
            "Note": yield_note, "Swelling": round(swelling_factor, 2)
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v11.3", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v11.3)")

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
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.5)

    st.header("🥁 2. Mechanical Physics")
    furniture = st.radio("Furniture", ["None", "Pegs", "Hybrid"], index=1)
    rpm = st.slider("RPM", 2, 20, 14)
    duration = st.slider("Run Time", 30, 240, 120)

    st.header("📐 3. Advanced Drying Tech")
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    vac_temp = st.slider("Vacuum Plate Temp (°C)", 25, 65, 30) # The 'Cold Vacuum' Toggle
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 2.4)
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, 5.0, 0.5, "None", duration, 40, furniture, rpm, 3.5, 2000, 35, 55, dry_method, climate, pickle_type)

if res:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Core Strike", f"{res['Pen']}%")
    m2.metric("Area Yield", f"{res['Yield']}%")
    m3.metric("Fiber Swelling", f"+{res['Swelling']}%")
    m4.metric("Mechanical Work", f"{res['Oomph']} kJ")
    m5.metric("Grain Break", f"G{res['Break']}")

    st.divider()
    
    

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Internal Anatomical Scan")
        cr_grad = [0.7, 0.9, 1.4, 0.9, 0.7] if pickle_type == "Chaser (Core Heavy)" else [1.0, 1.0, 1.0, 1.0, 1.0]
        oil_grad = [1.0, 0.8, 0.4*(res['Pen']/100), 0.8, 1.0]
        st.area_chart(pd.DataFrame({'Layer': ['Grain', 'Upper Corium', 'Core', 'Lower Corium', 'Flesh'],
                                    'Chrome Profile': cr_grad, 'Oil Profile': oil_grad}).set_index('Layer'))
    with col_r:
        st.subheader("📉 Technical Verdict")
        st.write(f"**Yield Note:** {res['Note']}")
        if dry_method == "Partial Vacuum" and vac_temp <= 30:
            st.success("❄️ **ADVANCED DRYING:** Low-temperature vacuum detected. Minimizing striction loss.")
        elif dry_method == "Partial Vacuum" and vac_temp > 50:
            st.error("🔥 **HEAT SHOCK:** High vacuum temperature is inducing extreme striction.")
        
        if res['Pen'] < 60:
            st.error(f"🚨 **BARRIER:** Core Dam ({res['Barrier']}) is resisting strike.")

    st.caption(f"v11.3 Platinum | Zeta: {res['Zeta']} | Mech Punch: {res['Punch']}")
