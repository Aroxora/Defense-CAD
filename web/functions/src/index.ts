/**
 * Golden Fleet War Room - Firebase Cloud Functions
 * Advanced simulation processing, lead scoring, and threat modeling
 */

import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';

admin.initializeApp();
const db = admin.firestore();

// Threat scenario configurations for advanced modeling
const THREAT_CONFIGS = {
  taiwan_strait: {
    china_asbm: { df21d: 8, df26: 4, df27: 4 },
    china_ascm: { yj18: 24, yj12: 12, yj21: 12 },
    hypersonics: 4,
    swarm: 200,
    salvoWaves: 3,
    reattackCapability: true
  },
  south_china_sea: {
    china_asbm: { df21d: 4, df26: 4 },
    china_ascm: { yj18: 12, yj12: 8, yj21: 4 },
    hypersonics: 2,
    swarm: 100,
    salvoWaves: 2,
    reattackCapability: false
  },
  nato_black_sea: {
    russia_hypersonic: { zircon: 4, kinzhal: 4 },
    russia_ascm: { p800: 12, p700: 8 },
    swarm: 50,
    salvoWaves: 2,
    reattackCapability: true
  },
  pacific_deterrence: {
    china_asbm: { df21d: 2, df26: 2 },
    china_ascm: { yj18: 8, yj12: 4 },
    hypersonics: 6,
    swarm: 200,
    salvoWaves: 1,
    reattackCapability: false
  }
};

// Defense system Pk values - using index signature for flexibility
interface DefenseSystem {
  [key: string]: { [key: string]: number } | undefined;
}

const DEFENSE_SYSTEMS: { current: DefenseSystem; goldenFleet: DefenseSystem } = {
  current: {
    sm3_iia: { pk_asbm: 0.53, pk_hypersonic: 0.15, cost: 36000000 },
    sm6: { pk_ascm: 0.85, pk_hypersonic: 0.25, cost: 4300000 },
    essm: { pk_ascm: 0.80, pk_drone: 0.60, cost: 2500000 },
    ram: { pk_ascm: 0.75, pk_drone: 0.70, cost: 1000000 },
    phalanx: { pk_ascm: 0.50, pk_drone: 0.40, cost: 50000 },
    helios_60kw: { pk_drone: 0.70, rate: 10, cost: 10 }
  },
  goldenFleet: {
    sm3_iia: { pk_asbm: 0.85, pk_hypersonic: 0.40, cost: 36000000 },
    thaad_er: { pk_asbm: 0.90, pk_hypersonic: 0.75, cost: 15000000 },
    sm6: { pk_ascm: 0.90, pk_hypersonic: 0.40, cost: 4300000 },
    essm: { pk_ascm: 0.85, pk_drone: 0.70, cost: 2500000 },
    searam: { pk_ascm: 0.80, pk_drone: 0.75, cost: 1000000 },
    hel_600kw: { pk_drone: 0.95, pk_ascm: 0.60, rate: 60, cost: 10 }
  }
};

/**
 * Run advanced Monte Carlo simulation for threat scenarios
 */
export const runAdvancedSimulation = functions.https.onCall(async (data, context) => {
  const { scenarioId, boShangHired, iterations = 1000 } = data;

  if (!scenarioId || !THREAT_CONFIGS[scenarioId as keyof typeof THREAT_CONFIGS]) {
    throw new functions.https.HttpsError('invalid-argument', 'Invalid scenario ID');
  }

  const config = THREAT_CONFIGS[scenarioId as keyof typeof THREAT_CONFIGS];
  const defense = boShangHired ? DEFENSE_SYSTEMS.goldenFleet : DEFENSE_SYSTEMS.current;

  const results = runMonteCarloSimulation(config, defense, iterations);

  // Save to Firestore
  const docRef = await db.collection('advanced_simulations').add({
    timestamp: admin.firestore.FieldValue.serverTimestamp(),
    scenario_id: scenarioId,
    bo_shang_hired: boShangHired,
    iterations,
    results,
    user_id: context.auth?.uid || 'anonymous'
  });

  return {
    simulationId: docRef.id,
    results
  };
});

function runMonteCarloSimulation(
  config: any,
  defense: any,
  iterations: number
): any {
  let totalLeakers = 0;
  let totalIntercepted = 0;
  let carriersLostSum = 0;
  let costSum = 0;
  const outcomeDistribution: number[] = [];

  for (let i = 0; i < iterations; i++) {
    const { leakers, intercepted, carriersLost, cost } = simulateSingleEngagement(config, defense);
    totalLeakers += leakers;
    totalIntercepted += intercepted;
    carriersLostSum += carriersLost;
    costSum += cost;
    outcomeDistribution.push(carriersLost);
  }

  // Calculate statistics
  const avgLeakers = totalLeakers / iterations;
  const avgIntercepted = totalIntercepted / iterations;
  const avgCarriersLost = carriersLostSum / iterations;
  const avgCost = costSum / iterations;

  // Calculate confidence intervals
  const sortedOutcomes = outcomeDistribution.sort((a, b) => a - b);
  const ci95Low = sortedOutcomes[Math.floor(iterations * 0.025)];
  const ci95High = sortedOutcomes[Math.floor(iterations * 0.975)];
  const median = sortedOutcomes[Math.floor(iterations * 0.5)];

  return {
    average: {
      leakers: avgLeakers,
      intercepted: avgIntercepted,
      carriersLost: avgCarriersLost,
      costMillions: avgCost / 1000000
    },
    confidence95: {
      low: ci95Low,
      high: ci95High,
      median
    },
    survivabilityRate: 1 - (avgCarriersLost / 3),
    effectivenessScore: (avgIntercepted / (avgLeakers + avgIntercepted)) * 100
  };
}

function simulateSingleEngagement(config: any, defense: DefenseSystem): any {
  let threats = 0;
  let leakers = 0;
  let intercepted = 0;
  let cost = 0;

  // Helper to get values safely
  const get = (sys: string, prop: string, defaultVal: number) =>
    defense[sys]?.[prop] ?? defaultVal;

  // Process ASBMs
  if (config.china_asbm) {
    for (const [, count] of Object.entries(config.china_asbm)) {
      for (let i = 0; i < (count as number); i++) {
        threats++;
        const pkFirst = get('sm3_iia', 'pk_asbm', 0.22);
        const pkSecond = get('thaad_er', 'pk_asbm', 0);

        // Two-shot doctrine
        const pMiss = (1 - pkFirst) * (1 - pkFirst) * (1 - pkSecond) * (1 - pkSecond);
        if (Math.random() > pMiss) {
          intercepted++;
          cost += (get('sm3_iia', 'cost', 36000000)) * 2;
        } else {
          leakers++;
        }
      }
    }
  }

  // Process ASCMs
  const ascmTypes = config.china_ascm || config.russia_ascm || {};
  for (const [, count] of Object.entries(ascmTypes)) {
    for (let i = 0; i < (count as number); i++) {
      threats++;
      const pkSm6 = get('sm6', 'pk_ascm', 0.85);
      const pkEssm = get('essm', 'pk_ascm', 0.80);
      const pkRam = get('searam', 'pk_ascm', get('ram', 'pk_ascm', 0.75));

      const pMiss = (1 - pkSm6) * (1 - pkEssm) * (1 - pkRam);
      if (Math.random() > pMiss) {
        intercepted++;
        cost += get('sm6', 'cost', 4300000);
      } else {
        leakers++;
      }
    }
  }

  // Process Hypersonics
  const hypersonicCount = config.hypersonics || 0;
  for (let i = 0; i < hypersonicCount; i++) {
    threats++;
    const pkHyper = get('thaad_er', 'pk_hypersonic', get('sm6', 'pk_hypersonic', 0.15));
    const pMiss = (1 - pkHyper) * (1 - pkHyper);

    if (Math.random() > pMiss) {
      intercepted++;
      cost += get('thaad_er', 'cost', get('sm6', 'cost', 15000000));
    } else {
      leakers++;
    }
  }

  // Calculate carrier losses (1 leaker can mission-kill, 2+ likely sinks)
  const carriersLost = Math.min(3, Math.floor(leakers / 2));

  return { threats, leakers, intercepted, cost, carriersLost };
}

/**
 * Score leads based on simulation engagement
 */
export const scoreLeadFromSimulation = functions.firestore
  .document('war_room_simulations/{simId}')
  .onCreate(async (snapshot, context) => {
    const data = snapshot.data();

    let score = 0;
    const factors: string[] = [];

    // Session duration scoring
    const sessionDuration = data.user_context?.session_duration_seconds || 0;
    if (sessionDuration > 300) {
      score += 20;
      factors.push('Extended session (5+ minutes)');
    }
    if (sessionDuration > 600) {
      score += 15;
      factors.push('Deep engagement (10+ minutes)');
    }

    // Simulation completion
    score += 25;
    factors.push('Completed simulation');

    // Bo Shang hired toggle
    if (data.bo_shang_hired) {
      score += 30;
      factors.push('Explored Bo Shang solution');
    }

    // Multiple interactions
    const interactions = data.user_context?.interaction_count || 0;
    if (interactions > 20) {
      score += 15;
      factors.push('High interaction count');
    }

    // Referrer analysis
    const referrer = data.user_context?.referrer || '';
    if (referrer.includes('.mil') || referrer.includes('.gov')) {
      score += 50;
      factors.push('Government/military referrer');
    }

    // Determine lead quality
    let quality: string;
    if (score >= 100) quality = 'HOT';
    else if (score >= 70) quality = 'WARM';
    else if (score >= 40) quality = 'QUALIFIED';
    else quality = 'NURTURE';

    // Update document with lead score
    await snapshot.ref.update({
      lead_score: {
        score,
        quality,
        factors,
        scored_at: admin.firestore.FieldValue.serverTimestamp()
      }
    });

    // If hot lead, create alert
    if (quality === 'HOT') {
      await db.collection('hot_lead_alerts').add({
        simulation_id: context.params.simId,
        score,
        factors,
        scenario: data.scenario_name,
        timestamp: admin.firestore.FieldValue.serverTimestamp(),
        notified: false
      });
    }

    return { score, quality };
  });

/**
 * Calculate daily analytics summary
 */
export const dailyAnalyticsSummary = functions.pubsub
  .schedule('0 0 * * *')
  .timeZone('America/New_York')
  .onRun(async (context) => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    yesterday.setHours(0, 0, 0, 0);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const simulations = await db.collection('war_room_simulations')
      .where('timestamp', '>=', yesterday)
      .where('timestamp', '<', today)
      .get();

    const inquiries = await db.collection('golden_fleet_inquiries')
      .where('submittedAt', '>=', yesterday.toISOString())
      .where('submittedAt', '<', today.toISOString())
      .get();

    let boShangHiredCount = 0;
    let currentPathCount = 0;
    let totalCarriersLost = 0;

    simulations.forEach(doc => {
      const data = doc.data();
      if (data.bo_shang_hired) boShangHiredCount++;
      else currentPathCount++;
      totalCarriersLost += data.summary?.total_carriers_lost || 0;
    });

    const summary = {
      date: yesterday.toISOString().split('T')[0],
      simulations: {
        total: simulations.size,
        bo_shang_hired: boShangHiredCount,
        current_path: currentPathCount,
        avg_carriers_lost: simulations.size > 0 ? totalCarriersLost / simulations.size : 0
      },
      inquiries: {
        total: inquiries.size
      },
      conversion_rate: simulations.size > 0 ? (inquiries.size / simulations.size) * 100 : 0
    };

    await db.collection('daily_analytics').add({
      ...summary,
      timestamp: admin.firestore.FieldValue.serverTimestamp()
    });

    console.log('Daily analytics summary:', summary);
    return summary;
  });

/**
 * HTTP endpoint for real-time threat modeling
 */
export const modelThreat = functions.https.onRequest(async (req, res) => {
  // CORS
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).send('Method not allowed');
    return;
  }

  const { threatType, count, defenseConfig } = req.body;

  if (!threatType || !count) {
    res.status(400).json({ error: 'Missing threatType or count' });
    return;
  }

  const defense = defenseConfig === 'golden_fleet'
    ? DEFENSE_SYSTEMS.goldenFleet
    : DEFENSE_SYSTEMS.current;

  // Helper to get values safely
  const get = (sys: string, prop: string, defaultVal: number) =>
    defense[sys]?.[prop] ?? defaultVal;

  let pkTotal = 0;

  switch (threatType) {
    case 'asbm':
      const pkAsbm = 1 - Math.pow(1 - get('sm3_iia', 'pk_asbm', 0.53), 2);
      const thaadPk = get('thaad_er', 'pk_asbm', 0);
      const pkThaad = thaadPk > 0 ? 1 - Math.pow(1 - thaadPk, 2) : 0;
      pkTotal = 1 - (1 - pkAsbm) * (1 - pkThaad);
      break;

    case 'ascm':
      pkTotal = 1 - (1 - get('sm6', 'pk_ascm', 0.85))
                  * (1 - get('essm', 'pk_ascm', 0.80))
                  * (1 - get('searam', 'pk_ascm', get('ram', 'pk_ascm', 0.75)));
      break;

    case 'hypersonic':
      pkTotal = 1 - Math.pow(1 - get('thaad_er', 'pk_hypersonic', get('sm6', 'pk_hypersonic', 0.15)), 2);
      break;

    case 'drone':
      pkTotal = get('hel_600kw', 'pk_drone', get('helios_60kw', 'pk_drone', 0.70));
      break;
  }

  const expectedLeakers = count * (1 - pkTotal);
  const expectedIntercepted = count * pkTotal;
  const salvoSurvivability = Math.pow(pkTotal, count);

  res.json({
    threatType,
    count,
    defenseConfig: defenseConfig || 'current',
    results: {
      single_shot_pk: pkTotal,
      expected_leakers: expectedLeakers,
      expected_intercepted: expectedIntercepted,
      salvo_survivability: salvoSurvivability,
      carrier_risk: expectedLeakers >= 2 ? 'HIGH' : expectedLeakers >= 1 ? 'MODERATE' : 'LOW'
    }
  });
});
