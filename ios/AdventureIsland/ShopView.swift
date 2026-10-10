import SwiftUI

// MARK: - 金币商店（v0.9 工单08/09）：小伙伴 + 骰子皮肤两区；商店/衣橱双段
// 对齐 HTML renderShop / renderWardrobe：卡片三态（使用中 / 换上 / 购买-价格）。
// 购买经 store.buyItem（账本扣款 .shop，余额不足拒绝、不透支）；激活经 store.activate。

struct ShopView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @Binding var route: Route

    @State private var file: ShopFile?
    @State private var seg = 0   // 0 商店 · 1 衣橱

    private var theme: AppTheme { .home }

    var body: some View {
        ZStack {
            SceneBackground(theme: theme)
            VStack(spacing: 12) {
                header
                    .padding(.horizontal, 22)
                    .padding(.top, 8)

                Picker("", selection: $seg) {
                    Text("🛒 商店").tag(0)
                    Text("🧥 衣橱").tag(1)
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, 40)

                if let file {
                    ScrollView(showsIndicators: false) {
                        VStack(spacing: 22) {
                            section(title: "小伙伴", items: file.characters, kind: "chars")
                            section(title: "骰子皮肤", items: file.dice, kind: "dice")
                        }
                        .padding(.horizontal, 26)
                        .padding(.bottom, 30)
                    }
                }
            }
        }
        .onAppear {
            if file == nil { file = ContentLoader.load(ShopFile.self, "shop") }
        }
    }

    private var header: some View {
        HStack {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            HStack(spacing: 0) {
                ZStack {
                    Circle().fill(LinearGradient(colors: [Color(hex: 0xFFE29A), .brandYellow], startPoint: .topLeading, endPoint: .bottomTrailing))
                    IconView(name: "shop", size: 34)
                }
                .frame(width: 54, height: 54)
                .overlay(Circle().stroke(.white, lineWidth: 4))
                Text(seg == 0 ? "金币商店" : "我的衣橱")
                    .font(.kidHead(20))
                    .foregroundColor(.white)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 12)
                    .background(Capsule().fill(LinearGradient(colors: [.brandOrange, .brandOrangeDk], startPoint: .top, endPoint: .bottom)))
                    .padding(.leading, -16)
            }
            .shadow(color: .ink.opacity(0.2), radius: 8, y: 5)
            Spacer()
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    private func section(title: String, items: [ShopItem], kind: String) -> some View {
        let ownedCount = (kind == "chars" ? store.snapshot.ownedChars : store.snapshot.ownedDice).count
        return VStack(alignment: .leading, spacing: 10) {
            Text("\(title) · 已拥有 \(ownedCount)/\(items.count)")
                .font(.kidHead(19))
                .foregroundColor(Color(hex: 0x8A5B00))
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 150, maximum: 200), spacing: 16)], spacing: 16) {
                ForEach(items) { item in
                    card(item, kind: kind)
                }
            }
        }
    }

    private func owned(_ kind: String, _ id: String) -> Bool {
        (kind == "chars" ? store.snapshot.ownedChars : store.snapshot.ownedDice).contains(id)
    }
    private func active(_ kind: String, _ id: String) -> Bool {
        (kind == "chars" ? store.snapshot.activeChar : store.snapshot.activeDice) == id
    }

    private func card(_ item: ShopItem, kind: String) -> some View {
        let isOwned = owned(kind, item.id)
        let isActive = active(kind, item.id)
        let poor = store.snapshot.coins < item.price
        return VStack(spacing: 8) {
            if kind == "chars" {
                IconView(name: item.icon, size: 78)
            } else {
                DieFaceView(face: 5, size: 78, pip: item.icon)
            }
            Text(seg == 1 && !isOwned ? "未获得" : item.name)
                .font(.kidHead(16))
                .foregroundColor(.ink)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            button(item: item, kind: kind, isOwned: isOwned, isActive: isActive, poor: poor)
        }
        .padding(.vertical, 16)
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(LinearGradient(colors: [.white, Color(hex: 0xFFF6E0)], startPoint: .top, endPoint: .bottom))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(isActive ? .brandYellowDk : Color(hex: 0xF0E0BC), lineWidth: isActive ? 4 : 2)
        )
        .shadow(color: .ink.opacity(0.10), radius: 10, y: 6)
        .opacity(seg == 1 && !isOwned ? 0.8 : 1)
    }

    @ViewBuilder
    private func button(item: ShopItem, kind: String, isOwned: Bool, isActive: Bool, poor: Bool) -> some View {
        if isActive {
            Text("✓ 使用中")
                .font(.kidHead(15))
                .foregroundColor(.brandGreenDk)
                .padding(.horizontal, 18).padding(.vertical, 8)
                .background(Capsule().fill(Color(hex: 0xE7F7EA)))
        } else if isOwned {
            Button {
                store.activate(kind: kind, id: item.id)
                sound.systemTap()
                toast.show("换上啦，马上生效！")
            } label: {
                Text("换上")
                    .font(.kidHead(15))
                    .foregroundColor(.white)
                    .padding(.horizontal, 18).padding(.vertical, 8)
                    .background(Capsule().fill(LinearGradient(colors: [.brandBlue, .brandBlueDk], startPoint: .top, endPoint: .bottom)))
            }
            .buttonStyle(.plain)
        } else if seg == 0 {
            // 商店：购买按钮显示价格；余额不足置灰（不透支）
            Button {
                if store.buyItem(kind: kind, id: item.id, price: item.price) {
                    sound.coin()
                    toast.show("买到「\(item.name)」啦！")
                } else {
                    sound.wrong()
                    toast.show("金币不够，还差 \(max(0, item.price - store.snapshot.coins)) 枚")
                }
            } label: {
                HStack(spacing: 5) {
                    IconView(name: "coin", size: 16)
                    Text("\(item.price)")
                        .font(.kidHead(15))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16).padding(.vertical, 8)
                .background(Capsule().fill(poor
                    ? LinearGradient(colors: [Color(hex: 0xC9C2B4), Color(hex: 0xA89F8C)], startPoint: .top, endPoint: .bottom)
                    : LinearGradient(colors: [.brandYellow, .brandYellowDk], startPoint: .top, endPoint: .bottom)))
            }
            .buttonStyle(.plain)
        } else {
            // 衣橱里未拥有：去商店
            Button {
                seg = 0
            } label: {
                Text("🔒 去商店")
                    .font(.kidHead(15))
                    .foregroundColor(.inkSoft)
                    .padding(.horizontal, 16).padding(.vertical, 8)
                    .background(Capsule().fill(Color(hex: 0xF0E8D6)))
            }
            .buttonStyle(.plain)
        }
    }
}
