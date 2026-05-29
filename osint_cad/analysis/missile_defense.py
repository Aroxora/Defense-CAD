#!/usr/bin/env python3
"""
Missile-Defense Engagement & Exchange-Ratio CAD (defensive / analytical).

Two coupled questions, both defensive and both useful for budget/force study:

  1) ENGAGEMENT: against a raid of M threats, with an interceptor of single-shot kill
     probability Pk fired in salvos of n per threat, how many leak through -- accounting for
     a finite interceptor magazine?
  2) COST-IMPOSITION: what is the cost-exchange ratio (defender $ spent per threat $)?
     A ratio > 1 means the threat imposes cost on the defender; < 1 means defense is the
     cheaper side of the trade.

This is operations-research for sizing defenses and budgets -- NOT operational guidance.

Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE
"""

from dataclasses import dataclass


@dataclass
class Interceptor:
    name: str
    pk_single_shot: float        # single-shot kill probability (0-1)
    unit_cost_musd: float        # per-interceptor cost (USD millions)
    magazine: int                # total interceptors available in the engagement


@dataclass
class Threat:
    name: str
    count: int                   # raid size
    unit_cost_musd: float        # per-threat cost (USD millions)


def kill_prob_salvo(pk: float, shots: int) -> float:
    """Probability of killing one target with `shots` independent interceptors."""
    return 1.0 - (1.0 - pk) ** max(0, shots)


def engage(interceptor: Interceptor, threat: Threat, shots_per_target: int = 2) -> dict:
    """Engagement outcome for a raid given a salvo policy and a finite magazine."""
    pk_target = kill_prob_salvo(interceptor.pk_single_shot, shots_per_target)
    engageable = interceptor.magazine // max(1, shots_per_target)
    engaged = min(threat.count, engageable)
    unengaged = threat.count - engaged                      # leak entirely (magazine empty)
    leakers = unengaged + engaged * (1.0 - pk_target)       # + statistical leakers
    interceptors_fired = engaged * shots_per_target
    return {
        "shots_per_target": shots_per_target,
        "pk_per_target": round(pk_target, 4),
        "engageable_targets": engageable,
        "engaged": engaged,
        "magazine_exhausted": unengaged > 0,
        "expected_leakers": round(leakers, 2),
        "interceptors_fired": interceptors_fired,
        "intercept_fraction": round(1.0 - leakers / threat.count, 4) if threat.count else 0.0,
    }


def exchange_ratio(interceptor: Interceptor, threat: Threat, shots_per_target: int = 2) -> dict:
    """Cost-exchange ratio: defender $ per threat $ to achieve a kill."""
    pk_target = kill_prob_salvo(interceptor.pk_single_shot, shots_per_target)
    # expected interceptors expended per successful kill
    per_kill = (shots_per_target / pk_target) if pk_target > 0 else float("inf")
    defender_cost_per_kill = per_kill * interceptor.unit_cost_musd
    ratio = defender_cost_per_kill / threat.unit_cost_musd if threat.unit_cost_musd else float("inf")
    return {
        "interceptors_per_kill": round(per_kill, 2),
        "defender_cost_per_kill_musd": round(defender_cost_per_kill, 1),
        "threat_unit_cost_musd": threat.unit_cost_musd,
        "cost_exchange_ratio": round(ratio, 2),     # >1 = threat imposes cost on defender
        "favorable_for_defender": bool(ratio < 1.0),
    }


def report(interceptor: Interceptor, threat: Threat, shots_per_target: int = 2) -> str:
    e = engage(interceptor, threat, shots_per_target)
    x = exchange_ratio(interceptor, threat, shots_per_target)
    verdict = "FAVORABLE (defense is the cheaper side)" if x["favorable_for_defender"] \
        else "UNFAVORABLE (threat imposes cost on the defender)"
    return "\n".join([
        "=" * 80,
        f"MISSILE-DEFENSE CAD: {interceptor.name} vs {threat.count}x {threat.name}",
        "Defensive engagement + cost-imposition study. NOT operational guidance.",
        "=" * 80,
        f"  Salvo policy            : {shots_per_target} interceptors/target",
        f"  Pk (single / salvo)     : {interceptor.pk_single_shot:.2f} / {e['pk_per_target']:.2f}",
        f"  Magazine                : {interceptor.magazine} interceptors "
        f"({e['engageable_targets']} targets engageable)",
        f"  Engaged / raid          : {e['engaged']} / {threat.count}"
        + ("  [MAGAZINE EXHAUSTED]" if e['magazine_exhausted'] else ""),
        f"  Expected leakers        : {e['expected_leakers']} "
        f"({e['intercept_fraction']:.0%} intercepted)",
        "-" * 80,
        f"  Interceptors per kill   : {x['interceptors_per_kill']}",
        f"  Defender $ per kill      : ${x['defender_cost_per_kill_musd']}M "
        f"vs ${x['threat_unit_cost_musd']}M threat",
        f"  Cost-exchange ratio     : {x['cost_exchange_ratio']}  -> {verdict}",
        "=" * 80,
    ])


def _demo():
    # Illustrative OSINT order-of-magnitude figures.
    sm6 = Interceptor("SM-6-class interceptor", pk_single_shot=0.70, unit_cost_musd=4.3, magazine=48)
    ascm = Threat("subsonic ASCM", count=24, unit_cost_musd=1.5)
    print(report(sm6, ascm, shots_per_target=2))


if __name__ == "__main__":
    _demo()
