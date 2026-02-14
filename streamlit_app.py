import streamlit as st
import math
import pandas as pd

# --- KNOWLEDGE BASE: INDUSTRIAL CHEMISTRY ---
FATLIQUOR_SPECS = {
    "Sulphated Fish Oil": {"stability": 2, "pen": 0.4, "soft": 0.9, "desc": "Surface-active; traditional nourishment."},
    "Sulphited Fish Oil": {"stability": 8, "pen": 0.9, "soft": 0.7, "desc": "Deep penetration; salt & acid stable."},
    "Sulphated Vegetable Oil": {"stability": 3, "pen": 0.5, "soft": 0.8, "desc": "Soft grain lubricity; standard performance."},
    "Synthetic Waterproofing Oil": {"stability": 6, "pen": 0.7, "soft": 0.4, "desc": "Polymer barrier; high stand, lower yield."},
    "Phosphoric Ester": {"stability": 9, "pen": 0.8, "soft": 0.8, "desc": "Electrolyte stable; maximum area retention."},
    "Raw/Neutral Oil (Neatsfoot)": {"stability": 1, "pen": 0.2, "soft": 1.2, "desc": "High crash risk; requires high NSA levels."}
}

class PlatinumIndustrialTwin:
    def __init__(self, thick, cr_offer, ph_val):
        self.thick = thick
        self.ph = ph_val
        self.cr_sat = min(1.0, cr_offer / 3.0)

    def simulate(self, o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, load_factor, furniture, rpm, diameter, weight, temp_fat, dry_method, climate, is_wp):
        total_offer = off1 + off2 + off3
        if total_offer == 0: return None
        
        # 1. ELECTRICAL DRAG & ZETA POTENTIAL (Restored Sensitivity)
        # Below pH 5.0, the "Electrical Wall" becomes much harder to penetrate.
        veg_map = {"None": 0, "Tara": 25, "Mimosa": -6, "Chestnut": -12}
        ph_stress = math.exp(max(0, 5.2 - self.ph)) 
        base_charge = (self.cr_sat * 100) + (ph_stress * 20)
        soup_masking = (syn * 12) + (nsa * 30) + veg_map.get(veg, 0)
        eff_zeta = base_charge - soup_masking
        
        # 2. MECHANICAL ENERGY (Full Physics)
        v_peripheral = (math.pi * diameter * rpm) / 60
        furn_map = {"None (Smooth)": 0.45, "Pegs or Shelves": 1.15, "Both (Hybrid)": 1.55}
        furn_mod = furn_map.get(furniture, 1.0)
        drop_mod = max(0.1, 1.0 - ((load_factor - 40) / 100))
        kinetic_oomph = v_peripheral * ((weight * 9.81 * (diameter * 0.75) * drop_mod * furn_mod) / 1000) * (duration / 60)
        
        # 3. CHEMICAL MIXTURE & THERMAL MOBILITY
        mix_stability = ((FATLIQUOR_SPECS[o1]['stability'] * off1) + (FATLIQUOR_SPECS[o2]['stability'] * off2) + (FATLIQUOR_SPECS[o3]['stability'] * off3)) / total_offer
        mix_pen_base = ((FATLIQUOR_SPECS[o1]['pen'] * off1) + (FATLIQUOR_SPECS[o2]['pen'] * off2) + (FATLIQUOR_SPECS[o3]['pen'] * off3)) / total_offer
        mix_soft = ((FATLIQUOR_SPECS[o1]['soft'] * off1) + (FATLIQUOR_SPECS[o2]['soft'] * off2) + (FATLIQUOR_SPECS[o3]['soft'] * off3)) / total_offer
        
        # 4. PENETRATION (Fick's Second Law with pH wall)
        diffusion_path = self.thick ** 2 
        pen_res = (max(0, eff_zeta) * 0.02 * diffusion_path * (1.1 if is_wp else 1.0))
        pen_score = 100 / (1 + (pen_res / (mix_pen_base * kinetic_oomph + 0.1)))
        
        # 5. AREA RETENTION & DRYING (Method Divergence Fix)
        climate_res = 1.0 if climate == "Temperate" else 1.4
        base_yield = 100 - (total_offer * 1.2) # General shrinkage from oil loading
        
        if dry_method == "Air Drying":
            # Fiber relaxation improves area yield
            area_yield = base_yield - (self.thick * 0.4 * climate_res)
            method_desc = "Natural capillary evaporation. High fiber relaxation."
            advice = "Safe for high-area yield; risk of salt spue in high humidity."
        else: # Partial Vacuum
            # Pressure and heat cause striction (shrinkage)
            # High pH + Vacuum = Grain darkening and high area loss
            striction_mod = 1.8 if self.ph > 5.5 else 1.2
            area_yield = base_yield - (self.thick * 1.4 * striction_mod * climate_res)
            method_desc = "Mechanical moisture extraction. Oil migration to grain."
            advice = "Risk of grain darkening; strictly monitor vacuum duration."

        # 6. QUALITY INDICATORS
        break_val = max(1.0, min(5.0, 5 - (pen_score / 25) + (ph_stress * 0.4)))
        
        return {
            "Zeta": round(eff_zeta, 1), "Pen": round(min(100, pen_score), 1), 
            "Yield": round(area_yield, 2), "Oomph": round(kinetic_oomph, 2), 
            "Break": round(break_val, 1), "Dry_Note": method_desc, 
            "Advice": advice, "Oil_Note": FATLIQUOR_SPECS[o1]['desc']
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Platinum Master Twin v10.4", layout="wide")
st.title("🛡️ Platinum Wet-End Digital Twin (v10.4)")

with st.sidebar:
    st.header("🥣 1. Recipe & Auxiliaries")
    o1 = st.selectbox("Primary Oil", list(FATLIQUOR_SPECS.keys()), index=1)
    off1 = st.number_input("% Offer (A)", 0.0, 10.0, 4.0)
    o2 = st.selectbox("Secondary Oil", list(FATLIQUOR_SPECS.keys()), index=0)
    off2 = st.number_input("% Offer (B)", 0.0, 10.0, 2.0)
    o3 = st.selectbox("Stability/WP Oil", list(FATLIQUOR_SPECS.keys()), index=3)
    off3 = st.number_input("% Offer (C)", 0.0, 10.0, 0.0)
    
    st.header("🧪 2. Chemical Modifiers")
    syn = st.slider("Syntan (%)", 0.0, 15.0, 5.0)
    nsa = st.slider("NSA / Surfactant (%)", 0.0, 3.0, 0.5)
    veg = st.selectbox("Veg Type", ["None", "Tara", "Mimosa", "Chestnut"])
    cr = st.slider("Chrome (%)", 0.0, 8.0, 4.5)

    st.header("🥁 3. Mechanical Controls")
    furniture = st.radio("Mechanical Furniture", ["None (Smooth)", "Pegs or Shelves", "Both (Hybrid)"], index=1)
    duration = st.slider("Run Time (min)", 30, 240, 90)
    rpm = st.slider("RPM", 2, 20, 12)
    diameter = st.number_input("Drum Diameter (m)", 1.5, 5.0, 3.0)
    weight = st.number_input("Load Weight (kg)", 100, 5000, 1000)

    st.header("📐 4. Substrate & Drying")
    thick = st.number_input("Thickness (mm)", 0.5, 6.0, 1.6)
    ph = st.slider("Neutralization pH", 4.0, 6.5, 5.5)
    dry_method = st.radio("Drying Method", ["Air Drying", "Partial Vacuum"])
    climate = st.radio("Climate Zone", ["Temperate", "Tropical"])
    is_wp = st.checkbox("Waterproofing Logic Active", value=True)

# EXECUTE
res = PlatinumIndustrialTwin(thick, cr, ph).simulate(o1, off1, o2, off2, o3, off3, syn, nsa, veg, duration, 40, furniture, rpm, diameter, weight, 55, dry_method, climate, is_wp)

if res:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Core Penetration", f"{res['Pen']}%")
    c2.metric("Area Yield Retention", f"{res['Yield']}%")
    c3.metric("Mechanical Work", f"{res['Oomph']} kJ")
    c4.metric("Grain Break", f"G{res['Break']}")

    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🥁 Strike-Through Analysis")
        if res['Pen'] < 50: st.error(f"🚨 **FIXATION CRASH:** Zeta Potential ({res['Zeta']}) too high for penetration.")
        else: st.success(f"✨ **Strike achieved.** Zeta Potential balanced at {res['Zeta']}.")
        
        st.info(f"**Oil Note:** {res['Oil_Note']}")

    with col_r:
        st.subheader("💨 Drying & Yield")
        st.write(f"**Method:** {res['Dry_Note']}")
        st.write(f"**Advice:** {res['Advice']}")
        if res['Yield'] < 85:
            st.warning("⚠️ **High Striction:** Significant area loss due to drying method/thickness.")
