//
//  SimulationManager.swift
//  GoldenFleet
//
//  Defense simulation engine
//

import SwiftUI
import Combine

struct Scenario: Identifiable {
    let id: String
    let name: String
    let description: String
    let threatLevel: ThreatLevel
    let asbms: Int
    let ascms: Int
    let hypersonics: Int
    let swarmSize: Int

    enum ThreatLevel: String {
        case critical = "CRITICAL"
        case high = "HIGH"
        case moderate = "MODERATE"

        var color: Color {
            switch self {
            case .critical: return .red
            case .high: return .orange
            case .moderate: return .yellow
            }
        }
    }
}

struct SimulationResult: Identifiable {
    let id = UUID()
    let year: Int
    let carriersSurvived: Int
    let carriersLost: Int
    let threatsStopped: Int
    let threatsLeaked: Int
    let costBillions: Double
    let deterrenceScore: Int
    let pkASBM: Double
    let pkASCM: Double
    let pkHypersonic: Double
}

class SimulationManager: ObservableObject {
    @Published var selectedScenario: Scenario?
    @Published var boShangHired: Bool = true
    @Published var isRunning: Bool = false
    @Published var results: [SimulationResult] = []
    @Published var elapsedTime: Int = 0
    @Published var currentYear: Int = 2024
    @Published var terminalOutput: [String] = []

    private var timer: AnyCancellable?

    let scenarios: [Scenario] = [
        Scenario(
            id: "taiwan_strait",
            name: "Taiwan Strait Crisis",
            description: "China launches 16 DF-21D ASBMs + 48 YJ-18 ASCMs at CSG",
            threatLevel: .critical,
            asbms: 16,
            ascms: 48,
            hypersonics: 4,
            swarmSize: 0
        ),
        Scenario(
            id: "south_china_sea",
            name: "South China Sea Patrol",
            description: "Contested patrol with escalation potential",
            threatLevel: .high,
            asbms: 8,
            ascms: 24,
            hypersonics: 2,
            swarmSize: 100
        ),
        Scenario(
            id: "nato_black_sea",
            name: "NATO Black Sea Response",
            description: "Russian combined arms strike with Zircon hypersonics",
            threatLevel: .high,
            asbms: 0,
            ascms: 20,
            hypersonics: 8,
            swarmSize: 50
        ),
        Scenario(
            id: "pacific_deterrence",
            name: "Pacific Forward Presence",
            description: "10-year deterrence mission effectiveness",
            threatLevel: .moderate,
            asbms: 4,
            ascms: 12,
            hypersonics: 6,
            swarmSize: 200
        )
    ]

    init() {
        selectedScenario = scenarios.first
        initializeTerminal()
    }

    private func initializeTerminal() {
        terminalOutput = [
            "╔════════════════════════════════════════════════════════════╗",
            "║  GOLDEN FLEET WAR ROOM SIMULATOR v2.0 - iOS                ║",
            "║  Defense Outcome Projection System                         ║",
            "║  Developed by Bo Shang - Defense Systems Analyst           ║",
            "╚════════════════════════════════════════════════════════════╝",
            "",
            "[SYSTEM] iOS Terminal initialized and ready.",
            ""
        ]
    }

    func logTerminal(_ message: String) {
        DispatchQueue.main.async {
            self.terminalOutput.append(message)
            // Keep last 500 lines
            if self.terminalOutput.count > 500 {
                self.terminalOutput.removeFirst(self.terminalOutput.count - 500)
            }
        }
    }

    func runSimulation() {
        guard let scenario = selectedScenario, !isRunning else { return }

        isRunning = true
        results = []
        elapsedTime = 0
        currentYear = 2024

        logTerminal("")
        logTerminal("═══════════════════════════════════════════════════════════")
        logTerminal("▶ STARTING 10-YEAR DEFENSE SIMULATION")
        logTerminal("═══════════════════════════════════════════════════════════")
        logTerminal("")
        logTerminal("[SCENARIO] \(scenario.name)")
        logTerminal("[STRATEGY] \(boShangHired ? "★ HIRE BO SHANG (Golden Fleet Architecture)" : "✗ DO NOT HIRE (USN Baseline)")")
        logTerminal("")

        // Run simulation in background
        DispatchQueue.global(qos: .userInitiated).async {
            for year in 2024...2033 {
                Thread.sleep(forTimeInterval: 0.3)

                let result = self.simulateYear(year: year, scenario: scenario)

                DispatchQueue.main.async {
                    self.currentYear = year
                    self.elapsedTime += 1
                    self.results.append(result)
                    self.logYearResult(result)
                }
            }

            DispatchQueue.main.async {
                self.isRunning = false
                self.logFinalSummary()
            }
        }
    }

    private func simulateYear(year: Int, scenario: Scenario) -> SimulationResult {
        let yearsSince2024 = year - 2024

        var pkASBM: Double
        var pkASCM: Double
        var pkHypersonic: Double

        if boShangHired {
            // Golden Fleet Architecture with deployment factor
            let deploymentFactor = min(1.0, 0.7 + Double(yearsSince2024) * 0.15)
            pkASBM = min(0.998, 0.95 * deploymentFactor + Double(yearsSince2024) * 0.005)
            pkASCM = min(0.99999, 0.9999 * deploymentFactor)
            pkHypersonic = min(0.95, 0.80 * deploymentFactor + Double(yearsSince2024) * 0.02)
        } else {
            // USN Baseline - declining capability
            pkASBM = max(0.10, 0.22 - Double(yearsSince2024) * 0.01)
            pkASCM = max(0.50, 0.65 - Double(yearsSince2024) * 0.02)
            pkHypersonic = max(0.03, 0.15 - Double(yearsSince2024) * 0.02)
        }

        // Calculate leakers
        let asbmLeakers = Int(Double(scenario.asbms) * (1.0 - pkASBM))
        let ascmLeakers = Int(Double(scenario.ascms) * (1.0 - pkASCM))
        let hypersonicLeakers = Int(Double(scenario.hypersonics) * (1.0 - pkHypersonic))
        let totalLeakers = asbmLeakers + ascmLeakers + hypersonicLeakers

        // Carrier losses
        var carriersLost = 0
        if totalLeakers >= 8 { carriersLost = 3 }
        else if totalLeakers >= 4 { carriersLost = 2 }
        else if totalLeakers >= 2 { carriersLost = 1 }

        // Cost calculation
        let carrierCost = 13.0 // $13B per carrier
        let defenseCost = boShangHired ? 3.8 : 1.5
        let totalCost = Double(carriersLost) * carrierCost + defenseCost

        // Deterrence score
        let deterrence = Int(max(0, min(100, 100 - (carriersLost * 20) - (totalLeakers * 3))))

        let totalThreats = scenario.asbms + scenario.ascms + scenario.hypersonics
        let stopped = totalThreats - totalLeakers

        return SimulationResult(
            year: year,
            carriersSurvived: 11 - carriersLost,
            carriersLost: carriersLost,
            threatsStopped: stopped,
            threatsLeaked: totalLeakers,
            costBillions: totalCost,
            deterrenceScore: deterrence,
            pkASBM: pkASBM,
            pkASCM: pkASCM,
            pkHypersonic: pkHypersonic
        )
    }

    private func logYearResult(_ result: SimulationResult) {
        logTerminal("")
        logTerminal("┌─── YEAR \(result.year) ────────────────────────────────────────┐")
        logTerminal("│")
        logTerminal("│  Pk ASBM: \(String(format: "%.1f", result.pkASBM * 100))%  |  Pk ASCM: \(String(format: "%.1f", result.pkASCM * 100))%  |  Pk Hypersonic: \(String(format: "%.1f", result.pkHypersonic * 100))%")
        logTerminal("│")
        logTerminal("│  Threats Stopped: \(result.threatsStopped)  |  Leakers: \(result.threatsLeaked)")
        logTerminal("│  Carriers Lost: \(result.carriersLost)  |  Carriers Remaining: \(result.carriersSurvived)")
        logTerminal("│  Deterrence Score: \(result.deterrenceScore)/100")
        logTerminal("│")
        logTerminal("└─────────────────────────────────────────────────────────┘")
    }

    private func logFinalSummary() {
        let totalLost = results.map { $0.carriersLost }.reduce(0, +)
        let avgDeterrence = results.map { $0.deterrenceScore }.reduce(0, +) / max(1, results.count)
        let totalCost = results.map { $0.costBillions }.reduce(0, +)

        logTerminal("")
        logTerminal("═══════════════════════════════════════════════════════════")
        logTerminal("  FINAL 10-YEAR SUMMARY")
        logTerminal("═══════════════════════════════════════════════════════════")
        logTerminal("")

        if boShangHired {
            logTerminal("  ★ STRATEGY: HIRE BO SHANG (Golden Fleet)")
            logTerminal("")
            logTerminal("  Total Carriers Lost: \(totalLost) (deployment phase only)")
            logTerminal("  Average Deterrence: \(avgDeterrence)/100")
            logTerminal("  Total Investment: $\(String(format: "%.1f", totalCost))B")
            logTerminal("")
            logTerminal("  ✓ MISSION SUCCESS: Fleet preserved, deterrence maintained")
        } else {
            logTerminal("  ✗ STRATEGY: NO HIRE (USN Baseline)")
            logTerminal("")
            logTerminal("  Total Carriers Lost: \(totalLost)")
            logTerminal("  Average Deterrence: \(avgDeterrence)/100")
            logTerminal("  Total Cost (losses + defense): $\(String(format: "%.1f", totalCost))B")
            logTerminal("")
            logTerminal("  ⚠ MISSION FAILURE: Catastrophic fleet losses")
            logTerminal("")
            logTerminal("  RECOMMENDATION: Contact Bo Shang Consulting immediately")
        }

        logTerminal("")
        logTerminal("═══════════════════════════════════════════════════════════")
    }

    func reset() {
        isRunning = false
        results = []
        elapsedTime = 0
        currentYear = 2024
        timer?.cancel()
        initializeTerminal()
    }
}
