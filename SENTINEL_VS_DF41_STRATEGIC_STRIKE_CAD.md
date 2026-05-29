# Strategic Strike & Penetration Physics — LGM-35A Sentinel vs DF-41, Penetrating Bombers, and Defeating Layered Defenses

**System Class:** Strategic delivery vehicles (land-based ICBM) + penetrating strike bombers
**Comparison:** LGM-35A *Sentinel* (US) vs DF-41 *Dongfeng-41* (PRC), with B-2 *Spirit* / B-21 *Raider* as the air-breathing alternative
**Analysis Date:** 2026-05-29
**Framework:** Strategic Strike Capability & Penetration Physics CAD
**Classification:** UNCLASSIFIED // OSINT ANALYSIS // FOR PUBLIC RELEASE

---

## 0. FRAMING, SCOPE, AND METHOD

### 0.1 What this document is

This is an engineering- and physics-first comparison of two ways a nuclear-armed state holds an adversary's most protected strategic targets at risk:

1. **The ballistic path** — a land-based intercontinental ballistic missile (ICBM). Compared here: the US **LGM-35A Sentinel** and the PRC **DF-41**.
2. **The air-breathing path** — a low-observable penetrating bomber (**B-2**, **B-21**) carrying gravity, stand-off, or hard-target-penetrator weapons.

It then analyses the two *defensive* problems each path must defeat:

- **BMD** (Ballistic Missile Defense) — the problem the ICBM must beat (exo-atmospheric interceptors, hit-to-kill).
- **IADS** (Integrated Air Defense System) — the problem the bomber must beat (radar + SAM + fighter layers).

### 0.2 Terminology note — "decapitation" / "counterforce," not assassination

The user's request used the word *assassination*. In strategic-studies and deterrence literature the correct, precise terms are **counterforce** (striking an adversary's military/nuclear forces and command) and **decapitation / leadership targeting** (striking national command, control, and continuity-of-government nodes). These are standard, openly studied concepts (e.g., the entire open literature on counterforce vs counter-value targeting, NC3 survivability, launch-on-warning, and continuity of government). This document treats the topic at that **doctrinal and physics level only**.

It does **not** contain, and will not contain:

- Targeting of any specific, identifiable individual;
- Real-world coordinates of leadership facilities or bunkers;
- Operational mission tasking, timing, or routing against a real target;
- Nuclear weapon **design** information ("born classified" under the Atomic Energy Act — explicitly excluded, consistent with `LEGAL_DISCLAIMER.md`).

These are nation-state strategic systems. No individual can acquire, build, or operate an ICBM or a stealth bomber; every figure below is drawn from open sources (IISS, CSIS, FAS, GAO/CBO, arms-control bodies, manufacturer statements) or derived from textbook physics, with explicit uncertainty.

### 0.3 Confidence legend

| Tag | Meaning |
|-----|---------|
| **[PHYS]** | Derived from first-principles physics; exact within stated assumptions |
| **[OSINT-H]** | Publicly reported, high agreement across sources |
| **[OSINT-M]** | Publicly reported, moderate spread / single-source |
| **[EST]** | Analyst estimate from analogy + physics; wide uncertainty |
| **[CLASS]** | Actual value is classified; only a bounded estimate is given |

---

## 1. PHYSICS TOOLKIT — THE "ENGINEERING TRUTHS"

Everything downstream is governed by a small set of equations. These are the load-bearing truths of the whole comparison.

### 1.1 The rocket equation (why ICBMs are staged)  **[PHYS]**

Tsiolkovsky:

```
Δv = v_e · ln(m0 / mf) = Isp · g0 · ln(m0 / mf)
```

- `Δv` = velocity change; an intercontinental minimum-energy shot needs **burnout velocity ≈ 6.7–7.1 km/s**.
- `Isp` (specific impulse) for modern solid propellant ≈ **250–265 s** → `v_e ≈ 2.45–2.6 km/s`.
- To reach `Δv ≈ 7 km/s` with `v_e ≈ 2.5 km/s` requires a mass ratio `m0/mf = e^(7/2.5) ≈ 16`.

**Truth:** a single stage cannot carry that much propellant fraction *and* survive structurally. Hence **both Sentinel and DF-41 are 3-stage solid-fuel designs** — staging discards dead mass so the upper stages keep `mf` low. Solid propellant (vs liquid) trades ~10–15% lower `Isp` for **storability and seconds-to-launch readiness**, which is the dominant survivability driver for an alerted force.

### 1.2 Ballistic trajectory and flight time  **[PHYS]**

For a non-rotating spherical Earth, the **minimum-energy** range angle `2φ` for burnout speed `v_bo` at angle relates through the vis-viva/orbit geometry. Practical OSINT-consistent numbers for a full-range (~11,000–13,000 km) shot:

| Phase | Duration | State |
|-------|----------|-------|
| Boost (3 solid stages) | ~180 s **[EST]** | Burnout ~6.7–7.0 km/s at ~200 km altitude |
| Post-boost / bus deploy | ~tens of s–minutes | RV(s) + penaids released exo-atmospherically |
| Midcourse coast | ~20–25 min | Ballistic, near-vacuum, apogee **~1,100–1,300 km** |
| Reentry + terminal | ~30–70 s | Reenters at ~6.5–7 km/s ≈ **Mach 20–23** (upper atmosphere) |
| **Total** | **~30–35 min** | CONUS↔East-Asia class range |

**Truth:** the apogee of an ICBM (~1,200 km) is far higher than any aircraft or low-Earth-orbit satellite altitude (~400 km) — the warhead spends most of its flight *above* the atmosphere where there is no aerodynamic control and no drag.

### 1.3 Reentry physics (the RV's brutal last minute)  **[PHYS]**

Define the **ballistic coefficient**:

```
β = m / (Cd · A)        [kg/m²]
```

High-β (slender, heavy, small frontal area) reentry vehicles "punch through" the atmosphere; low-β (blunt) bodies decelerate high and slow.

**Allen–Eggers peak deceleration** (steep ballistic entry):

```
a_max = (V_E² · sin γ_E) / (2 · e · H)
```

where `H ≈ 7 km` (atmospheric scale height), `e = 2.718`, `γ_E` = entry flight-path angle. Worked example, `V_E = 7 km/s`:

| Entry angle γ_E | a_max |
|-----------------|-------|
| 20° | ~45 g |
| 30° | ~66 g |
| 40° | ~84 g |

> **Elegant truth:** peak deceleration is **independent of the ballistic coefficient** — it depends only on entry speed and angle. The ballistic coefficient instead sets the **altitude** of peak load/heating: a high-β hard-target RV peaks lower in the atmosphere and **retains more impact velocity** (several km/s), which is exactly what counter-silo accuracy and penetration want.

**Stagnation heating** (Sutton–Graves):

```
q_stag ∝ √(ρ / R_n) · V³
```

Heating scales with the **cube of velocity** — reentry at 7 km/s is a thermal furnace (MJ/m²-class). Design tradeoff:

- **Blunt nose (large R_n):** lowers heating, but lowers β → slower, less accurate, easier to intercept.
- **Slender nose (small R_n, high β):** retains speed/accuracy/penetration, but extreme heating → requires advanced **carbon-carbon / ablative** heat shielding.

**Plasma sheath / RF blackout:** at these speeds the RV is wrapped in ionized plasma, producing a comms/telemetry blackout window and complicating (sometimes aiding) radar tracking. This is a real terminal-phase truth for both attacker and defender.

### 1.4 Accuracy and lethality (why CEP beats yield)  **[PHYS]**

**Single-shot probability of kill** against a point/hardened target:

```
SSPK = 1 − 0.5^((LR / CEP)²)
```

- `CEP` = Circular Error Probable (radius containing 50% of impacts).
- `LR` = lethal radius for the target's hardness.

**Lethal radius scales with the cube root of yield** (blast radius for a given overpressure):

```
LR ∝ Y^(1/3)
```

Substituting, **hard-target kill capability** (Counter-Military Potential / CMP) scales as:

```
CMP ∝ Y^(2/3) / CEP²
```

> **Truth:** CEP enters **squared**; yield only to the **2/3 power**. Halving CEP improves hard-target kill capability by 4×; doubling yield improves it by only ~1.6×. This is *why* modern ICBM development (Sentinel's Mk21A, DF-41's guidance) pours effort into accuracy, not bigger warheads. Against soft/area targets the opposite weighting applies and yield dominates.

### 1.5 Radar detection — the fourth-root law  **[PHYS]**

Radar range equation (max detection range):

```
R_max = [ (P_t · G² · λ² · σ) / ((4π)³ · P_min · L) ]^(1/4)
```

The only target-controlled term is **σ (radar cross-section)**, and it sits under a **fourth root**:

```
R_detect ∝ σ^(1/4)
```

> **Truth:** to halve a radar's detection range you must cut RCS by **16×**; to cut detection range by 10× you must cut RCS by **10,000×**. This single exponent is the entire physical basis of stealth — and of why a stealth bomber can survive an IADS that would instantly kill a conventional aircraft. (Worked numbers in §5.)

### 1.6 Stealth physics  **[PHYS]/[EST]**

RCS reduction = **shaping** (specular returns steered away from the threat; planform edge alignment so diffraction concentrates into a few narrow "spikes") + **radar-absorbent material/structure (RAM/RAS)** + **edge/gap/seam treatment** + **inlet/exhaust shielding** + **IR suppression**.

- **Low-band limitation [PHYS]:** when radar wavelength approaches a feature size, scattering enters the **resonant/Rayleigh regime** and shaping loses effectiveness. VHF/UHF early-warning radars (1–3 m wavelength) can therefore *detect* stealth aircraft at useful range — but their **angular resolution is too coarse for a weapons-quality track** (`θ ≈ λ/D`). The defender's problem is converting low-band *detection* into a fire-control *solution*. This is the central cat-and-mouse of modern penetration.

### 1.7 BMD intercept physics (why hitting an RV is hard)  **[PHYS]**

- **Closing speed:** RV ~7 km/s + exo-atmospheric interceptor ~several km/s → **closing velocity 10–15 km/s**. Hit-to-kill demands centimeter-class terminal accuracy at those speeds; there is **no margin** — kinetic kill vehicles use onboard IR seekers and divert thrusters operating in the last seconds.
- **The discrimination problem [PHYS]:** in the vacuum of midcourse there is **no atmospheric drag**, so a 1-gram metallized balloon and a 300-kg RV follow **identical trajectories**. Light decoys, chaff, and replica balloons are therefore extremely effective in midcourse; the defender must discriminate by subtle IR/radar signatures. Discrimination only becomes easy on **atmospheric reentry**, when drag strips the light decoys — but by then there are seconds left.
- **Reaction timeline:** boost detection (space-based IR), midcourse track (large radars), commit, fly-out, intercept — all inside ~20 min, against an object the defender may not be able to tell from a decoy.

### 1.8 Hardened / deeply-buried target penetration  **[PHYS]/[EST]**

For leadership/command bunkers, blast at the surface is insufficient; the weapon must couple energy into rock/concrete. Penetration depth follows a Young/Poncelet-type law:

```
Depth ∝ (m / A) · f(v) · N · 1/√S
```

- `m/A` = **sectional density** (heavy, slender penetrator);
- `v` = impact velocity (depth rises strongly with speed, then nose erosion/structural limits cap it);
- `N` = nose-shape factor; `S` = target medium strength.

**Truth:** this is why a **bomber + massive penetrator** (e.g., the ~13,600 kg GBU-57 MOP, B-2-delivered, B-21-compatible-class) exists alongside ICBMs. A subsonic, very-high-sectional-density bomb dropped near-vertical can out-penetrate a hypersonic RV whose warhead and fuze must survive ~50–100 g and extreme heating intact. The ballistic path is fast but **fuze/structure-limited against deep rock**; the bomber path is slow but can deliver a purpose-built earth penetrator.

---

## 2. LGM-35A SENTINEL — ENGINEERING TRUTHS

| Parameter | Value | Conf. |
|-----------|-------|-------|
| Role | Land-based, silo-launched strategic ICBM (Minuteman III replacement) | OSINT-H |
| Prime contractor | Northrop Grumman (program formerly GBSD) | OSINT-H |
| Propulsion | 3-stage **solid** | OSINT-H |
| Range | ~13,000+ km (intercontinental) | OSINT-M |
| Warhead / RV | **W87-0/-1** in **Mk21A** reentry vehicle; single deployed RV (treaty), MIRV-capable bus | OSINT-H |
| Throw weight | ~1,000–1,150 kg class (Minuteman-derived basing) | EST |
| CEP | ~120 m class (≈400 ft, W87/Mk21 OSINT; Mk21A adaptation) | OSINT-M/CLASS |
| Basing | ~400 deployed silos + launch control across F.E. Warren, Malmstrom, Minot | OSINT-H |
| IOC | Slipped to ~2030+ after restructure | OSINT-H |

### 2.1 Program status — the cost truth  **[OSINT-H]**

In January 2024 the program triggered a **critical Nunn-McCurdy breach** (per-unit cost growth ≥37%; program acquisition unit cost rose from ~**$118 M** to ~**$162 M** per missile in 2020 dollars). The July 2024 review put total program cost at **~$140.9 B** — about **81% over** the ~**$95.3 B** baseline — and revoked the EMD certification while directing a restructure. Critically, OSINT attributes the overrun primarily to the **command-and-launch / military-construction segment** (rebuilding 1960s-era silos, launch control centers, and tens of thousands of km of cabling) — **not the flight vehicle**. The Pentagon certified the program as essential (the land leg of the triad), so it continues but restructured; first test launch targeted ~2027 and IOC slipped to the **early 2030s**. (FY2027 request: ~$4.6 B, mostly RDT&E.)

> **Truth:** Sentinel's hardest engineering problem turned out to be **civil/infrastructure modernization at continental scale**, not rocketry. The flight vehicle is an evolution of mature solid-ICBM technology.

### 2.2 Why silo-based, and the survivability paradox

- **Pros:** hardened silos (hundreds of psi overpressure rating), continuous alert, seconds-to-launch readiness, the most accurate and most tightly C2-controlled leg of the triad, and a **warhead-absorbing "sponge"** — an adversary must expend ~2 warheads per silo to attempt destruction, complicating any first strike.
- **Con / paradox:** silos are **fixed and surveyed**. Their coordinates are effectively known. Their survivability rests on **hardness + the threat of launch-under-attack/launch-on-warning**, not on hiding. This is the structural reason the land leg is sometimes called destabilizing — its survivability logic pushes toward fast launch decisions.

### 2.3 Flight profile (representative, minimum-energy)  **[PHYS]/[EST]**

Boost ~180 s → burnout ~6.9 km/s near 200 km → apogee ~1,200 km → ~25 min exo-atmospheric coast → reentry at ~6.7 km/s (≈Mach 21) → impact ~30 min after launch for a full-range shot. The Mk21A is a **high-β, accuracy-optimized** RV: it retains velocity deep into the atmosphere (good CEP, good hard-target capability), at the cost of demanding heat-shield engineering (§1.3).

---

## 3. DF-41 (DONGFENG-41) — ENGINEERING TRUTHS

| Parameter | Value | Conf. |
|-----------|-------|-------|
| Role | Strategic ICBM; **road-mobile (TEL)**, with rail-mobile and silo options | OSINT-H |
| Propulsion | 3-stage **solid** | OSINT-H |
| Launch mass / size | ~**80,000 kg**; ~21–22 m long, ~2.25 m dia | OSINT-M |
| Range | ~**12,000–15,000 km** (covers CONUS from China) | OSINT-M |
| Warheads | **MIRV, 3–10** independently targetable RVs (most estimates "up to ~10") | OSINT-M |
| Throw weight | ~**2,500 kg** | OSINT-M |
| CEP | ~**100–200 m** | OSINT-M/EST |
| Reentry speed | in excess of ~Mach 25 quoted in some sources; physically ~6–7 km/s ≈ Mach 20–23 | OSINT-M/PHYS |
| Status | Entered service ~2017–2020; paraded 2019 | OSINT-H |

### 3.1 Why road/rail-mobile — the opposite survivability philosophy

DF-41's defining engineering choice is **mobility**. A transporter-erector-launcher (TEL) on roads (or rail) makes the launch point **uncertain**, so survivability comes from **hiding and dispersal** rather than (only) from hardness.

> **Truth:** mobility is a survivability *multiplier* but a readiness/accuracy *tax*. A moving TEL must stop, level, and align before launch; mobile alignment and the less-stable launch base historically make a road-mobile system marginally less accurate than a surveyed silo (hence DF-41's wider OSINT CEP band, ~100–200 m, vs Sentinel's ~90–120 m class). China hedges by also fielding **silo fields** for some forces.

### 3.2 The MIRV multiplier  **[PHYS]**

DF-41's larger throw weight (~2,500 kg vs ~1,000-class) lets it carry **multiple RVs + penetration aids**. Strategic arithmetic:

- One DF-41 presenting, say, 6 RVs + decoys forces the defender to discriminate and intercept **many credible objects** per missile.
- Against a finite midcourse interceptor inventory, **a handful of MIRVed missiles can saturate** the defense (see §5.4). MIRV is therefore simultaneously a counterforce tool (many aimpoints per booster) and a BMD-defeat tool (many objects per booster).

---

## 4. SENTINEL vs DF-41 — HEAD-TO-HEAD

### 4.1 Side-by-side

| Dimension | **LGM-35A Sentinel (US)** | **DF-41 (PRC)** | Physics/why it matters |
|-----------|---------------------------|-----------------|------------------------|
| Basing | Fixed hardened **silo** | **Road/rail-mobile** + silo | Hardness+sponge vs hide+disperse |
| Survivability model | Absorb a strike / launch-on-warning | Pre-launch concealment | Different failure modes |
| Stages / fuel | 3-stage solid | 3-stage solid | Both storable, fast-launch |
| Range | ~13,000+ km | ~12,000–15,000 km | Both full-CONUS / full-China class |
| Throw weight | ~1,000–1,150 kg class | ~2,500 kg | DF-41 carries more RVs/penaids |
| Warheads (deployed) | 1 RV (treaty), MIRV-capable | 3–10 MIRV | DF-41 = more aimpoints + saturation |
| CEP | ~90–120 m class | ~100–200 m | Silo accuracy edge → hard-target kill |
| Accuracy driver | Surveyed launch + Mk21A | Mobile alignment penalty | CMP ∝ 1/CEP² |
| Flight time (full range) | ~30 min | ~30 min | Both ~30 min — strategic-warning regime |
| Reentry speed | ~6.7 km/s (~Mach 21) | ~6–7 km/s (~Mach 20–23) | Both hypersonic, sub-minute terminal |
| Program maturity | Restructured, IOC ~2030+, cost-stressed | Operational since ~2017–2020 | DF-41 fielded now; Sentinel modernizing |
| Cost story | Infra/MILCON-driven (~$140 B program) | Lower (mobile, no silo-field rebuild) | Mobility avoids continental MILCON bill |

### 4.2 The honest verdict (physics-bounded)

- **Accuracy / hard-target kill:** edge to **Sentinel** (surveyed silo + Mk21A → tighter CEP; CMP ∝ 1/CEP²).
- **Pre-launch survivability:** edge to **DF-41** (mobility defeats a counterforce first strike by being un-locatable; Sentinel's silos are known and rely on hardness + fast launch).
- **Saturation / payload flexibility:** edge to **DF-41** (greater throw weight → more MIRVs + penaids per booster → stresses BMD inventory).
- **Readiness *now*:** edge to **DF-41** (operational; Sentinel's IOC slipped to ~2030+).
- **Both** share the same fundamental flight physics: ~30-minute intercontinental flight, ~1,200 km apogee, hypersonic sub-minute reentry. Neither can be **recalled** once launched. That irrevocability is the defining strategic property of the ballistic path.

### 4.3 The counterforce / decapitation **timeline** truth (doctrinal level)  **[PHYS]**

| Delivery path | Notice from launch to impact |
|---------------|------------------------------|
| ICBM (Sentinel / DF-41), full range | **~30 min** |
| SLBM, depressed trajectory, near coast | **~10–15 min** |
| Penetrating bomber, from CONUS | **~12–16 h** transit |
| Penetrating bomber, forward-based (Guam/Diego Garcia-class) | **~4–6 h** |

> **Truth:** the ballistic path compresses national decision time to **minutes**. Space-based infrared sensors detect the boost plume within seconds; ground BMEW radars confirm midcourse; the defending leadership then has on the order of ten-odd minutes to decide. This compression is the engine of the **launch-on-warning** debate and the reason **NC3 (nuclear command, control, communications) survivability and continuity-of-government** are studied as the true center of gravity. The bomber path, by contrast, is slow but **recallable and signal-bearing** — it can be launched, observed, and turned back, which is why it is valued for crisis signaling and flexible response.

---

## 5. "PAST DEFENSE" — DEFEATING LAYERED DEFENSES

Two different defensive problems must be beaten by the two paths.

### 5.1 The two defense problems

| | **Ballistic path (ICBM/RV)** must beat → | **Air-breathing path (bomber)** must beat → |
|---|---|---|
| Defense | **BMD** (Ballistic Missile Defense) | **IADS** (Integrated Air Defense System) |
| Defender sensors | Space IR (boost), large UHF/X-band radars (midcourse/terminal) | EW/VHF (volume search), acquisition + engagement radars (X/Ku) |
| Defender effectors | GMD/GBI, Aegis SM-3, THAAD, Patriot (US); HQ-19/-26-class (PRC) | S-300/-400/-500, HQ-9/-22, Patriot + interceptor fighters |
| Attacker's lever | Speed, decoys, MIRV saturation, maneuvering RV/HGV | Low RCS, route planning, EW, stand-off, SEAD/DEAD |
| Hardest moment | Midcourse discrimination (vacuum, no drag) | Conversion of low-band detection → fire-control track |

### 5.2 IADS architecture (what the bomber faces)

```
                    SPACE / OTH ── strategic warning
                          │
   ┌──────── EARLY-WARNING / VHF radar (volume search, 300–600 km) ────────┐
   │   detects, cannot yet target stealth at fire-control quality          │
   ├──────── ACQUISITION radar (hand-off, narrows track) ──────────────────┤
   ├──────── ENGAGEMENT / FIRE-CONTROL radar (X/Ku, weapons-quality) ──────┤
   │            │ S-400 / S-500 / HQ-9 launchers          fighters + AEW&C │
   └────────────┴──────────────────── C2 / data fusion ───────────────────┘
```

The kill chain is **find → fix → track → target → engage → assess**. Stealth + EW + routing attack the *weakest link* — usually the conversion of a coarse VHF detection into a weapons-quality engagement track.

### 5.3 Radar detection vs RCS — worked numbers  **[PHYS]**

Using `R_detect ∝ σ^(1/4)` and a reference of a long-range SAM engagement radar that sees a **1 m²** target at **250 km**:

| Target | RCS (est.) | Detection range vs that radar |
|--------|-----------|-------------------------------|
| Legacy fighter / bomber | ~5 m² | ~373 km |
| 1 m² reference | 1 m² | 250 km |
| F-35-class | ~0.001 m² **[EST/CLASS]** | **~44 km** |
| B-2-class (≈ −30 dBsm) | ~0.001 m² **[EST]** | **~44 km** |
| B-21-class (≈ −40 dBsm) | ~0.0001 m² **[EST]** | **~25 km** |

> **Truth:** the 10,000× RCS reduction of a B-21-class signature collapses a 250 km engagement bubble to ~25 km. SAM sites are then **point defenses with small lethal footprints**, and a planned route can thread the **gaps between sites** (the "fly between the bubbles" geometry). The defender's counter is **more sensors, networked low-band radars, passive/bistatic detection, and pushing fighters/AEW forward** — i.e., re-growing the footprint by quantity and fusion.

### 5.4 ICBM penetration of BMD (the ballistic path)  **[PHYS]**

The RV exploits physics the defender cannot change:

1. **Speed:** ~7 km/s leaves seconds in the terminal window; closing speeds of 10–15 km/s give hit-to-kill near-zero error margin.
2. **Midcourse decoys/penaids:** in vacuum (no drag), light replica balloons/chaff fly the **same trajectory** as the RV → the defender must intercept (or discriminate) many credible objects.
3. **MIRV saturation:** throw weight buys multiple RVs; **N missiles × k RVs + decoys** can exceed a finite interceptor magazine. (US GMD fields a few dozen GBIs — a small number of heavily-MIRVed, decoy-equipped missiles can in principle saturate it; this is the open arithmetic behind "BMD is for rogue/small attacks, not a peer arsenal.")
4. **Maneuvering RVs / HGVs:** a maneuvering reentry vehicle or boost-glide vehicle flies a **non-ballistic, depressed, lower** trajectory — shrinking radar horizon warning time and breaking the "predict the impact point" assumption that midcourse interceptors rely on. (The repo's `df17_hgv_model.py` and related files model this class.)

> **Truth:** against a **peer-sized** ICBM force, midcourse BMD is **outmatched by decoys + numbers + physics**; it is credible mainly against **small/rogue** salvos. This is itself a strategic-stability finding, not an operational recipe.

### 5.5 Bomber penetration of IADS (the air-breathing path)  **[EST]**

Layered defeat, in order of leverage:

1. **Low RCS** — shrink every radar bubble (§5.3).
2. **Route planning** — exploit terrain masking and the gaps between point-defense bubbles.
3. **Stand-off weapons** — release LRSO/JASSM-class from outside the densest bubbles so the *weapon*, not the aircraft, runs the final gauntlet.
4. **Electronic warfare** — degrade track quality so even a detection cannot become a launch-quality solution.
5. **SEAD/DEAD** — actively roll back the IADS (anti-radiation weapons, cyber, decoys) so later strikers face a thinner defense.
6. **Hard-target penetrators** — for deeply buried command/leadership facilities, deliver a massive earth-penetrator (GBU-57 MOP-class, ~13,600 kg) that couples energy deep into rock (§1.8) — the one mission a hypersonic RV struggles to do because warhead/fuze survival at reentry loads is hard.

### 5.6 The hardened/deeply-buried-leadership problem (doctrinal)  **[PHYS]/[EST]**

The most protected national-command facilities are **deeply buried under hundreds of meters of rock**. The physics of §1.8 shows why neither path is trivially decisive:

- A **single conventional penetrator** may not reach a facility under deep rock; depth scales with sectional density and impact speed, both bounded by what an aircraft can carry and a casing can survive.
- A **nuclear ground-burst** couples far more energy but at enormous escalation cost and with cratering/coupling physics that still favor *deep* targets surviving.
- An **RV-delivered** penetrator faces the fuze/structure-survival ceiling at ~50–100 g and reentry heating.

> **Truth:** deep burial is a deliberate, physics-aware counter to *both* delivery paths. This is why "decapitation" is generally assessed in the open literature as **hard and unreliable**, and why continuity-of-government and dispersed/mobile NC3 exist — the defender engineers survivability faster than the attacker can engineer reach. This document deliberately stops at this doctrinal level.

---

## 6. COMPARATIVE SURVIVABILITY, COST, AND ROLE

### 6.1 Why a triad (and why both paths coexist)

| Property | ICBM (Sentinel/DF-41) | Penetrating bomber (B-2/B-21) | SLBM (context) |
|----------|----------------------|-------------------------------|----------------|
| Time to target | **~30 min** (fast) | hours (slow) | ~10–30 min |
| Recallable? | **No** | **Yes** | No |
| Survivability | Hardness/mobility | Dispersal + stealth in flight | **Highest** (hidden at sea) |
| Accuracy | **Highest (silo)** | High (PGM/penetrator) | High |
| Flexibility/signaling | Low | **Highest** | Low |
| Defeats | BMD (speed/decoys/MIRV) | IADS (stealth/EW/SEAD) | BMD + detection |

> **Truth:** the paths are **complementary, not redundant**. The ICBM provides prompt, accurate, un-stoppable response; the bomber provides recallable, flexible, re-targetable, penetrator-capable strike and visible signaling; the SLBM provides the survivable assured-retaliation backstop. A defender optimized to beat one path is exposed to the others — which is the entire deterrence rationale for maintaining all three.

### 6.2 Approximate cost-per-delivered-effect (order of magnitude)  **[EST]**

| Path | Unit / shot cost (OSINT order-of-magnitude) | Notes |
|------|---------------------------------------------|-------|
| Sentinel program | ~$140 B program (infra-dominated) | Fixed leg modernization |
| DF-41 | Lower; mobile, no continental silo rebuild | Operational now |
| B-21 | ~$0.7 B/aircraft (LRIP), target ~100+ a/c | Reusable, many sorties |
| GBU-57 MOP | Penetrator weapon, B-2/-21 delivery | Hard-target niche |

---

## 7. LIMITATIONS & UNCERTAINTY (the honest part)

| Quantity | Status | Why |
|----------|--------|-----|
| Sentinel/DF-41 exact CEP | **[CLASS]** | Bounded estimates only; actual values classified |
| RV ballistic coefficients, heat-shield specs | **[CLASS]** | Design data; physics bounds only |
| True stealth RCS (B-2/B-21/F-35) | **[CLASS]** | Order-of-magnitude estimates only |
| Real SAM/BMD Pk vs stealth/RVs | **[EST]** | Depends on tactics, ECM, geometry — not knowable from OSINT |
| Decoy/penaid effectiveness | **[EST]** | Discrimination is the classified crux of BMD |
| Operational targeting | **Out of scope** | Deliberately excluded |

Every numeric value above is an **OSINT or first-principles estimate with explicit uncertainty**, consistent with `ACCURACY_AND_LIMITATIONS_CAD.md` and `LEGAL_DISCLAIMER.md`. None is, or is represented to be, ground truth, an intelligence assessment, or operational data.

---

## APPENDIX A — EQUATIONS & CONSTANTS

```
Rocket eq.:          Δv = Isp · g0 · ln(m0/mf)            g0 = 9.81 m/s²
Ballistic coeff.:    β  = m / (Cd · A)
Allen–Eggers a_max:  a_max = V_E² sin γ_E / (2 e H)        H ≈ 7 km, e = 2.718
Stagnation heating:  q_stag ∝ √(ρ/R_n) · V³
SSPK:                SSPK = 1 − 0.5^((LR/CEP)²)
Lethal radius:       LR ∝ Y^(1/3)
Hard-target capab.:  CMP ∝ Y^(2/3) / CEP²
Radar range:         R_max = [P_t G² λ² σ / ((4π)³ P_min L)]^(1/4)
Detection scaling:   R_detect ∝ σ^(1/4)
Radar resolution:    θ ≈ λ / D
```

## APPENDIX B — DATA SOURCES (OSINT)

| Topic | Public source class |
|-------|---------------------|
| Sentinel cost / Nunn-McCurdy | GAO, CBO, DoD public statements, defense press |
| DF-41 specs | IISS Military Balance, CSIS Missile Threat, FAS, parade imagery |
| W87/Mk21A, CEP classes | FAS Nuclear Notebook, arms-control literature |
| B-2/B-21 | USAF/Northrop public statements, GAO, CSIS (see `B21_RAIDER_CAD_ANALYSIS.md`) |
| SAM/BMD performance | DoD China Military Power Report, CSIS, manufacturer data |
| Physics | Standard astronautics/reentry/radar texts (Allen–Eggers, Sutton–Graves, radar range eq.) |

**Key public references (accessed 2026-05):**
- CRS, *Defense Primer: LGM-35A Sentinel ICBM* — https://www.congress.gov/crs-product/IF11681
- USNI News, *Report to Congress on LGM-35A Sentinel ICBM* — https://news.usni.org/2024/11/11/report-to-congress-on-lgm-35a-sentinel-icbm-2
- Air & Space Forces Mag., *Sentinel Survives Pentagon Review, Cost Jumps 81%* — https://www.airandspaceforces.com/sentinel-icbm-pentagon-review-result-cost/
- CSIS Missile Threat, *DF-41 (Dong Feng-41 / CSS-X-20)* — https://missilethreat.csis.org/missile/df-41/
- Wikipedia, *DF-41* — https://en.wikipedia.org/wiki/DF-41
- USAF, *Second B-21 test aircraft arrives at Edwards AFB* — https://www.af.mil/News/Article-Display/Article/4301502/
- Nuclear Weapon Archive, *The W87 Warhead* — https://nuclearweaponarchive.org/Usa/Weapons/W87.html
- Air & Space Forces Mag., *AF Gives Lockheed $1B for Sentinel Reentry Vehicle (Mk21A)* — https://www.airandspaceforces.com/air-force-lockheed-1-billion-sentinel-icbm-reentry-vehicle/

## APPENDIX C — KEY ASSUMPTIONS

1. Minimum-energy ballistic trajectories unless stated; full-range ~13,000 km class.
2. Atmospheric scale height H ≈ 7 km; entry speed ~7 km/s for worked examples.
3. RCS estimates are order-of-magnitude; detection ranges scale from a 1 m²/250 km reference.
4. Solid-motor Isp 250–265 s.
5. No classified design data used; deep-target and discrimination discussion kept doctrinal.

## APPENDIX D — GLOSSARY

**A2/AD** anti-access/area-denial · **BMD** ballistic missile defense · **CEP** circular error probable · **CMP** counter-military potential · **DEAD/SEAD** destruction/suppression of enemy air defenses · **HGV** hypersonic glide vehicle · **IADS** integrated air defense system · **MIRV** multiple independently-targetable reentry vehicle · **MOP** Massive Ordnance Penetrator (GBU-57) · **NC3** nuclear command, control & communications · **RAM/RAS** radar-absorbent material/structure · **RV** reentry vehicle · **SSPK** single-shot probability of kill · **TEL** transporter-erector-launcher.

---

**Classification:** UNCLASSIFIED // OSINT ANALYSIS // FOR PUBLIC RELEASE
**Prepared for:** Defense-CAD strategic-strike capability comparison set
**Scope guard:** Doctrine + physics only. No individual targeting, no facility coordinates, no weapon-design data, no operational mission planning.
**Date:** 2026-05-29
