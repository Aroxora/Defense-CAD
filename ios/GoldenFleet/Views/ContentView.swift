//
//  ContentView.swift
//  GoldenFleet
//
//  Main navigation and tab view
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @EnvironmentObject var simulationManager: SimulationManager
    @State private var selectedTab = 0
    @State private var showSettings = false

    var body: some View {
        ZStack {
            // Background gradient
            themeManager.currentTheme.backgroundGradient
                .ignoresSafeArea()

            TabView(selection: $selectedTab) {
                // War Room Tab
                WarRoomView()
                    .tabItem {
                        Image(systemName: "shield.fill")
                        Text("War Room")
                    }
                    .tag(0)

                // Web Simulator Tab
                WebSimulatorView()
                    .tabItem {
                        Image(systemName: "globe")
                        Text("Simulator")
                    }
                    .tag(1)

                // Analytics Tab
                AnalyticsView()
                    .tabItem {
                        Image(systemName: "chart.bar.fill")
                        Text("Analytics")
                    }
                    .tag(2)

                // Contact Tab
                ContactView()
                    .tabItem {
                        Image(systemName: "envelope.fill")
                        Text("Contact")
                    }
                    .tag(3)
            }
            .accentColor(themeManager.currentTheme.accent)

            // Floating Settings Button
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    Button(action: { showSettings = true }) {
                        Image(systemName: "gear")
                            .font(.title2)
                            .foregroundColor(themeManager.currentTheme.primary)
                            .frame(width: 56, height: 56)
                            .background(themeManager.currentTheme.accent)
                            .clipShape(Circle())
                            .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
                    }
                    .padding(.trailing, 20)
                    .padding(.bottom, 90)
                }
            }
        }
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(ThemeManager())
        .environmentObject(SimulationManager())
}
