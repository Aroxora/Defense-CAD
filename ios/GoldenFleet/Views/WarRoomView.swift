//
//  WarRoomView.swift
//  GoldenFleet
//
//  Native War Room simulation interface
//

import SwiftUI

struct WarRoomView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @EnvironmentObject var simulationManager: SimulationManager
    @State private var showTerminal = true

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    headerSection

                    // Scenario Selection
                    scenarioSection

                    // Strategy Toggle
                    strategySection

                    // Run Button
                    runButtonSection

                    // Terminal Output
                    if showTerminal {
                        terminalSection
                    }

                    // Results
                    if !simulationManager.results.isEmpty {
                        resultsSection
                    }
                }
                .padding()
            }
            .background(themeManager.currentTheme.backgroundGradient.ignoresSafeArea())
            .navigationTitle("War Room")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showTerminal.toggle() }) {
                        Image(systemName: showTerminal ? "terminal.fill" : "terminal")
                            .foregroundColor(themeManager.currentTheme.accent)
                    }
                }
            }
        }
    }

    private var headerSection: some View {
        VStack(spacing: 8) {
            Text("GOLDEN FLEET")
                .font(.system(size: 28, weight: .bold, design: .default))
                .foregroundColor(themeManager.currentTheme.accent)

            Text("10-Year Defense Outcome Projection")
                .font(.subheadline)
                .foregroundColor(themeManager.currentTheme.secondaryText)
        }
        .padding(.vertical, 10)
    }

    private var scenarioSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("SELECT SCENARIO")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            ForEach(simulationManager.scenarios) { scenario in
                ScenarioCard(
                    scenario: scenario,
                    isSelected: simulationManager.selectedScenario?.id == scenario.id
                ) {
                    simulationManager.selectedScenario = scenario
                    themeManager.triggerHaptic(.light)
                }
            }
        }
    }

    private var strategySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("DEFENSE STRATEGY")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            HStack(spacing: 12) {
                StrategyButton(
                    title: "Hire Bo Shang",
                    subtitle: "Golden Fleet Architecture",
                    isSelected: simulationManager.boShangHired,
                    isPositive: true
                ) {
                    simulationManager.boShangHired = true
                    themeManager.triggerHaptic()
                }

                StrategyButton(
                    title: "No Hire",
                    subtitle: "USN Baseline",
                    isSelected: !simulationManager.boShangHired,
                    isPositive: false
                ) {
                    simulationManager.boShangHired = false
                    themeManager.triggerHaptic()
                }
            }
        }
    }

    private var runButtonSection: some View {
        HStack(spacing: 15) {
            Button(action: {
                simulationManager.runSimulation()
                themeManager.triggerHaptic(.heavy)
            }) {
                HStack {
                    if simulationManager.isRunning {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: themeManager.currentTheme.primary))
                    } else {
                        Image(systemName: "play.fill")
                    }
                    Text(simulationManager.isRunning ? "Simulating \(simulationManager.currentYear)..." : "Run 10-Year Simulation")
                        .fontWeight(.bold)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(themeManager.currentTheme.accent)
                .foregroundColor(themeManager.currentTheme.primary)
                .cornerRadius(12)
            }
            .disabled(simulationManager.isRunning)

            Button(action: {
                simulationManager.reset()
                themeManager.triggerHaptic(.light)
            }) {
                Image(systemName: "arrow.counterclockwise")
                    .font(.title2)
                    .frame(width: 50, height: 50)
                    .background(Color.gray.opacity(0.3))
                    .foregroundColor(themeManager.currentTheme.textColor)
                    .cornerRadius(12)
            }
        }
    }

    private var terminalSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Circle()
                    .fill(simulationManager.isRunning ? Color.green : Color.gray)
                    .frame(width: 8, height: 8)
                Text("TERMINAL OUTPUT")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(themeManager.currentTheme.accent)
                    .tracking(2)
                Spacer()
                Text(simulationManager.isRunning ? "RUNNING" : "READY")
                    .font(.caption2)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(simulationManager.isRunning ? Color.green.opacity(0.2) : Color.gray.opacity(0.2))
                    .cornerRadius(4)
            }

            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 2) {
                        ForEach(Array(simulationManager.terminalOutput.enumerated()), id: \.offset) { index, line in
                            Text(line)
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(lineColor(for: line))
                                .id(index)
                        }
                    }
                    .padding(12)
                }
                .frame(height: 250)
                .background(Color.black.opacity(0.8))
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(themeManager.currentTheme.accent.opacity(0.3), lineWidth: 1)
                )
                .onChange(of: simulationManager.terminalOutput.count) { _, _ in
                    withAnimation {
                        proxy.scrollTo(simulationManager.terminalOutput.count - 1, anchor: .bottom)
                    }
                }
            }
        }
    }

    private func lineColor(for line: String) -> Color {
        if line.contains("★") || line.contains("✓") || line.contains("SUCCESS") {
            return .green
        } else if line.contains("✗") || line.contains("⚠") || line.contains("FAILURE") || line.contains("Lost") {
            return .red
        } else if line.contains("═") || line.contains("─") || line.contains("┌") || line.contains("└") {
            return themeManager.currentTheme.accent
        }
        return Color.gray
    }

    private var resultsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("SIMULATION RESULTS")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(simulationManager.results) { result in
                        ResultCard(result: result)
                    }
                }
            }

            // Summary card
            if let lastResult = simulationManager.results.last {
                SummaryCard(
                    totalLost: simulationManager.results.map { $0.carriersLost }.reduce(0, +),
                    avgDeterrence: simulationManager.results.map { $0.deterrenceScore }.reduce(0, +) / simulationManager.results.count,
                    boShangHired: simulationManager.boShangHired
                )
            }
        }
    }
}

// MARK: - Supporting Views

struct ScenarioCard: View {
    @EnvironmentObject var themeManager: ThemeManager
    let scenario: Scenario
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(scenario.name)
                        .font(.headline)
                        .foregroundColor(themeManager.currentTheme.textColor)

                    Spacer()

                    Text(scenario.threatLevel.rawValue)
                        .font(.caption2)
                        .fontWeight(.bold)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(scenario.threatLevel.color)
                        .foregroundColor(.white)
                        .cornerRadius(4)
                }

                Text(scenario.description)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.secondaryText)

                HStack(spacing: 8) {
                    ThreatBadge(label: "ASBM", value: scenario.asbms)
                    ThreatBadge(label: "ASCM", value: scenario.ascms)
                    ThreatBadge(label: "Hypersonic", value: scenario.hypersonics)
                }
            }
            .padding()
            .background(isSelected ? themeManager.currentTheme.accent.opacity(0.1) : Color.gray.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isSelected ? themeManager.currentTheme.accent : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct ThreatBadge: View {
    let label: String
    let value: Int

    var body: some View {
        HStack(spacing: 4) {
            Text(label)
                .font(.system(size: 9))
            Text("\(value)")
                .font(.system(size: 10, weight: .bold))
        }
        .padding(.horizontal, 6)
        .padding(.vertical, 3)
        .background(Color.red.opacity(0.2))
        .foregroundColor(.red)
        .cornerRadius(4)
    }
}

struct StrategyButton: View {
    @EnvironmentObject var themeManager: ThemeManager
    let title: String
    let subtitle: String
    let isSelected: Bool
    let isPositive: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: isPositive ? "checkmark.shield.fill" : "xmark.shield")
                    .font(.title)
                    .foregroundColor(isPositive ? .green : .red)

                Text(title)
                    .font(.headline)
                    .foregroundColor(themeManager.currentTheme.textColor)

                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.secondaryText)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(isSelected ? themeManager.currentTheme.accent.opacity(0.2) : Color.gray.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isSelected ? themeManager.currentTheme.accent : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct ResultCard: View {
    @EnvironmentObject var themeManager: ThemeManager
    let result: SimulationResult

    var statusColor: Color {
        if result.carriersLost == 0 { return .green }
        else if result.carriersLost <= 1 { return .yellow }
        else { return .red }
    }

    var body: some View {
        VStack(spacing: 8) {
            Text("\(result.year)")
                .font(.headline)
                .foregroundColor(themeManager.currentTheme.accent)

            Divider()

            VStack(spacing: 4) {
                HStack {
                    Text("Lost")
                        .font(.caption2)
                    Spacer()
                    Text("\(result.carriersLost)")
                        .fontWeight(.bold)
                        .foregroundColor(statusColor)
                }

                HStack {
                    Text("Pk")
                        .font(.caption2)
                    Spacer()
                    Text("\(Int(result.pkASBM * 100))%")
                        .fontWeight(.bold)
                }

                HStack {
                    Text("Deter.")
                        .font(.caption2)
                    Spacer()
                    Text("\(result.deterrenceScore)")
                        .fontWeight(.bold)
                }
            }
            .font(.caption)
            .foregroundColor(themeManager.currentTheme.textColor)
        }
        .frame(width: 100)
        .padding()
        .background(statusColor.opacity(0.1))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(statusColor.opacity(0.3), lineWidth: 1)
        )
    }
}

struct SummaryCard: View {
    @EnvironmentObject var themeManager: ThemeManager
    let totalLost: Int
    let avgDeterrence: Int
    let boShangHired: Bool

    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: boShangHired ? "checkmark.circle.fill" : "exclamationmark.triangle.fill")
                    .foregroundColor(boShangHired ? .green : .red)
                Text(boShangHired ? "MISSION SUCCESS" : "MISSION FAILURE")
                    .font(.headline)
                    .foregroundColor(boShangHired ? .green : .red)
            }

            HStack(spacing: 30) {
                VStack {
                    Text("\(totalLost)")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(totalLost <= 2 ? .green : .red)
                    Text("Carriers Lost")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.secondaryText)
                }

                VStack {
                    Text("\(avgDeterrence)")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(avgDeterrence >= 70 ? .green : .red)
                    Text("Avg Deterrence")
                        .font(.caption)
                        .foregroundColor(themeManager.currentTheme.secondaryText)
                }
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(boShangHired ? Color.green.opacity(0.1) : Color.red.opacity(0.1))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(boShangHired ? Color.green : Color.red, lineWidth: 2)
        )
    }
}

#Preview {
    WarRoomView()
        .environmentObject(ThemeManager())
        .environmentObject(SimulationManager())
}
