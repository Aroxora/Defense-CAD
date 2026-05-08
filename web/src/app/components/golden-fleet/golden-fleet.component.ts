import { Component, OnInit, AfterViewInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import * as d3 from 'd3';

interface HullSpec {
  parameter: string;
  value: string | number;
  unit: string;
}

interface PlatformOption {
  name: string;
  designation: string;
  cpsCells: number | string;
  unitCostB: number | string;
  survivability: 'Low' | 'Moderate' | 'High';
  availability: string;
  notes: string;
}

interface VLSLoadout {
  missile: string;
  cells: number;
  role: string;
  color: string;
}

interface DefenseLayer {
  system: string;
  range_km: number;
  pk: number;
  type: 'outer' | 'middle' | 'inner' | 'ciws';
  color: string;
}

interface CPSSpec {
  parameter: string;
  value: string;
}

interface EngineeringConstraint {
  category: string;
  requirement: string;
  status: 'proven' | 'in-development' | 'speculative';
}

@Component({
  selector: 'app-golden-fleet',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './golden-fleet.component.html',
  styleUrl: './golden-fleet.component.scss'
})
export class GoldenFleetComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('costEffectivenessChart') costEffectivenessChart!: ElementRef;
  @ViewChild('cpsCellComparisonChart') cpsCellComparisonChart!: ElementRef;
  @ViewChild('defenseLayerChart') defenseLayerChart!: ElementRef;

  Math = Math;

  activeSection = 'cps-overview';

  sections = [
    { id: 'original-proposal', label: 'Original BBG Proposal' },
    { id: 'contracts-budget', label: 'Contracts & Budget' },
    { id: 'arsenal-cad', label: 'Arsenal Ship CAD' },
    { id: 'cps-overview', label: 'CPS System Overview' },
    { id: 'trade-study', label: 'Platform Trade Study' },
    { id: 'lsc-concept', label: 'DDG-1000 Zumwalt CAD' },
    { id: 'constraints', label: 'Engineering Constraints' },
    { id: 'cost-analysis', label: 'Cost Analysis' },
  ];

  // Trump-class BBG-1 "Golden Fleet" battleship — announced Dec 22, 2025
  // Sources: USNI News, CSIS, Breaking Defense, The War Zone, Navy.mil
  originalProposal = {
    name: 'Trump-class Guided Missile Battleship (BBG-1 USS Defiant)',
    program: 'Golden Fleet',
    announcedDate: 'December 22, 2025 — Mar-a-Lago',
    announcedBy: 'President Trump, SecDef Pete Hegseth, SecNav John Phelan',
    displacement: '30,000–40,000 tons (official Navy data: 35,000+ tons)',
    length: '840–880 ft (256–268 m)',
    beam: '105–115 ft (32–35 m)',
    draft: '24–30 ft (7.3–9.1 m)',
    speed: '30+ knots',
    crew: '650–850 sailors',
    vlsCells: '128 Mk 41 VLS cells (3 arrays: 2 forward, 1 aft)',
    cpsCells: '12 Conventional Prompt Strike (IRCPS)',
    estimatedCost: '$9.1B per hull (CBO est.); lead ship ~$13.5B (50% first-of-class premium)',
    radar: 'AN/SPY-6 (AMDR)',
    flightDeck: 'Hangar + flight deck rated for V-22 Osprey and future FLRAA vertical lift',
    guns: 'Multiple turreted 5-inch (Mk 45) naval guns',
    plannedQuantity: '2 initial, target 20–25 total',
    constructionStart: '2030 (planned)',
    replacesProgram: 'DDG(X) next-generation destroyer (canceled/deferred)',
    weapons: [
      { system: '128 Mk 41 VLS cells', status: 'Proven', note: 'Standard strike-length launcher. In service across DDG-51, CG-47 fleet. Well-understood.' },
      { system: '12 CPS (IRCPS) via LMVLS', status: 'In Development', note: 'CPS AUR (34.5″, ~12m) requires LMVLS (2.2m dia) — NOT Mk 41. Tested from land TEL only (Dec 2024, May 2025). First ship launch FY2027-2028 from DDG-1000. No LMVLS design exists for BBG hull.' },
      { system: 'Electromagnetic Railgun (32 MJ)', status: 'Canceled', note: 'Navy canceled railgun program in 2021 after $500M+ spent. Barrel erosion, power supply, and rate-of-fire problems unresolved. Would need to restart from scratch.' },
      { system: 'Directed Energy Weapons (laser)', status: 'Early Development', note: 'Navy HELIOS (150 kW) operational on USS Preble. Effective against drones only. Scaling to battleship-relevant power (300+ kW) is unproven.' },
      { system: 'Nuclear SLCM (SLCM-N)', status: 'Not Yet Funded', note: 'Nuclear sea-launched cruise missile. Congress has not appropriated development funds. Requires nuclear warhead design, arms control implications.' },
      { system: '5-inch Mk 45 guns (multiple)', status: 'Proven', note: 'Standard naval gun, in service since 1971. Proven and reliable but limited range (~24 km).' },
      { system: 'AN/SPY-6 radar', status: 'Proven', note: 'Active electronically scanned array. In production for DDG-51 Flight III. Well-understood technology.' },
    ],
  };

  originalProposalIssues = [
    {
      issue: 'Railgun program was canceled in 2021',
      detail: 'The Navy spent $500M+ on electromagnetic railgun development and canceled it due to barrel erosion (barrels lasted ~400 shots), thermal management, and inability to achieve militarily useful rate of fire. Restarting this program adds billions in R&D with no guarantee of success.',
      severity: 'critical',
    },
    {
      issue: 'Estimated cost of $9.1B per hull ($13.5B lead ship)',
      detail: 'CBO estimates ~$300K/ton for modern combatants. At 35,000 tons that yields $9.1B, with lead ship at ~$13.5B — approaching aircraft carrier cost ($13.3B for CVN-78 Ford). For 20-25 ships at $9B each: $180-225B total program cost. DDG-1000 program saw 83% unit cost growth when buy shrank from 24 to 3 hulls.',
      severity: 'critical',
    },
    {
      issue: 'Contradicts Navy distributed lethality doctrine',
      detail: 'The Navy\'s stated strategy since 2015 is distributed maritime operations — spreading sensors, shooters, and C2 across many smaller platforms networked together. A 35,000-ton battleship concentrates enormous value in a single targetable hull, the opposite approach. CSIS: "strategically wrong, fiscally wrong, and tactically wrong."',
      severity: 'critical',
    },
    {
      issue: 'Replaces DDG(X), which was already sized for the mission',
      detail: 'DDG(X) was designed as the DDG-51 replacement at ~13,500 tons with growth margin for future weapons. Canceling/deferring DDG(X) for a ship 3x larger delays the fleet recapitalization the Navy actually needs.',
      severity: 'critical',
    },
    {
      issue: 'U.S. shipyard capacity cannot support this',
      detail: 'HII and Bath Iron Works already have multi-year backlogs on DDG-51, Virginia-class SSN, Columbia-class SSBN, and CVN-78. Adding a 35,000-ton new-design warship requires new facilities, workforce, and tooling that do not exist. Navy shipbuilding is currently 2-3 years behind schedule.',
      severity: 'critical',
    },
    {
      issue: 'Nuclear SLCM-N has no funding or warhead',
      detail: 'SLCM-N requires a new nuclear warhead (W80-4 or equivalent), Congressional appropriation, and arms control review. The Biden administration canceled SLCM-N funding in FY2023. Restarting requires years of warhead development at NNSA.',
      severity: 'moderate',
    },
    {
      issue: 'Largest surface combatant since WWII = largest target since WWII',
      detail: 'At 35,000 tons, BBG-1 would be larger than any surface combatant built since Iowa-class (1943). China\'s DF-21D and DF-26 anti-ship ballistic missiles are specifically designed to kill large surface targets. A single ASBM hit could mission-kill a $9B asset.',
      severity: 'critical',
    },
    {
      issue: '"100 times more powerful" claim is not meaningful',
      detail: 'WWII battleships engaged at 15-mile range with 2,700-lb armor-piercing shells. Modern guided missiles operate at 100-1,700+ mile range. The comparison is apples to oranges. A DDG-51 with Tomahawk already outranges any WWII battleship by 80x.',
      severity: 'moderate',
    },
    {
      issue: 'CSIS assessment: "This ship will never sail"',
      detail: 'CSIS analysis concludes the program will take years to design, cost billions before first steel is cut, and be canceled by a future administration before commissioning — the same pattern as DDG-1000 (cut from 24 to 3), CG(X) (canceled), and LCS (truncated).',
      severity: 'moderate',
    },
  ];

  // BBG(X) Shipyard Contracts Awarded — Dec 22, 2025 (same day as announcement)
  // Sources: Defense Daily, USNI News, CRS IF13142, Breaking Defense
  shipyardContracts = [
    {
      contractor: 'Leidos / Gibbs & Cox',
      role: 'Lead Ship Design Engineering (SC SDE)',
      scope: 'Preliminary design, contract design, requirements definition. Extension of government design team.',
      duration: '72 months (6 years, through ~2032)',
      contractType: 'Sole-source',
      legalBasis: '10 U.S.C. 3204(a)(1)',
      dollarValue: 'Not publicly disclosed',
      status: 'Awarded Dec 22, 2025',
    },
    {
      contractor: 'HII Ingalls Shipbuilding (Pascagoula, MS)',
      role: 'Shipbuilder Engineering & Design Analysis',
      scope: 'Design products, engineering analysis, construction planning for BBG(X).',
      duration: '6 years',
      contractType: 'Sole-source',
      legalBasis: '10 U.S.C. 3204(a)(1)',
      dollarValue: 'Not publicly disclosed',
      status: 'Awarded Dec 22, 2025',
    },
    {
      contractor: 'GD Bath Iron Works (Bath, ME)',
      role: 'Shipbuilder Engineering & Design Analysis',
      scope: 'Design products, engineering analysis, construction planning for BBG(X).',
      duration: '6 years',
      contractType: 'Sole-source',
      legalBasis: '10 U.S.C. 3204(a)(1)',
      dollarValue: 'Not publicly disclosed',
      status: 'Awarded Dec 22, 2025',
    },
  ];

  // Hanwha Philly Shipyard — Reality Check
  hanwhaAnalysis = {
    announcement: 'Trump stated battleships would be built at Hanwha Philly Shipyard.',
    acquisition: 'Hanwha acquired Philly Shipyard for $100M.',
    investment: '$5B expansion announced (2 new docks, 3 quays, block assembly facility).',
    problems: [
      'Philly Shipyard has never built a warship — only Jones Act commercial vessels.',
      'Does not hold a U.S. defense industrial license for naval combatants.',
      'Byrnes-Tollefson Amendment bars Navy ships from foreign-owned construction.',
      'Hanwha\'s announced role is actually FF(X) frigates, NOT BBG(X) battleships.',
      'No formal agreements for battleship construction have been disclosed.',
    ],
  };

  // CBO Cost Estimates — Jan 2026 (Eric Labs, SNA Symposium)
  cboCostEstimates = {
    source: 'Congressional Budget Office (CBO) — Eric Labs, SNA Symposium Jan 16, 2026',
    ifOrderedToday: {
      leadShip: '$14.3B – $20.6B',
      followOn: '$9B – $13B each',
    },
    ifOrderedFY2030: {
      leadShip: '$15.1B – $21.6B',
      followOn: '$10B – $15B each',
    },
    crsUpperEstimate: {
      leadShip: 'Up to $22B',
      followOn: 'Up to $12.7B each',
    },
    comparison: 'DDG-51 Flight III costs ~$2.7B. One BBG = 6-8 Burkes.',
  };

  // FY2026 Reconciliation Budget Breakdown
  fy2026Budget = {
    total: '$47.4B (SCN appropriation)',
    reconciliationShare: '$26.5B (56%)',
    newMoney: '$20.8B (44%)',
    shipsProcured: 19,
    bbgAllocation: '$0 — Zero dollars for BBG(X) construction',
    breakdown: [
      { item: 'DDG-51 Arleigh Burke destroyers', amount: '$5.4B', qty: '2 ships' },
      { item: 'Virginia-class SSN', amount: '$4.6B', qty: '1 additional sub' },
      { item: 'Amphibious warships (multi-ship)', amount: '$1.47B', qty: 'Contract' },
      { item: 'Medium unmanned surface vessels', amount: '$2.1B', qty: 'Development' },
      { item: 'Unmanned underwater vehicles', amount: '$1.3B', qty: 'Production expansion' },
      { item: 'Autonomy/AI for shipbuilding', amount: '$450M', qty: 'Workforce/tech' },
      { item: 'Columbia-class SSBN', amount: '$5.27B', qty: '1 sub' },
      { item: 'Columbia-class advanced procurement', amount: '$5.21B', qty: 'Future subs' },
    ],
  };

  // Arsenal Ship Requirements — What Would Actually Make Sense
  arsenalRequirements = {
    mission: 'Distributed magazine / saturation strike platform',
    vlsCells: '200+ CPS/hypersonic cells across the force',
    power: '100+ MW for future directed energy weapons at battleship-relevant power',
    survivability: 'Unmanned, highly compartmented, or distributed across many hulls',
    production: 'Buildable at existing shipyards without starving Columbia/Virginia/DDG-51',
  };

  // Arsenal Ship Options — Trade Study
  arsenalOptions = [
    {
      name: 'MASC Fleet (Distributed Unmanned)',
      description: 'Modular Attack Surface Craft — 16-32 VLS cells per hull, many unmanned vessels operating as "adjunct magazines" for manned combatants.',
      vlsCells: '16-32 per hull',
      totalFor200: '7-13 hulls',
      unitCost: '~$200-350M',
      power: '~2 MW (insufficient for DEW)',
      survivability: 'Distributed — loss of one hull = loss of 16-32 cells, not 200+',
      production: 'Commercial standards, multiple yards, 18-month delivery target',
      status: 'In development — FY2026 prototype contract',
      timeline: 'First deliveries 2027-2028',
      pros: ['Distributed = survivable', 'Non-exquisite = easy to build', 'Unmanned = no crew risk', 'Already funded'],
      cons: ['Low power (no DEW)', 'C2 complexity', 'Autonomy not fully proven', 'CPS integration unclear'],
      verdict: 'RECOMMENDED for distributed strike magazine',
    },
    {
      name: 'Virginia Block V Expansion',
      description: 'Accelerate Virginia Block V SSN production. Each boat has Virginia Payload Module (VPM) with 4 large-diameter tubes for CPS or 28 Tomahawks.',
      vlsCells: '4 CPS or 28 TLAM per hull',
      totalFor200: '7 boats (CPS) or 8 boats (TLAM)',
      unitCost: '~$3.4B',
      power: 'Nuclear — unlimited for mission duration',
      survivability: 'Highest — submarine stealth',
      production: 'Electric Boat + Newport News. Currently 1.2-1.5 boats/year. Backlogged.',
      status: 'In production — but behind schedule',
      timeline: 'Block V boats delivering 2028+',
      pros: ['Highest survivability', 'Proven design', 'Nuclear endurance', 'CPS-capable'],
      cons: ['Expensive ($3.4B)', 'Production bottleneck', 'Only 4 CPS per boat', 'Competes with Columbia SSBN'],
      verdict: 'RECOMMENDED but cannot be sole solution due to production limits',
    },
    {
      name: 'Commercial Hull + Mk 70 Containers',
      description: 'Acquire commercial container ships or tankers ($25-50M each), install Mk 70 containerized VLS (4 cells per 40ft container). China is already doing this with Zhong Da 79.',
      vlsCells: '30-60 per ship (deck space limited)',
      totalFor200: '4-7 ships',
      unitCost: '~$100-200M (hull + conversion + Mk 70s)',
      power: '10-20 MW (commercial diesels) — marginal for DEW',
      survivability: 'Low — no armor, no compartmentalization, no damage control',
      production: 'Commercial yards worldwide. Fast acquisition.',
      status: 'Concept proven — Mk 70 tested on LCS, Army Typhon deployed',
      timeline: 'Could deploy in 12-24 months',
      pros: ['Cheap hulls ($25-50M)', 'Fast acquisition', 'Mk 70 is proven', 'Massive global shipyard capacity'],
      cons: ['Not survivable', 'Slow speed', 'No self-defense', 'Crew exposure', 'Mk 70 is Mk 41 only — no CPS'],
      verdict: 'VIABLE for low-threat / second-salvo mission. NOT for CPS.',
    },
    {
      name: 'LPD-17 Flight II Arsenal Variant',
      description: 'HII proposed in 2013: modify LPD-17 San Antonio-class hull to carry up to 288 VLS cells for BMD and strike. Production line exists.',
      vlsCells: '288 (Mk 41)',
      totalFor200: '1 ship',
      unitCost: '~$2.5-3.5B (estimated)',
      power: '~40 MW (LM2500+ gas turbines) — marginal for high-power DEW',
      survivability: 'Moderate — large hull, some compartmentalization, but big target',
      production: 'HII Ingalls — same yard as LPD-17. Could use existing workforce.',
      status: 'Concept only — no program of record',
      timeline: '6-8 years from contract to delivery (typical for new variant)',
      pros: ['Huge VLS capacity', 'Existing hull design', 'Existing production line', 'Single ship = 288 cells'],
      cons: ['Concentrates risk', '~$3B per hull', 'No CPS/LMVLS variant designed', 'Competes with amphibs'],
      verdict: 'VIABLE if Navy wants single-hull arsenal. Needs LMVLS integration for CPS.',
    },
    {
      name: 'Ohio SSGN Life Extension',
      description: 'Retain and refuel remaining Ohio SSGNs instead of retiring. Each carries 154 Tomahawks. 4 boats = 616 tubes.',
      vlsCells: '154 TLAM per hull (22 tubes × 7)',
      totalFor200: '2 boats',
      unitCost: '~$1.5-2B (refueling + life extension)',
      power: 'Nuclear — unlimited',
      survivability: 'High — submarine',
      production: 'Puget Sound Naval Shipyard / Electric Boat. Competes with Columbia.',
      status: 'Retiring — Ohio (SSGN-726) and Florida (SSGN-728) decommissioning 2026',
      timeline: 'Would require immediate decision to stop retirement',
      pros: ['Hulls exist', '154 tubes each', 'Proven system', 'High survivability'],
      cons: ['Hulls are 40+ years old', 'Reactor refueling competes with Columbia', 'Navy chose not to retain', 'No CPS capability'],
      verdict: 'TOO LATE — Navy already decommissioning. Window closed.',
    },
    {
      name: 'DDG-1000 + MASC Hybrid',
      description: 'Use 3 DDG-1000s (36 CPS total, 78 MW power for DEW) as command ships with MASC unmanned arsenal escorts carrying Mk 41 missiles.',
      vlsCells: '36 CPS (DDG-1000) + 96-192 Mk 41 (MASC)',
      totalFor200: '3 DDG-1000 + 6-12 MASC',
      unitCost: 'DDG-1000: sunk. MASC: ~$2-3B total for 6-12 hulls',
      power: '78 MW per DDG-1000 — best available for DEW',
      survivability: 'Distributed MASC + moderate DDG-1000',
      production: 'MASC: multiple yards. DDG-1000: already built.',
      status: 'DDG-1000 refitting now. MASC in development.',
      timeline: 'DDG-1000 operational 2026-2028. MASC 2027-2028.',
      pros: ['DEW-capable (DDG-1000 power)', 'CPS-capable (DDG-1000 LMVLS)', 'Distributed magazine (MASC)', 'Mostly funded'],
      cons: ['Only 3 DDG-1000 hulls', 'MASC autonomy unproven', 'Integration complexity'],
      verdict: 'RECOMMENDED — Best near-term option for CPS + DEW + distributed magazine',
    },
  ];

  // Power Analysis for DEW
  powerAnalysis = [
    { platform: 'DDG-51 Flight III', totalPower: '87 MW', electricalPower: '7.5 MW', dewCapable: 'No (150 kW max)', notes: 'Mechanical propulsion. Limited electrical.' },
    { platform: 'DDG-1000 Zumwalt', totalPower: '78 MW', electricalPower: '78 MW (IPS)', dewCapable: 'Yes (300-600 kW feasible)', notes: 'All-electric IPS. Best surface combatant for DEW.' },
    { platform: 'CVN-78 Ford', totalPower: '~200 MW', electricalPower: '~100 MW', dewCapable: 'Yes (MW-class)', notes: 'Nuclear. Overkill for arsenal mission.' },
    { platform: 'LPD-17', totalPower: '~40 MW', electricalPower: '~10 MW', dewCapable: 'Marginal (150 kW)', notes: 'Could upgrade with IPS for arsenal variant.' },
    { platform: 'MASC', totalPower: '~2-5 MW', electricalPower: '~150 kW', dewCapable: 'No', notes: 'Commercial diesels. Magazine-only, no DEW.' },
    { platform: 'Commercial Container Ship', totalPower: '10-30 MW', electricalPower: '2-5 MW', dewCapable: 'No', notes: 'Slow-speed diesels for cargo. No DEW margin.' },
  ];

  // What to Do With Existing Contracts — Recommendations
  contractRecommendations = [
    {
      option: 'Terminate for Convenience (T4C)',
      description: 'Cancel all BBG(X) design contracts under FAR 49.5. Government pays for work completed to date plus reasonable termination costs. No further design work.',
      pros: ['Stops bleeding immediately', 'Standard contract clause — no litigation', 'Frees up Gibbs & Cox, HII, BIW for other work'],
      cons: ['Sunk cost on design work to date', 'Political embarrassment for administration'],
      verdict: 'RECOMMENDED if BBG(X) is assessed as not viable.',
    },
    {
      option: 'Redirect to DDG(X)',
      description: 'Transfer design work scope back to DDG(X) program that was suspended. Use Gibbs & Cox and shipyard engineering on the 13,500-ton destroyer the Navy actually needs.',
      pros: ['Design work not wasted', 'DDG(X) has existing requirements', 'Restarts cruiser/destroyer recapitalization'],
      cons: ['Administration may resist reversing its own program', 'Some BBG-specific work not transferable'],
      verdict: 'RECOMMENDED — best use of contracted engineering resources.',
    },
    {
      option: 'Slow-Roll / Reduce Scope',
      description: 'Keep contracts active but reduce funding rate. Stretch 6-year design to 10+ years. Hope next administration cancels.',
      pros: ['Avoids immediate political fight', 'Keeps options open'],
      cons: ['Continues to waste money', 'Ties up engineering talent', 'Delays other programs'],
      verdict: 'NOT RECOMMENDED — worst of all worlds.',
    },
    {
      option: 'Proceed as Planned',
      description: 'Continue 6-year design phase, begin construction in early 2030s, deliver first ship late 2030s.',
      pros: ['Fulfills administration promise', 'HII/BIW get work'],
      cons: ['$180-225B total program cost', 'First ship ~$20B', 'No shipyard capacity', 'CSIS: "will never sail"', 'Delays Columbia, Virginia, DDG-51 programs'],
      verdict: 'NOT RECOMMENDED — fiscally and strategically wrong.',
    },
  ];

  // CPS / LRHW "Dark Eagle" technical specs — verified from DoD, USNI, CRS, Lockheed Martin
  cpsSpecs: CPSSpec[] = [
    { parameter: 'Program Name', value: 'Long Range Hypersonic Weapon (LRHW) "Dark Eagle"' },
    { parameter: 'Warhead', value: 'Common Hypersonic Glide Body (C-HGB) — kinetic energy, non-explosive' },
    { parameter: 'Booster', value: '34.5″ (87.6 cm) diameter two-stage solid rocket' },
    { parameter: 'AUR Length', value: '~12 m (~39 ft) fully assembled All-Up Round' },
    { parameter: 'Range', value: '1,725+ mi (2,776+ km) — Army states "in excess of"' },
    { parameter: 'Speed', value: 'Mach 17 peak (Army); Mach 5+ sustained glide (~6,100+ km/h)' },
    { parameter: 'Flight Profile', value: 'Boost-glide: two-stage rocket to altitude, C-HGB released, unpowered maneuvering glide' },
    { parameter: 'Launch Mechanism', value: 'Cold-gas eject from canister, booster ignites after clearing platform' },
    { parameter: 'Ship Launcher', value: 'Large Missile VLS (LMVLS) — 2.2 m diameter tubes. NOT compatible with Mk 41 (21″) or Mk 57.' },
    { parameter: 'Navy Designation', value: 'Conventional Prompt Strike (CPS) / Intermediate-Range CPS (IRCPS)' },
    { parameter: 'Prime Contractors', value: 'Lockheed Martin (weapon system); Leidos (C-HGB)' },
    { parameter: 'Current Platforms', value: 'DDG-1000 Zumwalt (AGS removed, LMVLS installed — 4 modules × 3 AURs = 12); Virginia Block V SSN (VPM — 4 large tubes)' },
    { parameter: 'Army Ground Battery', value: '4× M983 TEL trucks (2 AURs each) + command vehicle = 8 missiles per battery' },
    { parameter: 'Test: Dec 12, 2024', value: 'Land-based (TEL at Cape Canaveral). All-Up Round end-to-end flight test — successful. Second successful AUR test of 2024.' },
    { parameter: 'Test: May 2, 2025', value: 'Cape Canaveral SFSS. First CPS flight test using Navy cold-gas launch approach — the same eject method that will be used on ships. End-to-end flight successful. (DoD Public Affairs, SSP)' },
    { parameter: 'Cold-Gas Significance', value: 'Cold-gas ejects AUR from canister to safe distance above ship BEFORE first-stage solid rocket ignites. Critical for ship safety — solid rocket ignition inside a launcher would destroy the ship. Same principle as Trident SLBM submarine launch.' },
    { parameter: 'In-Air Launch Facility', value: 'SSP conducted "extensive test campaign" at an In-Air Launch test facility to validate the launch approach before the May 2025 flight test. This is a land-based simulator of shipboard launch conditions.' },
    { parameter: 'Ship Live-Fire', value: 'CPS live-fire demonstration from USS Zumwalt scheduled 2027 (GAO, June 2025). Operational employment expected 2026-2028.' },
    { parameter: 'Program Lead', value: 'Navy Strategic Systems Programs (SSP) — VADM Johnny R. Wolfe Jr., Director. SSP is lead designer of the common hypersonic missile.' },
  ];

  // DDG-1000 Zumwalt full CAD — verified from HII, USNI, TWZ, Naval News, Defense Daily, GAO
  zumwaltCad = {
    designation: 'DDG-1000 USS Zumwalt',
    class: 'Zumwalt-class guided-missile destroyer',
    hull: 'Tumblehome wave-piercing hull form',
    displacement: '15,742 tons (full load)',
    length: '610 ft (186 m)',
    beam: '80.7 ft (24.6 m)',
    draft: '27.6 ft (8.4 m)',
    propulsion: 'Integrated Power System (IPS): 2× Rolls-Royce MT30 gas turbines (35.4 MW each) + 2× Rolls-Royce RR4500 auxiliary turbine generators. Total: ~78 MW. All-electric drive via 2× electric induction motors driving fixed-pitch propellers.',
    speed: '30+ knots',
    range: '~10,000 nm at economical speed',
    crew: '148 (originally designed for high automation)',
    radar: 'AN/SPY-3 (X-band, MFR) + AN/SPY-4 (S-band, VSR — removed from production ships due to cost)',
    combatSystem: 'Total Ship Computing Environment (TSCE)',
  };

  zumwaltCpsIntegration = {
    lmvlsTubes: '4× Large Missile VLS (LMVLS) tubes',
    tubeDiameter: '87 inches (7.25 ft / 2.21 m) per tube',
    missileLoading: 'IRCPS triple-packed into Advanced Payload Module (APM) canisters — 3 AURs per tube × 4 tubes = 12 CPS total',
    removedSystems: 'Both 155mm Advanced Gun Systems (AGS) removed. Forward turret housing scrapped for LMVLS. Second gun emplacement internals gutted.',
    installationTimeline: [
      { date: 'Aug 2023', event: 'USS Zumwalt arrives Ingalls Shipbuilding, Pascagoula MS for modernization' },
      { date: 'Mar 2024', event: 'Forward 155mm AGS turret removal completed' },
      { date: 'May 2024', event: 'LMVLS foundation installation' },
      { date: 'Jul-Aug 2024', event: '4 LMVLS tubes delivered to shipyard' },
      { date: 'Oct 2024', event: 'Basic tube installation completed' },
      { date: 'Nov 2025', event: 'Advanced Payload Module (APM) installation complete' },
      { date: 'Dec 2024', event: 'USS Zumwalt undocked — back in the water' },
      { date: 'Jan 21, 2026', event: 'HII completes builder\'s sea trials — first CPS-equipped warship at sea' },
      { date: '2026', event: 'Reactivation and operational employment planned (Capt. Clint Lawler, SNA 2026)' },
      { date: '2027', event: 'CPS live-fire demonstration from ship (GAO, June 2025)' },
    ],
    sisterShips: [
      { name: 'USS Michael Monsoor (DDG-1001)', status: 'Deployed to WESTPAC. CPS modification at Ingalls scheduled 2026-2027.' },
      { name: 'USS Lyndon B. Johnson (DDG-1002)', status: 'Forward gun mount removed. CPS integration underway at Ingalls. Return to service before DDG-1001 enters dry dock 2027.' },
    ],
    basing: 'All 3 Zumwalt-class + up to 3 Virginia-class SSN with CPS to be stationed at Joint Base Pearl Harbor-Hickam, Hawaii by mid-2028.',
    contractValue: 'Lockheed Martin: $2B+ contract (Feb 2023) for CPS weapon system integration on Zumwalt-class.',
  };

  // CPS development timeline — verified from DoD, HII, GAO, USNI, Defense Daily
  cpsMilestones = [
    { date: '2021-2022', event: 'Early booster flight test failures', status: 'failed' },
    { date: 'Mar 2023', event: 'Launch scrubbed pre-flight (mechanical problem with Lockheed launcher)', status: 'failed' },
    { date: 'Aug 2023', event: 'USS Zumwalt arrives Ingalls Shipbuilding, Pascagoula MS for CPS modernization', status: 'success' },
    { date: 'Sep 2023', event: 'Second launch scrubbed pre-flight (same launcher issue)', status: 'failed' },
    { date: 'Mar 2024', event: 'Zumwalt forward 155mm AGS turret removal completed', status: 'success' },
    { date: 'May 2024', event: 'LMVLS foundation installed on Zumwalt', status: 'success' },
    { date: 'Jul-Aug 2024', event: '4 LMVLS tubes (87″ dia each) delivered and installed on Zumwalt', status: 'success' },
    { date: 'Oct 2024', event: 'Basic LMVLS tube installation completed', status: 'success' },
    { date: '2024 (first)', event: 'First successful AUR end-to-end flight test (land-based)', status: 'success' },
    { date: 'Dec 6, 2024', event: 'USS Zumwalt undocked — first CPS-equipped warship back in water', status: 'success' },
    { date: 'Dec 12, 2024', event: 'Second AUR flight test (land TEL, Cape Canaveral). First live-fire from Battery Operations Center + TEL.', status: 'success' },
    { date: 'Nov 2025', event: 'Advanced Payload Module (APM) installation complete on Zumwalt', status: 'success' },
    { date: 'May 2, 2025', event: 'First CPS test using Navy cold-gas launch approach (land-based, Cape Canaveral). End-to-end flight successful.', status: 'success' },
    { date: 'Jan 21, 2026', event: 'HII completes builder\'s sea trials for USS Zumwalt — first CPS platform at sea', status: 'success' },
    { date: '2026', event: 'USS Zumwalt reactivation and operational employment (Capt. Lawler, SNA 2026)', status: 'planned' },
    { date: '2027', event: 'CPS live-fire demonstration from USS Zumwalt (GAO, June 2025)', status: 'planned' },
    { date: '2026-2027', event: 'DDG-1001 Monsoor enters Ingalls for CPS modification', status: 'planned' },
    { date: 'Mid-2028', event: 'All 3 Zumwalts + up to 3 Virginia SSNs with CPS stationed at Pearl Harbor', status: 'planned' },
  ];

  // Cold-gas launch analysis — why it matters for BBG assessment
  coldGasAnalysis = [
    {
      point: 'Cold-gas launch is proven technology',
      detail: 'The same principle has been used for Trident D5 SLBM launches from Ohio-class SSBNs since 1990. Gas generator pressurizes launch tube, ejects missile through water/air, rocket motor ignites at safe distance. SSP — the same office that manages Trident — is leading CPS development.',
    },
    {
      point: 'May 2025 test validated the Navy approach, but from land',
      detail: 'The DoD press release confirms this was "the first launch of the CPS capability utilizing the Navy\'s cold-gas launch approach that will be used in Navy sea-based platform fielding." This was at Cape Canaveral, not from a ship. The "In-Air Launch test facility" simulates shipboard conditions on land.',
    },
    {
      point: 'Ship integration is the remaining hard problem',
      detail: 'Cold-gas eject works. The remaining challenges are: LMVLS structural integration into specific hull types, blast deflection of the solid rocket exhaust above deck, shock/vibration effects on adjacent ship systems, and electromagnetic compatibility with ship radars during launch.',
    },
    {
      point: 'DDG-1000 is already done — BBG has no integration design',
      detail: 'USS Zumwalt completed builder\'s sea trials on Jan 21, 2026 with LMVLS installed. All 4 tubes (87″ dia) and APMs are in. DDG-1002 is in the yard now. Live-fire from ship: 2027. The Trump-class BBG has no hull design, no LMVLS arrangement, and no integration engineering. DDG-1000 will be operational with CPS years before BBG construction could begin.',
    },
    {
      point: 'BBG adds zero CPS capacity over DDG-1000',
      detail: 'Trump-class BBG: 12 CPS cells at $9.1B per hull. DDG-1000 refit: 12 CPS cells at marginal refit cost (hull already paid for at $4.4B sunk). Same CPS loadout. By mid-2028, all 3 Zumwalts (36 CPS total) + Virginia SSNs will be stationed at Pearl Harbor. The BBG\'s 128 Mk 41 cells carry conventional missiles that DDG-51 Flight III already carries at $2.2B. The $9B premium buys size, not capability.',
    },
  ];

  // Platform comparison trade study
  platformOptions: PlatformOption[] = [
    {
      name: 'DDG-1000 Zumwalt (refit)',
      designation: 'DDG-1000',
      cpsCells: 12,
      unitCostB: '~4.4 (sunk)',
      survivability: 'Moderate',
      availability: '3 hulls exist, refitting now',
      notes: 'Both 155mm AGS turrets removed. 4 LMVLS modules (2.2m dia, 3 AURs each) installed on foredeck = 12 CPS. Cost is sunk — marginal cost is refit only. Shipboard live-fire test FY2027-2028.'
    },
    {
      name: 'Virginia Block V SSN',
      designation: 'SSN-774+',
      cpsCells: 4,
      unitCostB: '~3.4',
      survivability: 'High',
      availability: 'Building now, delivery ~2028+',
      notes: 'VPM: 84-ft mid-hull plug adds 4 large-diameter tubes (+2,500 tons displacement). Submarine survivability is highest. Limited to 4 CPS per hull.'
    },
    {
      name: 'Ohio SSGN (if retained)',
      designation: 'SSGN-726',
      cpsCells: '44+',
      unitCostB: '0 (exists)',
      survivability: 'High',
      availability: '4 hulls, retiring 2026-2028',
      notes: '22 launch tubes × 2 canisters each. Highest capacity per hull but hulls are aging out. Retention would require reactor refueling.'
    },
    {
      name: 'Trump-class BBG (Golden Fleet)',
      designation: 'BBG-1',
      cpsCells: 12,
      unitCostB: '~9.1 (CBO est.)',
      survivability: 'Low',
      availability: 'Announced Dec 2025, construction 2030 (planned)',
      notes: '35,000-ton battleship. 128 Mk 41 VLS + 12 CPS. Includes canceled railgun, unfunded SLCM-N. CSIS: "will never sail." Replaces DDG(X). Lead ship ~$13.5B.'
    },
    {
      name: 'DDG-51 Flight III',
      designation: 'DDG-51 Flt III',
      cpsCells: 0,
      unitCostB: '~2.2',
      survivability: 'Moderate',
      availability: 'In production',
      notes: 'Mk 41 VLS cells are 21″ diameter — too small for 34.5″ CPS booster. Cannot carry CPS without new launcher integration.'
    },
  ];

  // LSC-X concept hull specs
  hullSpecs: HullSpec[] = [
    { parameter: 'Displacement', value: '18,000-22,000', unit: 'tons (full load)' },
    { parameter: 'Length', value: '210-230', unit: 'm' },
    { parameter: 'Beam', value: '24-26', unit: 'm' },
    { parameter: 'Draft', value: '8-9', unit: 'm' },
    { parameter: 'Propulsion', value: 'IEP (Integrated Electric)', unit: '' },
    { parameter: 'Speed', value: '30+', unit: 'knots' },
    { parameter: 'CPS Cells', value: '12-20', unit: 'large-diameter' },
    { parameter: 'Mk 41 VLS', value: '64-96', unit: 'cells (self-defense)' },
    { parameter: 'Crew', value: '180-220', unit: 'personnel' },
    { parameter: 'Radar', value: 'AN/SPY-6(V)', unit: '' },
  ];

  // VLS loadout for LSC-X concept
  vlsLoadout: VLSLoadout[] = [
    { missile: 'CPS (LRHW)', cells: 16, role: 'Hypersonic Strike', color: '#e74c3c' },
    { missile: 'SM-6 / SM-3', cells: 48, role: 'Air/Missile Defense', color: '#3498db' },
    { missile: 'ESSM Block 2', cells: 32, role: 'Self-Defense (quad-packed)', color: '#2ecc71' },
    { missile: 'Tomahawk Block V', cells: 16, role: 'Land Attack / Anti-Ship', color: '#f39c12' },
  ];

  // Defense layers for LSC-X concept
  defenseLayers: DefenseLayer[] = [
    { system: 'SM-6 Blk IB', range_km: 370, pk: 0.85, type: 'outer', color: '#3498db' },
    { system: 'SM-3 Blk IIA', range_km: 2500, pk: 0.80, type: 'outer', color: '#9b59b6' },
    { system: 'ESSM Blk 2', range_km: 50, pk: 0.90, type: 'middle', color: '#2ecc71' },
    { system: 'SeaRAM / RAM', range_km: 10, pk: 0.85, type: 'inner', color: '#e67e22' },
    { system: 'CIWS Phalanx', range_km: 1.5, pk: 0.70, type: 'ciws', color: '#e74c3c' },
  ];

  // Engineering constraints for CPS integration — verified
  engineeringConstraints: EngineeringConstraint[] = [
    { category: 'Launcher: LMVLS Required', requirement: 'CPS AUR (34.5″ / 87.6 cm booster, ~12m long) requires Large Missile VLS (LMVLS) — 2.2m diameter tubes. Incompatible with Mk 41 (21″) and Mk 57. DDG-1000 goes "down about 5 platforms" to fit missile height.', status: 'proven' },
    { category: 'Ship Integration Depth', requirement: 'DDG-1000 required removing both 155mm AGS turrets and cutting into the foredeck to install 4 LMVLS modules. BBG would need purpose-built LMVLS bays — no design exists yet.', status: 'proven' },
    { category: 'Cold-Gas Launch', requirement: 'Cold-gas eject pushes AUR clear of ship before solid rocket ignites. Successfully ground-tested (May 2025). NOT yet tested from a ship — first shipboard launch FY2027-2028.', status: 'in-development' },
    { category: 'Exhaust & Blast', requirement: 'Two-stage solid rocket ignition above deck requires blast deflectors and minimum standoff distances from other topside equipment and personnel.', status: 'proven' },
    { category: 'Magazine Safety', requirement: 'Solid rocket motors require Insensitive Munitions (IM) compliance and thermal management below deck.', status: 'proven' },
    { category: 'Targeting & C2', requirement: 'CPS requires external targeting data for full-range (1,725+ mi) shots. Depends on CEC, satellite, or F-35 sensor network. Weapon itself has no seeker for mid-course update.', status: 'proven' },
    { category: 'Reload at Sea', requirement: 'No at-sea reload for LMVLS canisters. Ship must return to port after expending CPS loadout. 12-shot magazine = one salvo.', status: 'proven' },
    { category: 'BBG LMVLS Design', requirement: 'Trump-class BBG announces 12 CPS cells but no LMVLS design exists for a 35,000-ton hull. Only proven integration is DDG-1000 (15,700 tons) and Virginia VPM. BBG would require new LMVLS arrangement — undesigned.', status: 'speculative' },
    { category: 'Acoustic Signature', requirement: 'Surface combatant is inherently noisier than SSN — lower pre-launch survivability vs. submarine-launched CPS.', status: 'proven' },
  ];

  get vlsTotal(): number {
    return this.vlsLoadout.reduce((sum, l) => sum + l.cells, 0);
  }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.renderCostEffectivenessChart();
      this.renderCpsCellComparisonChart();
      this.renderDefenseLayerChart();
    }, 100);
  }

  ngOnDestroy(): void {}

  setActiveSection(id: string): void {
    this.activeSection = id;
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  }

  getStatusClass(status: string): string {
    return `status-${status}`;
  }

  getSurvivabilityClass(level: string): string {
    return `survivability-${level.toLowerCase()}`;
  }

  private renderCostEffectivenessChart(): void {
    if (!this.costEffectivenessChart?.nativeElement) return;

    const el = this.costEffectivenessChart.nativeElement;
    const margin = { top: 30, right: 30, bottom: 60, left: 70 };
    const width = el.clientWidth - margin.left - margin.right;
    const height = 320 - margin.top - margin.bottom;

    d3.select(el).selectAll('*').remove();

    const svg = d3.select(el)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Cost per CPS cell analysis ($M per cell)
    const data = [
      { platform: 'Ohio SSGN\n(retained)', costPerCell: 0, cells: 44, color: '#2ecc71' },
      { platform: 'DDG-1000\n(refit)', costPerCell: 367, cells: 12, color: '#3498db' },
      { platform: 'Virginia\nBlock V', costPerCell: 850, cells: 4, color: '#9b59b6' },
      { platform: 'Trump BBG\n($9.1B)', costPerCell: 758, cells: 12, color: '#e74c3c' },
    ];

    const x = d3.scaleBand().domain(data.map(d => d.platform)).range([0, width]).padding(0.3);
    const y = d3.scaleLinear().domain([0, 1000]).range([height, 0]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('fill', '#94a3b8')
      .style('font-size', '11px');

    svg.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => `$${d}M`))
      .selectAll('text')
      .style('fill', '#94a3b8');

    svg.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => x(d.platform)!)
      .attr('y', d => y(d.costPerCell))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.costPerCell))
      .attr('fill', d => d.color)
      .attr('rx', 4);

    // Cell count labels
    svg.selectAll('.cell-label')
      .data(data)
      .enter()
      .append('text')
      .attr('x', d => x(d.platform)! + x.bandwidth() / 2)
      .attr('y', d => y(d.costPerCell) - 8)
      .attr('text-anchor', 'middle')
      .style('fill', '#e2e8f0')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text(d => d.costPerCell === 0 ? 'Sunk cost' : `$${d.costPerCell}M`);

    svg.append('text')
      .attr('x', width / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('fill', '#e2e8f0')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .text('Estimated Cost per CPS Cell ($M)');
  }

  private renderCpsCellComparisonChart(): void {
    if (!this.cpsCellComparisonChart?.nativeElement) return;

    const el = this.cpsCellComparisonChart.nativeElement;
    const margin = { top: 30, right: 30, bottom: 60, left: 70 };
    const width = el.clientWidth - margin.left - margin.right;
    const height = 320 - margin.top - margin.bottom;

    d3.select(el).selectAll('*').remove();

    const svg = d3.select(el)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const data = [
      { platform: 'Ohio SSGN', cells: 44, color: '#2ecc71', survivability: 3 },
      { platform: 'Trump BBG', cells: 12, color: '#e74c3c', survivability: 1 },
      { platform: 'DDG-1000', cells: 12, color: '#3498db', survivability: 2 },
      { platform: 'Virginia Blk V', cells: 4, color: '#9b59b6', survivability: 3 },
      { platform: 'DDG-51 Flt III', cells: 0, color: '#636e72', survivability: 2 },
    ];

    const x = d3.scaleBand().domain(data.map(d => d.platform)).range([0, width]).padding(0.3);
    const y = d3.scaleLinear().domain([0, 50]).range([height, 0]);

    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('fill', '#94a3b8')
      .style('font-size', '11px');

    svg.append('g')
      .call(d3.axisLeft(y).ticks(5))
      .selectAll('text')
      .style('fill', '#94a3b8');

    svg.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => x(d.platform)!)
      .attr('y', d => y(d.cells))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.cells))
      .attr('fill', d => d.color)
      .attr('rx', 4);

    svg.selectAll('.cell-label')
      .data(data)
      .enter()
      .append('text')
      .attr('x', d => x(d.platform)! + x.bandwidth() / 2)
      .attr('y', d => y(d.cells) - 8)
      .attr('text-anchor', 'middle')
      .style('fill', '#e2e8f0')
      .style('font-size', '13px')
      .style('font-weight', 'bold')
      .text(d => d.cells === 0 ? 'N/A' : `${d.cells}`);

    svg.append('text')
      .attr('x', width / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('fill', '#e2e8f0')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .text('CPS Cells per Platform');
  }

  private renderDefenseLayerChart(): void {
    if (!this.defenseLayerChart?.nativeElement) return;

    const el = this.defenseLayerChart.nativeElement;
    const size = Math.min(el.clientWidth, 400);
    const center = size / 2;

    d3.select(el).selectAll('*').remove();

    const svg = d3.select(el)
      .append('svg')
      .attr('width', size)
      .attr('height', size);

    const maxRange = 370; // SM-6 outer range for scaling
    const scale = (center - 40) / Math.log(maxRange + 1);

    // Draw rings from outside in
    const sortedLayers = [...this.defenseLayers]
      .filter(l => l.type !== 'outer' || l.system === 'SM-6 Blk IB')
      .sort((a, b) => b.range_km - a.range_km);

    sortedLayers.forEach(layer => {
      const r = Math.log(layer.range_km + 1) * scale;
      svg.append('circle')
        .attr('cx', center)
        .attr('cy', center)
        .attr('r', r)
        .attr('fill', 'none')
        .attr('stroke', layer.color)
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '6,3')
        .attr('opacity', 0.6);

      svg.append('text')
        .attr('x', center + r + 4)
        .attr('y', center - 4)
        .style('fill', layer.color)
        .style('font-size', '10px')
        .text(`${layer.system} (${layer.range_km} km)`);
    });

    // Ship icon at center
    svg.append('rect')
      .attr('x', center - 12)
      .attr('y', center - 4)
      .attr('width', 24)
      .attr('height', 8)
      .attr('fill', '#e2e8f0')
      .attr('rx', 3);

    svg.append('text')
      .attr('x', center)
      .attr('y', center + 24)
      .attr('text-anchor', 'middle')
      .style('fill', '#94a3b8')
      .style('font-size', '11px')
      .text('LSC-X');
  }
}
