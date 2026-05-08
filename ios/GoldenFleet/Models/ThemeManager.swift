//
//  ThemeManager.swift
//  GoldenFleet
//
//  Theme system with multiple visual styles
//

import SwiftUI
import UIKit

enum AppTheme: String, CaseIterable, Identifiable {
    case navyDark = "navy-dark"
    case tacticalGreen = "tactical-green"
    case commandGold = "command-gold"
    case arcticWhite = "arctic-white"
    case threatRed = "threat-red"

    var id: String { rawValue }

    var name: String {
        switch self {
        case .navyDark: return "Navy Dark"
        case .tacticalGreen: return "Tactical Green"
        case .commandGold: return "Command Gold"
        case .arcticWhite: return "Arctic White"
        case .threatRed: return "Threat Red"
        }
    }

    var icon: String {
        switch self {
        case .navyDark: return "water.waves"
        case .tacticalGreen: return "leaf.fill"
        case .commandGold: return "star.fill"
        case .arcticWhite: return "snowflake"
        case .threatRed: return "exclamationmark.triangle.fill"
        }
    }

    var primary: Color {
        switch self {
        case .navyDark: return Color(hex: "0a1628")
        case .tacticalGreen: return Color(hex: "0a1a10")
        case .commandGold: return Color(hex: "1a1508")
        case .arcticWhite: return Color(hex: "f0f4f8")
        case .threatRed: return Color(hex: "1a0808")
        }
    }

    var accent: Color {
        switch self {
        case .navyDark: return Color(hex: "c9a227")
        case .tacticalGreen: return Color(hex: "00ff00")
        case .commandGold: return Color(hex: "ffd700")
        case .arcticWhite: return Color(hex: "1a365d")
        case .threatRed: return Color(hex: "ff4444")
        }
    }

    var textColor: Color {
        switch self {
        case .arcticWhite: return Color(hex: "1a202c")
        default: return .white
        }
    }

    var secondaryText: Color {
        switch self {
        case .arcticWhite: return Color(hex: "4a5568")
        default: return Color(hex: "95a5a6")
        }
    }

    var backgroundGradient: LinearGradient {
        LinearGradient(
            colors: [primary, primary.opacity(0.8)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    }

    var isDark: Bool {
        self != .arcticWhite
    }
}

class ThemeManager: ObservableObject {
    @Published var currentTheme: AppTheme {
        didSet {
            UserDefaults.standard.set(currentTheme.rawValue, forKey: "selectedTheme")
        }
    }

    @Published var soundEnabled: Bool {
        didSet {
            UserDefaults.standard.set(soundEnabled, forKey: "soundEnabled")
        }
    }

    @Published var hapticEnabled: Bool {
        didSet {
            UserDefaults.standard.set(hapticEnabled, forKey: "hapticEnabled")
        }
    }

    @Published var compactMode: Bool {
        didSet {
            UserDefaults.standard.set(compactMode, forKey: "compactMode")
        }
    }

    var colorScheme: ColorScheme? {
        currentTheme.isDark ? .dark : .light
    }

    init() {
        let savedTheme = UserDefaults.standard.string(forKey: "selectedTheme") ?? "navy-dark"
        self.currentTheme = AppTheme(rawValue: savedTheme) ?? .navyDark
        self.soundEnabled = UserDefaults.standard.bool(forKey: "soundEnabled")
        self.hapticEnabled = UserDefaults.standard.object(forKey: "hapticEnabled") as? Bool ?? true
        self.compactMode = UserDefaults.standard.bool(forKey: "compactMode")
    }

    func cycleTheme() {
        let themes = AppTheme.allCases
        guard let currentIndex = themes.firstIndex(of: currentTheme) else { return }
        let nextIndex = (currentIndex + 1) % themes.count
        currentTheme = themes[nextIndex]
        triggerHaptic()
    }

    func triggerHaptic(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
        guard hapticEnabled else { return }
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }
}

// Color extension for hex support
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
