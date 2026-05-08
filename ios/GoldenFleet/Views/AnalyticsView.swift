//
//  AnalyticsView.swift
//  GoldenFleet
//
//  Defense analytics and statistics display
//

import SwiftUI
import Charts

struct AnalyticsView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @EnvironmentObject var simulationManager: SimulationManager

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    if simulationManager.results.isEmpty {
                        emptyStateView
                    } else {
                        // Pk Over Time Chart
                        pkChartSection

                        // Carrier Status Chart
                        carrierChartSection

                        // Deterrence Chart
                        deterrenceChartSection

                        // Statistics Grid
                        statisticsGrid
                    }
                }
                .padding()
            }
            .background(themeManager.currentTheme.backgroundGradient.ignoresSafeArea())
            .navigationTitle("Analytics")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "chart.bar.xaxis")
                .font(.system(size: 60))
                .foregroundColor(themeManager.currentTheme.accent.opacity(0.5))

            Text("No Simulation Data")
                .font(.title2)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.textColor)

            Text("Run a simulation in the War Room to see analytics")
                .font(.subheadline)
                .foregroundColor(themeManager.currentTheme.secondaryText)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 100)
    }

    private var pkChartSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("PROBABILITY OF KILL (Pk)")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            Chart {
                ForEach(simulationManager.results) { result in
                    LineMark(
                        x: .value("Year", result.year),
                        y: .value("Pk ASBM", result.pkASBM * 100)
                    )
                    .foregroundStyle(Color.blue)
                    .symbol(.circle)

                    LineMark(
                        x: .value("Year", result.year),
                        y: .value("Pk ASCM", result.pkASCM * 100)
                    )
                    .foregroundStyle(Color.green)
                    .symbol(.square)

                    LineMark(
                        x: .value("Year", result.year),
                        y: .value("Pk Hypersonic", result.pkHypersonic * 100)
                    )
                    .foregroundStyle(Color.orange)
                    .symbol(.triangle)
                }
            }
            .frame(height: 200)
            .chartYScale(domain: 0...100)
            .chartLegend(position: .bottom)
            .padding()
            .background(Color.black.opacity(0.3))
            .cornerRadius(12)
        }
    }

    private var carrierChartSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("CARRIER STATUS BY YEAR")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            Chart {
                ForEach(simulationManager.results) { result in
                    BarMark(
                        x: .value("Year", String(result.year)),
                        y: .value("Survived", result.carriersSurvived)
                    )
                    .foregroundStyle(Color.green)

                    BarMark(
                        x: .value("Year", String(result.year)),
                        y: .value("Lost", result.carriersLost)
                    )
                    .foregroundStyle(Color.red)
                }
            }
            .frame(height: 180)
            .chartLegend(position: .bottom)
            .padding()
            .background(Color.black.opacity(0.3))
            .cornerRadius(12)
        }
    }

    private var deterrenceChartSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("DETERRENCE SCORE")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            Chart {
                ForEach(simulationManager.results) { result in
                    AreaMark(
                        x: .value("Year", result.year),
                        y: .value("Deterrence", result.deterrenceScore)
                    )
                    .foregroundStyle(
                        LinearGradient(
                            colors: [themeManager.currentTheme.accent.opacity(0.5), themeManager.currentTheme.accent.opacity(0.1)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )

                    LineMark(
                        x: .value("Year", result.year),
                        y: .value("Deterrence", result.deterrenceScore)
                    )
                    .foregroundStyle(themeManager.currentTheme.accent)
                }
            }
            .frame(height: 150)
            .chartYScale(domain: 0...100)
            .padding()
            .background(Color.black.opacity(0.3))
            .cornerRadius(12)
        }
    }

    private var statisticsGrid: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("KEY STATISTICS")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                StatCard(
                    title: "Total Carriers Lost",
                    value: "\(simulationManager.results.map { $0.carriersLost }.reduce(0, +))",
                    icon: "ship.circle.fill",
                    color: .red
                )

                StatCard(
                    title: "Avg Pk ASBM",
                    value: String(format: "%.1f%%", simulationManager.results.map { $0.pkASBM * 100 }.reduce(0, +) / Double(max(1, simulationManager.results.count))),
                    icon: "target",
                    color: .blue
                )

                StatCard(
                    title: "Threats Stopped",
                    value: "\(simulationManager.results.map { $0.threatsStopped }.reduce(0, +))",
                    icon: "shield.checkered",
                    color: .green
                )

                StatCard(
                    title: "Final Deterrence",
                    value: "\(simulationManager.results.last?.deterrenceScore ?? 0)/100",
                    icon: "flag.fill",
                    color: themeManager.currentTheme.accent
                )
            }
        }
    }
}

struct StatCard: View {
    @EnvironmentObject var themeManager: ThemeManager
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 10) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)

            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(themeManager.currentTheme.textColor)

            Text(title)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.secondaryText)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.black.opacity(0.3))
        .cornerRadius(12)
    }
}

#Preview {
    AnalyticsView()
        .environmentObject(ThemeManager())
        .environmentObject(SimulationManager())
}
