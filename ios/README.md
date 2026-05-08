# Golden Fleet iOS App

Native iOS companion app for the Golden Fleet War Room Defense Simulator.

## Features

- **War Room Simulator**: Native SwiftUI interface for 10-year defense outcome projection
- **Web Simulator**: Embedded WKWebView for full web experience
- **Analytics Dashboard**: Swift Charts visualization of simulation results
- **Contact Form**: Direct inquiry submission to Bo Shang Consulting
- **Multiple Themes**: Navy Dark, Tactical Green, Command Gold, Arctic White, Threat Red
- **Sound & Haptics**: Immersive feedback system
- **Offline Capable**: Core simulation runs locally

## Requirements

- iOS 17.0+
- Xcode 15.0+
- Swift 5.9+

## Installation

### Option 1: Open in Xcode

1. Open `GoldenFleet.xcodeproj` in Xcode
2. Select your development team in Signing & Capabilities
3. Build and run on simulator or device

### Option 2: Generate Xcode Project (if needed)

```bash
cd ios
swift package generate-xcodeproj
open GoldenFleet.xcodeproj
```

### Option 3: Build from Command Line

```bash
cd ios
xcodebuild -scheme GoldenFleet -destination 'platform=iOS Simulator,name=iPhone 15 Pro' build
```

## Project Structure

```
ios/
├── Package.swift                 # Swift Package Manager config
├── GoldenFleet/
│   ├── GoldenFleetApp.swift     # App entry point
│   ├── Info.plist               # App configuration
│   ├── Assets.xcassets/         # Images and colors
│   ├── Models/
│   │   ├── ThemeManager.swift   # Theme system
│   │   └── SimulationManager.swift  # Simulation engine
│   ├── Views/
│   │   ├── ContentView.swift    # Main tab navigation
│   │   ├── WarRoomView.swift    # Native simulation UI
│   │   ├── WebSimulatorView.swift   # WKWebView wrapper
│   │   ├── AnalyticsView.swift  # Charts dashboard
│   │   ├── ContactView.swift    # Contact form
│   │   └── SettingsView.swift   # App settings
│   └── Services/
│       └── (API services)
└── GoldenFleet.xcodeproj/       # Xcode project (generated)
```

## Themes

| Theme | Description | Use Case |
|-------|-------------|----------|
| Navy Dark | Default naval operations | Standard use |
| Tactical Green | Night vision compatible | Field operations |
| Command Gold | Executive briefing mode | Presentations |
| Arctic White | High visibility light mode | Daytime/bright environments |
| Threat Red | Combat alert status | Simulated alerts |

## Keyboard Shortcuts (iPad)

| Shortcut | Action |
|----------|--------|
| ⌘ + T | Cycle themes |
| ⌘ + R | Run simulation |
| ⌘ + , | Open settings |

## Web Integration

The app includes an embedded web view that loads the full Golden Fleet web simulator:
- URL: https://def-cad-for-pay.web.app
- Full D3.js visualizations
- Monte Carlo cloud function integration
- Real-time terminal output

## License

MIT License - See [LICENSE](../LICENSE) for details.

## Contact

**Bo Shang Consulting**
- Web: https://def-cad-for-pay.web.app
- Twitter: @PeteHegseth, @SecScottBessent

---

*UNCLASSIFIED // CONCEPTUAL DESIGN // Bo Shang Consulting*
