//
//  WebSimulatorView.swift
//  GoldenFleet
//
//  WKWebView wrapper for full web simulator
//

import SwiftUI
import WebKit

struct WebSimulatorView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @State private var isLoading = true
    @State private var loadingProgress: Double = 0

    var body: some View {
        NavigationStack {
            ZStack {
                WebView(
                    url: URL(string: "https://def-cad-for-pay.web.app")!,
                    isLoading: $isLoading,
                    progress: $loadingProgress
                )

                if isLoading {
                    VStack(spacing: 20) {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: themeManager.currentTheme.accent))
                            .scaleEffect(1.5)

                        Text("Loading War Room...")
                            .font(.headline)
                            .foregroundColor(themeManager.currentTheme.accent)

                        ProgressView(value: loadingProgress)
                            .progressViewStyle(LinearProgressViewStyle(tint: themeManager.currentTheme.accent))
                            .frame(width: 200)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(themeManager.currentTheme.primary.opacity(0.95))
                }
            }
            .navigationTitle("Web Simulator")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Link(destination: URL(string: "https://def-cad-for-pay.web.app")!) {
                        Image(systemName: "safari")
                            .foregroundColor(themeManager.currentTheme.accent)
                    }
                }
            }
        }
    }
}

struct WebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var progress: Double

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.allowsInlineMediaPlayback = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true

        // Add progress observation
        webView.addObserver(context.coordinator, forKeyPath: "estimatedProgress", options: .new, context: nil)

        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        var parent: WebView

        init(_ parent: WebView) {
            self.parent = parent
        }

        override func observeValue(forKeyPath keyPath: String?, of object: Any?, change: [NSKeyValueChangeKey : Any]?, context: UnsafeMutableRawPointer?) {
            if keyPath == "estimatedProgress", let webView = object as? WKWebView {
                DispatchQueue.main.async {
                    self.parent.progress = webView.estimatedProgress
                }
            }
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            DispatchQueue.main.async {
                self.parent.isLoading = true
            }
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            DispatchQueue.main.async {
                self.parent.isLoading = false
            }
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            DispatchQueue.main.async {
                self.parent.isLoading = false
            }
        }
    }
}

#Preview {
    WebSimulatorView()
        .environmentObject(ThemeManager())
}
