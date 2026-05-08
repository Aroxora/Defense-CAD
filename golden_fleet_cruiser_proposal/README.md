# Golden Fleet - Heavy Cruiser Proposal

A sensible alternative to simply scaling up existing naval combatants: a **Large Surface Combatant (LSC-X)** designed specifically for Army-Navy equipment integration.

## The Problem

Current destroyers and cruisers (~10,000 tons) cannot accommodate larger Army systems:
- THAAD launchers (40 tons, 12m long)
- AN/TPY-2 radar (25 tons, requires 600 kW)
- PrSM containerized launchers

## The Solution

A 23,000-ton heavy cruiser with:
- **160 VLS cells** (vs 96 on DDG-51)
- **30 MW combat power reserve** (vs 9 MW on DDG-51)
- **Deck space for THAAD launchers** - 16 interceptors
- **Army PrSM integration** - 1000 km anti-ship capability
- **150 kW directed energy weapons** - soft-kill for swarm threats

## Files

| File | Description |
|------|-------------|
| `HEAVY_CRUISER_PROPOSAL.md` | Full technical proposal document |
| `lsc_x_model.py` | Physics-based capability simulation |

## Run Simulation

```bash
python3 lsc_x_model.py
```

## Key Insight

"100x battleship power" in modern naval warfare isn't about bigger guns - it's about **sensor-effector integration**. This design provides:

1. **Layered BMD** (SM-3 + THAAD = 99.7% Pk)
2. **Extended strike range** (Army PrSM from sea = 1000 km)
3. **Multi-domain integration** (Army/Navy fires fusion)

Cost: $4.5B vs $6B for 3x DDG-51s with less capability.
