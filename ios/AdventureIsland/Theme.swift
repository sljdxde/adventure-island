import SwiftUI

// MARK: - 设计令牌（对齐 design/style.css v3）

extension Color {
    init(hex: UInt32) {
        self.init(
            red: Double((hex >> 16) & 0xFF) / 255,
            green: Double((hex >> 8) & 0xFF) / 255,
            blue: Double(hex & 0xFF) / 255
        )
    }

    static let brandOrange = Color(hex: 0xFF9F43)
    static let brandOrangeDk = Color(hex: 0xF08C1F)
    static let brandOrangeDdk = Color(hex: 0xD97706)
    static let brandYellow = Color(hex: 0xFFC53D)
    static let brandYellowDk = Color(hex: 0xF5A623)
    static let brandYellowDdk = Color(hex: 0xD98A0F)
    static let brandCoral = Color(hex: 0xFF7B6B)
    static let brandCoralDk = Color(hex: 0xE85D4E)
    static let brandCoralDdk = Color(hex: 0xC24836)
    static let brandBlue = Color(hex: 0x4FA9E8)
    static let brandBlueDk = Color(hex: 0x2F86C9)
    static let brandBlueDdk = Color(hex: 0x20629E)
    static let brandPurple = Color(hex: 0x9B7BF5)
    static let brandPurpleDk = Color(hex: 0x7C5CE0)
    static let brandPurpleDdk = Color(hex: 0x5E3FBE)
    static let brandGreen = Color(hex: 0x58C96B)
    static let brandGreenDk = Color(hex: 0x3BA851)
    static let brandGreenDdk = Color(hex: 0x2E8A40)
    static let brandPink = Color(hex: 0xFF8FB5)
    static let brandPinkDk = Color(hex: 0xF76EA0)
    static let cream = Color(hex: 0xFFF9EE)
    static let creamDk = Color(hex: 0xFFF1D8)
    static let ink = Color(hex: 0x57433A)
    static let inkSoft = Color(hex: 0xA08A76)
    static let line = Color(hex: 0xF3E5C8)
    static let gold = Color(hex: 0xFFD34D)
    static let goldDk = Color(hex: 0xE5A916)
    static let goldDdk = Color(hex: 0xC08A0C)
    static let waterBlue = Color(hex: 0x7FD4F8)
}

/// 页面主题：天空配色 + 面板描边色（对应 CSS data-theme）
enum AppTheme {
    case home, cn, math, lab, coll, parent

    var sky: [Color] {
        switch self {
        case .home: return [Color(hex: 0x4FB4F5), Color(hex: 0x8FD6FA), Color(hex: 0xD8F3FF)]
        case .cn: return [Color(hex: 0xFFDE9E), Color(hex: 0xFFCF87), Color(hex: 0xFFE9BE)]
        case .math: return [Color(hex: 0x58C4F7), Color(hex: 0x9FE0FB), Color(hex: 0xDCF6FE)]
        case .lab: return [Color(hex: 0x8F74EC), Color(hex: 0xB39CF7), Color(hex: 0xE2DAFE)]
        case .coll: return [Color(hex: 0xFFC964), Color(hex: 0xFFDE94), Color(hex: 0xFFF2C4)]
        case .parent: return [Color(hex: 0xA9C0DC), Color(hex: 0xC6D6E9), Color(hex: 0xE6EEF5)]
        }
    }

    var panelStroke: Color {
        switch self {
        case .home: return Color(hex: 0xF5B942)
        case .cn: return .brandOrangeDk
        case .math: return .brandBlueDk
        case .lab: return .brandPurple
        case .coll: return .goldDk
        case .parent: return Color(hex: 0x9AA7B4)
        }
    }

    var titleStroke: Color {
        switch self {
        case .home: return .brandBlueDk
        case .cn: return Color(hex: 0xC96A06)
        case .math: return .brandBlueDk
        case .lab: return .brandPurpleDk
        case .coll: return .goldDdk
        case .parent: return Color(hex: 0x5C7089)
        }
    }

    var hillOpacity: Double { self == .parent ? 0.35 : 0.95 }
}

// MARK: - 字体

extension Font {
    static func kidTitle(_ size: CGFloat = 27) -> Font {
        .system(size: size, weight: .heavy, design: .rounded)
    }
    static func kidHead(_ size: CGFloat = 20) -> Font {
        .system(size: size, weight: .bold, design: .rounded)
    }
    static func kidBody(_ size: CGFloat = 17) -> Font {
        .system(size: size, weight: .semibold, design: .rounded)
    }
    static func hanzi(_ size: CGFloat) -> Font {
        .system(size: size, weight: .heavy)
    }
}
