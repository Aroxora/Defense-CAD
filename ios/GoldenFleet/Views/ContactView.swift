//
//  ContactView.swift
//  GoldenFleet
//
//  Contact form for Bo Shang Consulting
//

import SwiftUI

struct ContactView: View {
    @EnvironmentObject var themeManager: ThemeManager
    @State private var name = ""
    @State private var email = ""
    @State private var organization = ""
    @State private var phone = ""
    @State private var interest = "general"
    @State private var message = ""
    @State private var isSubmitting = false
    @State private var showSuccess = false

    let interests = [
        ("general", "General Inquiry"),
        ("contract", "DoD Contract Proposal"),
        ("consulting", "Consulting Services"),
        ("integration", "System Integration"),
        ("demo", "Live Demo Request")
    ]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    headerSection

                    // Contact Form
                    formSection

                    // Submit Button
                    submitButton

                    // Contact Info
                    contactInfoSection
                }
                .padding()
            }
            .background(themeManager.currentTheme.backgroundGradient.ignoresSafeArea())
            .navigationTitle("Contact")
            .navigationBarTitleDisplayMode(.inline)
            .alert("Message Sent", isPresented: $showSuccess) {
                Button("OK") { resetForm() }
            } message: {
                Text("Thank you for your inquiry. Bo Shang Consulting will respond within 24 hours.")
            }
        }
    }

    private var headerSection: some View {
        VStack(spacing: 12) {
            Image(systemName: "envelope.badge.shield.half.filled")
                .font(.system(size: 50))
                .foregroundColor(themeManager.currentTheme.accent)

            Text("Contact Bo Shang Consulting")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(themeManager.currentTheme.textColor)

            Text("For DoD contract proposals, consulting inquiries, or technical demonstrations")
                .font(.subheadline)
                .foregroundColor(themeManager.currentTheme.secondaryText)
                .multilineTextAlignment(.center)
        }
        .padding(.vertical)
    }

    private var formSection: some View {
        VStack(spacing: 16) {
            FormField(label: "Full Name", text: $name, placeholder: "Your name", icon: "person.fill")

            FormField(label: "Email", text: $email, placeholder: "your.email@gov.mil", icon: "envelope.fill", keyboardType: .emailAddress)

            FormField(label: "Organization", text: $organization, placeholder: "Department / Agency / Company", icon: "building.2.fill")

            FormField(label: "Phone", text: $phone, placeholder: "+1 (555) 000-0000", icon: "phone.fill", keyboardType: .phonePad)

            // Interest Picker
            VStack(alignment: .leading, spacing: 8) {
                Label("Interest Area", systemImage: "star.fill")
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.accent)

                Picker("Interest", selection: $interest) {
                    ForEach(interests, id: \.0) { id, label in
                        Text(label).tag(id)
                    }
                }
                .pickerStyle(.segmented)
            }

            // Message
            VStack(alignment: .leading, spacing: 8) {
                Label("Message", systemImage: "text.alignleft")
                    .font(.caption)
                    .foregroundColor(themeManager.currentTheme.accent)

                TextEditor(text: $message)
                    .frame(height: 120)
                    .padding(8)
                    .background(Color.black.opacity(0.3))
                    .cornerRadius(10)
                    .foregroundColor(themeManager.currentTheme.textColor)
            }
        }
        .padding()
        .background(Color.black.opacity(0.2))
        .cornerRadius(16)
    }

    private var submitButton: some View {
        Button(action: submitForm) {
            HStack {
                if isSubmitting {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: themeManager.currentTheme.primary))
                } else {
                    Image(systemName: "paperplane.fill")
                }
                Text(isSubmitting ? "Sending..." : "Send Message")
                    .fontWeight(.bold)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(isFormValid ? themeManager.currentTheme.accent : Color.gray)
            .foregroundColor(themeManager.currentTheme.primary)
            .cornerRadius(12)
        }
        .disabled(!isFormValid || isSubmitting)
    }

    private var contactInfoSection: some View {
        VStack(spacing: 16) {
            Text("DIRECT CONTACT")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(themeManager.currentTheme.accent)
                .tracking(2)

            VStack(spacing: 12) {
                ContactInfoRow(icon: "globe", label: "Website", value: "def-cad-for-pay.web.app")
                ContactInfoRow(icon: "at", label: "Twitter", value: "@PeteHegseth, @SecScottBessent")
                ContactInfoRow(icon: "building.columns.fill", label: "Targeting", value: "DoD, Treasury, NSC")
            }
            .padding()
            .background(Color.black.opacity(0.2))
            .cornerRadius(12)

            // Classification Banner
            Text("UNCLASSIFIED // CONCEPTUAL DESIGN // Bo Shang Consulting")
                .font(.caption2)
                .foregroundColor(themeManager.currentTheme.primary)
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(themeManager.currentTheme.accent)
                .cornerRadius(4)
        }
    }

    private var isFormValid: Bool {
        !name.isEmpty && !email.isEmpty && email.contains("@") && !organization.isEmpty
    }

    private func submitForm() {
        isSubmitting = true
        themeManager.triggerHaptic()

        // Simulate API call
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            isSubmitting = false
            showSuccess = true
            themeManager.triggerHaptic(.heavy)
        }
    }

    private func resetForm() {
        name = ""
        email = ""
        organization = ""
        phone = ""
        interest = "general"
        message = ""
    }
}

struct FormField: View {
    @EnvironmentObject var themeManager: ThemeManager
    let label: String
    @Binding var text: String
    let placeholder: String
    let icon: String
    var keyboardType: UIKeyboardType = .default

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(label, systemImage: icon)
                .font(.caption)
                .foregroundColor(themeManager.currentTheme.accent)

            TextField(placeholder, text: $text)
                .keyboardType(keyboardType)
                .textFieldStyle(.plain)
                .padding(12)
                .background(Color.black.opacity(0.3))
                .cornerRadius(10)
                .foregroundColor(themeManager.currentTheme.textColor)
        }
    }
}

struct ContactInfoRow: View {
    @EnvironmentObject var themeManager: ThemeManager
    let icon: String
    let label: String
    let value: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(themeManager.currentTheme.accent)
                .frame(width: 30)

            Text(label)
                .foregroundColor(themeManager.currentTheme.secondaryText)

            Spacer()

            Text(value)
                .foregroundColor(themeManager.currentTheme.textColor)
                .font(.caption)
        }
    }
}

#Preview {
    ContactView()
        .environmentObject(ThemeManager())
}
