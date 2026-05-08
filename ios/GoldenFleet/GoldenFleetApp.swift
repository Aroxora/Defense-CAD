//
//  GoldenFleetApp.swift
//  GoldenFleet
//
//  Golden Fleet War Room - Defense Systems Analysis
//  Bo Shang Consulting
//

import SwiftUI

@main
struct GoldenFleetApp: App {
    @StateObject private var themeManager = ThemeManager()
    @StateObject private var simulationManager = SimulationManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(themeManager)
                .environmentObject(simulationManager)
                .preferredColorScheme(themeManager.colorScheme)
        }
    }
}
