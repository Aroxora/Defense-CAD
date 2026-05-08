//
//  SettingsView.swift
//  GoldenFleet
//
//  App settings and preferences
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Theme Section
                    themeSection

                    // Features Section
                    featuresSection

                    // About Section
                    aboutSection

                    // Version Info
                    versionInfo
                }
                .padding()
            }
            .background(themeManager.currentTheme.backgroundGradient.ignoresSafeArea())
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                        .foregroundColor(themeManager.currentTheme.accent)
                }
            }
        }
    }

    private var themeSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("THEME")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                ForEach(AppTheme.allCases) { theme in
                    ThemeCard(theme: theme, isSelected: themeManager.currentTheme == theme) {
                        withAnimation {
                            themeManager.currentTheme = theme
                            themeManager.triggerHaptic()
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.black.opacity(0.2))
        .cornerRadius(16)
    }

    private var featuresSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("FEATURES")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            VStack(spacing: 0) {
                SettingsToggle(
                    icon: "speaker.wave.2.fill",
                    title: "Sound Effects",
                    subtitle: "Play sounds on actions",
                    isOn: $themeManager.soundEnabled
                )

                Divider().background(Color.white.opacity(0.1))

                SettingsToggle(
                    icon: "hand.tap.fill",
                    title: "Haptic Feedback",
                    subtitle: "Vibration on interactions",
                    isOn: $themeManager.hapticEnabled
                )

                Divider().background(Color.white.opacity(0.1))

                SettingsToggle(
                    icon: "rectangle.compress.vertical",
                    title: "Compact Mode",
                    subtitle: "Reduce spacing and padding",
                    isOn: $themeManager.compactMode
                )
            }
        }
        .padding()
        .background(Color.black.opacity(0.2))
        .cornerRadius(16)
    }

    private var aboutSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("ABOUT")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            VStack(spacing: 12) {
                HStack {
                    Image(systemName: "shield.checkered")
                        .foregroundColor(themeManager.currentTheme.accent)
                        .frame(width: 30)
                    VStack(alignment: .leading) {
                        Text("Golden Fleet War Room")
                            .foregroundColor(themeManager.currentTheme.textColor)
                        Text("Defense Systems Analysis Framework")
                            .font(.caption)
                            .foregroundColor(themeManager.currentTheme.secondaryText)
                    }
                    Spacer()
                }

                HStack {
                    Image(systemName: "person.fill")
                        .foregroundColor(themeManager.currentTheme.accent)
                        .frame(width: 30)
                    VStack(alignment: .leading) {
                        Text("Bo Shang Consulting")
                            .foregroundColor(themeManager.currentTheme.textColor)
                        Text("Principal Consultant")
                            .font(.caption)
                            .foregroundColor(themeManager.currentTheme.secondaryText)
                    }
                    Spacer()
                }

                Link(destination: URL(string: "https://def-cad-for-pay.web.app")!) {
                    HStack {
                        Image(systemName: "globe")
                            .foregroundColor(themeManager.currentTheme.accent)
                            .frame(width: 30)
                        Text("Visit Web Simulator")
                            .foregroundColor(themeManager.currentTheme.textColor)
                        Spacer()
                        Image(systemName: "arrow.up.right.square")
                            .foregroundColor(themeManager.currentTheme.secondaryText)
                    }
                }

                Link(destination: URL(string: "https://github.com/ClandestineAI/PLA-Defense-CAD")!) {
                    HStack {
                        Image(systemName: "chevron.left.forwardslash.chevron.right")
                            .foregroundColor(themeManager.currentTheme.accent)
                            .frame(width: 30)
                        Text("View Source Code (MIT)")
                            .foregroundColor(themeManager.currentTheme.textColor)
                        Spacer()
                        Image(systemName: "arrow.up.right.square")
                            .foregroundColor(themeManager.currentTheme.secondaryText)
                    }
                }
            }
        }
        .padding()
        .background(Color.black.opacity(0.2))
        .cornerRadius(16)
    }

    private var versionInfo: some View {
        VStack(spacing: 8) {
            Text("Golden Fleet iOS v1.0.0")
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.secondaryText)

            Text("UNCLASSIFIED // CONCEPTUAL DESIGN")
                .font(.caption2)
                .foregroundColor(themeManager.currentTheme.primary)
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background(themeManager.currentTheme.accent)
                .cornerRadius(4)
        }
        .padding(.top, 20)
    }
}

struct ThemeCard: View {
    @EnvironmentObject var themeManager: ThemeManager
    let theme: AppTheme
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Circle()
                    .fill(theme.primary)
                    .frame(width: 50, height: 50)
                    .overlay(
                        Circle()
                            .stroke(theme.accent, lineWidth: 3)
                    )
                    .overlay(
                        Image(systemName: theme.icon)
                            .foregroundColor(theme.accent)
                    )

                Text(theme.name)
                    .font(.caption2)
                    .foregroundColor(themeManager.currentTheme.textColor)
                    .lineLimit(1)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(isSelected ? theme.accent.opacity(0.2) : Color.clear)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isSelected ? theme.accent : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct SettingsToggle: View {
    @EnvironmentObject var themeManager: ThemeManager
    let icon: String
    let title: String
    let subtitle: String
    @Binding var isOn: Bool

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(themeManager.currentTheme.accent)
                .frame(width: 30)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .foregroundColor(themeManager.currentTheme.textColor)
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.secondaryText)
            }

            Spacer()

            Toggle("", isOn: $isOn)
                .labelsHidden()
                .tint(themeManager.currentTheme.accent)
        }
        .padding(.vertical, 12)
    }
}

#Preview {
    SettingsView()
        .environmentObject(ThemeManager())
}
