// swift-tools-version: 5.9
// Golden Fleet iOS App - Swift Package

import PackageDescription

let package = Package(
    name: "GoldenFleet",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "GoldenFleet",
            targets: ["GoldenFleet"]
        )
    ],
    dependencies: [],
    targets: [
        .target(
            name: "GoldenFleet",
            dependencies: [],
            path: "GoldenFleet"
        )
    ]
)
