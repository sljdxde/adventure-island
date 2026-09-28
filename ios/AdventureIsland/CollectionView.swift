import SwiftUI

// MARK: - 收集册（图鉴/贴纸/汉字卡/徽章）

struct CollectionView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Binding var route: Route
    @State private var file: CollectionFile?
    @State private var activeTab = "science"

    private var theme: AppTheme { .coll }

    var body: some View {
        ZStack {
            SceneBackground(theme: theme)

            VStack(spacing: 0) {
                header
                    .padding(.horizontal, 22)
                    .padding(.top, 8)

                tabs
                    .padding(.horizontal, 30)
                    .padding(.top, 6)

                board
                    .padding(.horizontal, 20)
                    .padding(.top, 8)
                    .padding(.bottom, 12)
            }
        }
        .onAppear {
            if file == nil { file = ContentLoader.load(CollectionFile.self, "collection") }
        }
    }

    // MARK: 顶部

    private var header: some View {
        HStack {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            HStack(spacing: 0) {
                ZStack {
                    Circle().fill(LinearGradient(colors: [Color(hex: 0xFFE29A), .brandYellow], startPoint: .topLeading, endPoint: .bottomTrailing))
                    IconView(name: "girl", size: 34)
                }
                .frame(width: 54, height: 54)
                .overlay(Circle().stroke(.white, lineWidth: 4))
                Text("收集册")
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
            GoldChip(icon: "fire", text: "连续 \(max(store.snapshot.streak, 1)) 天")
        }
    }

    // MARK: 页签

    private var tabs: some View {
        HStack(spacing: 18) {
            ForEach(file?.groups ?? []) { group in
                tab(group)
            }
            Spacer()
        }
    }

    private func tab(_ group: CollectionGroup) -> some View {
        let active = activeTab == group.id
        return Button {
            activeTab = group.id
            soundTap()
        } label: {
            VStack(spacing: 3) {
                IconView(name: group.icon, size: 28)
                    .frame(width: 58, height: 58)
                    .background(
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(active
                                  ? AnyShapeStyle(LinearGradient(colors: [Color(hex: 0xFFDD7A), .brandYellowDk], startPoint: .top, endPoint: .bottom))
                                  : AnyShapeStyle(.white.opacity(0.88)))
                    )
                    .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(active ? .brandYellowDdk : .white, lineWidth: 2.5))
                    .shadow(color: active ? .brandYellowDdk : .ink.opacity(0.1), radius: 0, x: 0, y: active ? 4 : 3)
                    .scaleEffect(active ? 1.06 : 1)
                Text(group.title)
                    .font(.kidBody(14))
                    .foregroundColor(active ? .brandYellowDdk : Color(hex: 0x8A6520))
            }
        }
        .buttonStyle(.plain)
    }

    // MARK: 面板

    private var board: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 40, style: .continuous)
                .fill(LinearGradient(colors: [Color(hex: 0xFFFBF0), .creamDk], startPoint: .top, endPoint: .bottom))
                .overlay(RoundedRectangle(cornerRadius: 40, style: .continuous).stroke(.white, lineWidth: 5))
                .shadow(color: .ink.opacity(0.14), radius: 16, y: 8)

            if let group = file?.groups.first(where: { $0.id == activeTab }) {
                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 14) {
                        groupHeader(group)
                        let columns = [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12),
                                       GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12),
                                       GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)]
                        LazyVGrid(columns: columns, spacing: 12) {
                            ForEach(group.items) { item in
                                slot(group, item)
                            }
                        }
                        footerHint(group)
                    }
                    .padding(24)
                }
            }
        }
        .frame(maxHeight: .infinity)
    }

    private func groupHeader(_ group: CollectionGroup) -> some View {
        HStack {
            Text("\(groupTitle(group))")
                .font(.kidHead(20))
                .foregroundColor(.inkSoft)
            Spacer()
            GoldTrack(ratio: ratio(group), height: 12)
                .frame(width: 260)
        }
    }

    private func groupTitle(_ group: CollectionGroup) -> String {
        switch group.id {
        case "science":
            let got = group.items.filter { isCollected(group, $0) }.count
            return "已完成 \(got) / \(group.items.count) 个现象"
        case "sticker":
            let got = group.items.filter { store.snapshot.stickers.contains($0.id) }.count
            return "已获得 \(got) / \(group.items.count) 张"
        case "hanzi":
            let got = group.items.filter { store.snapshot.learnedHanzi.contains($0.text ?? "") }.count
            return "已认读 \(got) / \(group.items.count) 字"
        default:
            return "每一枚徽章都是了不起的坚持"
        }
    }

    private func ratio(_ group: CollectionGroup) -> Double {
        let total = max(group.items.count, 1)
        let got: Int
        switch group.id {
        case "science": got = group.items.filter { isCollected(group, $0) }.count
        case "sticker": got = group.items.filter { store.snapshot.stickers.contains($0.id) }.count
        case "hanzi": got = group.items.filter { store.snapshot.learnedHanzi.contains($0.text ?? "") }.count
        default: got = 0
        }
        return Double(got) / Double(total)
    }

    /// 科学图鉴：前 6 项由实验收集，其余默认已解锁展示知识
    private func isCollected(_ group: CollectionGroup, _ item: CollectionItem) -> Bool {
        guard group.id == "science" else { return true }
        let experimentIds = ["sci-apple", "sci-rock", "sci-wood", "sci-key", "sci-sponge", "sci-balloon"]
        if experimentIds.contains(item.id) {
            return store.snapshot.collectedScience.contains(item.id)
        }
        return true
    }

    @ViewBuilder
    private func slot(_ group: CollectionGroup, _ item: CollectionItem) -> some View {
        let collected = isCollected(group, item)
        Button {
            guard collected else { return }
            if let fact = item.fact {
                speech.speak(fact)
                toast.show(fact, seconds: 3.2)
            } else if let text = item.text, let pinyin = item.pinyin {
                speech.speak("\(text)，\(pinyin)")
                toast.show("\(text) · \(pinyin)")
            }
        } label: {
            VStack(spacing: 4) {
                ZStack(alignment: .topTrailing) {
                    if collected {
                        if let icon = item.icon {
                            IconView(name: icon, size: 46)
                        } else if let text = item.text {
                            Text(text)
                                .font(.hanzi(44))
                                .foregroundColor(Color(hex: 0xE2582A))
                        } else {
                            IconView(name: group.icon, size: 42)
                        }
                    } else {
                        Text("？")
                            .font(.hanzi(40))
                            .foregroundColor(Color(hex: 0xC9BBA0))
                    }
                    if collected, let tag = item.tag {
                        Text(tag)
                            .font(.system(size: 12, weight: .heavy))
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 2.5)
                            .background(Capsule().fill(tagColor(item.tagColor)))
                            .offset(x: 12, y: -6)
                    }
                }
                .frame(height: 58)
                Text(collected ? item.name : group.lockedLabel)
                    .font(.kidBody(14))
                    .foregroundColor(collected ? .ink : Color(hex: 0xC9BBA0))
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 104)
            .background(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(collected
                          ? AnyShapeStyle(LinearGradient(colors: [.white, Color(hex: 0xFFF6E0)], startPoint: .top, endPoint: .bottom))
                          : AnyShapeStyle(Color(hex: 0xF3EADA)))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(collected ? Color(hex: 0xF5DFAC) : Color(hex: 0xE0D2B6), lineWidth: collected ? 3 : 2.5)
            )
            .shadow(color: collected ? Color(hex: 0xEFDBA8) : .clear, radius: 0, x: 0, y: 4)
        }
        .buttonStyle(.plain)
        .opacity(collected ? 1 : 0.75)
    }

    private func tagColor(_ name: String?) -> Color {
        switch name {
        case "blue": return .brandBlue
        case "coral": return .brandCoralDk
        case "gold": return .brandYellowDk
        default: return .brandPurple
        }
    }

    private func footerHint(_ group: CollectionGroup) -> some View {
        let hint: String
        switch group.id {
        case "science": hint = "💡 去科学岛做实验，就能点亮更多现象图鉴"
        case "sticker": hint = "💡 完成每日任务、闯关成功都能掉落贴纸"
        case "hanzi": hint = "💡 在识字村闯关，就能点亮更多汉字卡"
        default: hint = "💡 徽章记录每一次了不起的坚持"
        }
        return Text(hint)
            .font(.kidBody(15))
            .foregroundColor(.inkSoft)
            .frame(maxWidth: .infinity)
    }

    private func soundTap() {
        // 轻点音效
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }
}
