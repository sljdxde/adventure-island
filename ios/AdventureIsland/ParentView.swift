import SwiftUI

// MARK: - 家长中心（算术家长门 + 时长管理 + 进度 + 难度）

struct ParentView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var settings: SettingsStore
    @EnvironmentObject var timeManager: TimeManager
    @EnvironmentObject var toast: ToastCenter
    @Binding var route: Route

    @State private var unlocked = false
    @State private var gate = ParentGate.makeQuestion()
    @State private var gateInput = ""

    var body: some View {
        ZStack {
            SceneBackground(theme: .parent)

            VStack(spacing: 0) {
                header
                    .padding(.horizontal, 22)
                    .padding(.top, 8)

                ScrollView(showsIndicators: false) {
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                        timePanel
                        shieldPanel
                        progressPanel
                        controlPanel
                        promisesPanel
                            .gridCellColumns(2)
                    }
                    .padding(.horizontal, 22)
                    .padding(.top, 10)
                    .padding(.bottom, 20)
                }
            }

            if !unlocked {
                gateOverlay
            }
        }
    }

    // MARK: 顶部

    private var header: some View {
        HStack {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            VStack(alignment: .leading, spacing: 1) {
                Text("🔒 家长中心")
                    .font(.kidHead(22))
                    .foregroundColor(Color(hex: 0x5C7089))
                Text("孩子数据仅保存在本机 · 不上传云端")
                    .font(.kidBody(13.5))
                    .foregroundColor(.inkSoft)
            }
            Spacer()
            GoldChip(icon: settings.settings.avatar, text: settings.settings.childName)
        }
    }

    // MARK: 家长门

    private var gateOverlay: some View {
        ZStack {
            Color.black.opacity(0.5).ignoresSafeArea()
            VStack(spacing: 14) {
                Text("🔐").font(.system(size: 56))
                Text("家长中心")
                    .font(.kidTitle(28))
                    .foregroundColor(.ink)
                Text("这里是大人的设置区，请完成验证：\n（孩子答不出来的小算术 😊）")
                    .font(.kidBody(16))
                    .foregroundColor(.inkSoft)
                    .multilineTextAlignment(.center)
                Text(gate.text)
                    .font(.kidTitle(36))
                    .foregroundColor(.ink)
                    .padding(.horizontal, 40)
                    .padding(.vertical, 14)
                    .background(
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(.white)
                            .shadow(color: Color(hex: 0xF0DCAC), radius: 0, x: 0, y: 4)
                    )
                HStack(spacing: 12) {
                    TextField("答案", text: $gateInput)
                        .textFieldStyle(.plain)
                        .multilineTextAlignment(.center)
                        .font(.kidTitle(26))
                        .keyboardType(.numberPad)
                        .frame(width: 130, height: 58)
                        .background(
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .fill(.white)
                                .shadow(color: Color(hex: 0xE8DFC8), radius: 0, x: 0, y: 4)
                        )
                    Button {
                        if ParentGate.check(gateInput, answer: gate.answer) {
                            withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) { unlocked = true }
                            toast.show("✅ 家长验证通过")
                        } else {
                            toast.show("答案不对哦，再试试")
                            gate = ParentGate.makeQuestion()
                            gateInput = ""
                        }
                    } label: {
                        Text("进入").font(.kidHead(21))
                    }
                    .buttonStyle(.jellyGreen)
                }
                Text("提示：答案会随题目刷新")
                    .font(.kidBody(12.5))
                    .foregroundColor(.inkSoft.opacity(0.8))
            }
            .padding(44)
            .background(
                RoundedRectangle(cornerRadius: 30, style: .continuous)
                    .fill(LinearGradient(colors: [Color(hex: 0xFFFDF4), Color(hex: 0xFFF3D8)], startPoint: .top, endPoint: .bottom))
            )
            .overlay(RoundedRectangle(cornerRadius: 30, style: .continuous).stroke(.white, lineWidth: 5))
            .shadow(color: .black.opacity(0.3), radius: 26)
        }
    }

    // MARK: 面板们

    private func panel<Content: View>(_ icon: String, _ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 9) {
                IconView(name: icon, size: 22)
                    .frame(width: 36, height: 36)
                    .background(RoundedRectangle(cornerRadius: 12).fill(Color(hex: 0xFFF3D8)))
                Text(title).font(.kidHead(19)).foregroundColor(.ink)
            }
            content()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .fill(LinearGradient(colors: [.white, Color(hex: 0xFBF7EE)], startPoint: .top, endPoint: .bottom))
        )
        .overlay(RoundedRectangle(cornerRadius: 26, style: .continuous).stroke(.white, lineWidth: 4))
        .shadow(color: .ink.opacity(0.08), radius: 12, y: 6)
    }

    private var timePanel: some View {
        panel("clock", "今日使用时长") {
            HStack(spacing: 18) {
                ZStack {
                    Circle().stroke(Color(hex: 0xF0E2C2), lineWidth: 13)
                    Circle()
                        .trim(from: 0, to: ringRatio)
                        .stroke(.brandBlue, style: StrokeStyle(lineWidth: 13, lineCap: .round))
                        .rotationEffect(.degrees(-90))
                    VStack(spacing: 0) {
                        Text("\(timeManager.todaySeconds / 60)")
                            .font(.kidTitle(26))
                            .foregroundColor(.ink)
                        Text("/\(settings.settings.dailyMinutes) 分钟")
                            .font(.kidBody(11))
                            .foregroundColor(.inkSoft)
                    }
                }
                .frame(width: 116, height: 116)

                VStack(alignment: .leading, spacing: 6) {
                    Text("已用 \(timeManager.todaySeconds / 60) 分钟")
                    Text("剩余 \(timeManager.remainingTodaySeconds / 60) 分钟")
                    Text("休息 \(restCount) 次间隔")
                }
                .font(.kidBody(15))
                .foregroundColor(.inkSoft)

                Spacer()
            }
            Text("👀 超时会自动进入「小眼睛休息」画面，休息结束再继续")
                .font(.kidBody(14))
                .foregroundColor(Color(hex: 0x9A6B00))
                .padding(10)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 12).fill(Color(hex: 0xFFF3D8)))
        }
    }

    private var ringRatio: Double {
        guard timeManager.dailyLimitSeconds > 0 else { return 0 }
        return min(1, Double(timeManager.todaySeconds) / Double(timeManager.dailyLimitSeconds))
    }
    private var restCount: Int {
        timeManager.segmentSeconds / max(1, timeManager.restIntervalSeconds)
    }

    private var shieldPanel: some View {
        panel("shield", "护眼与时长管理") {
            segSetting("单次使用时长", values: [10, 15, 20, 25], current: settings.settings.onceMinutes, suffix: " 分钟") {
                settings.settings.onceMinutes = $0
                settings.save()
            }
            segSetting("每日使用上限", values: [30, 45, 60], current: settings.settings.dailyMinutes, suffix: " 分钟") {
                settings.settings.dailyMinutes = $0
                settings.save()
            }
            segSetting("休息间隔提醒", values: [15, 30, 0], current: settings.settings.restIntervalMinutes, suffix: "") { v in
                settings.settings.restIntervalMinutes = v
                settings.save()
            } label: { v in v == 0 ? "关闭" : "每 \(v) 分钟" }
        }
    }

    private func segSetting(_ title: String, values: [Int], current: Int, suffix: String,
                            onChange: @escaping (Int) -> Void,
                            label: ((Int) -> String)? = nil) -> some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(title).font(.kidBody(14.5)).foregroundColor(.ink)
            HStack(spacing: 7) {
                ForEach(values, id: \.self) { v in
                    let on = v == current
                    Button {
                        onChange(v)
                        toast.show("设置已保存", seconds: 1)
                    } label: {
                        Text(label?(v) ?? (v == 0 ? "关闭" : "\(v)\(suffix)"))
                            .font(.kidBody(14))
                            .foregroundColor(on ? .white : .inkSoft)
                            .padding(.horizontal, 13)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(on ? AnyShapeStyle(LinearGradient(colors: [.brandBlue, .brandBlueDk], startPoint: .top, endPoint: .bottom))
                                          : AnyShapeStyle(Color(hex: 0xF3EADA)))
                            )
                            .shadow(color: on ? .brandBlueDdk : Color(hex: 0xE2D4B8), radius: 0, x: 0, y: 3)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private var progressPanel: some View {
        panel("chart", "学习进度") {
            ForEach([("book", "识字村", "cn"), ("equal", "思维镇", "math"), ("speaker", "拼音谷", "pinyin"),
                     ("castle", "英语王国", "english"), ("moon", "天文台", "astro")], id: \.1) { icon, name, sub in
                let ids = LevelCatalog.ids(sub)
                let done = store.doneCount(subject: sub, ids: ids)
                progressRow(icon: icon, name: name,
                            ratio: Double(done) / Double(max(ids.count, 1)),
                            val: "\(done)/\(ids.count) 关")
            }
            progressRow(icon: "flask", name: "科学岛", ratio: Double(store.snapshot.collectedScience.count) / 6, val: "实验 \(store.snapshot.testedItems.count) 项")
            HStack(spacing: 8) {
                statChip("累计金币 \(store.snapshot.coins)")
                statChip("连击 \(store.snapshot.streak) 天")
                statChip("汉字 \(store.snapshot.learnedHanzi.count) 个")
            }
            HStack(spacing: 8) {
                statChip("拼音 \(store.snapshot.learnedPinyin.count) 个")
                statChip("单词 \(store.snapshot.learnedEnglish.count) 词")
                statChip("星空 \(store.snapshot.learnedAstro.count) 个")
            }
        }
    }

    private func progressRow(icon: String, name: String, ratio: Double, val: String) -> some View {
        HStack(spacing: 10) {
            IconView(name: icon, size: 20)
            Text(name).font(.kidBody(15)).foregroundColor(.ink).frame(width: 66, alignment: .leading)
            GoldTrack(ratio: ratio, height: 12)
            Text(val).font(.kidBody(13)).foregroundColor(.inkSoft).frame(width: 74, alignment: .trailing)
        }
    }

    private func statChip(_ text: String) -> some View {
        Text(text)
            .font(.kidBody(13))
            .foregroundColor(Color(hex: 0x9A6B00))
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Capsule().fill(Color(hex: 0xFFF3D8)))
    }

    private var controlPanel: some View {
        panel("slider", "难度与内容管理") {
            segSetting("难度模式", values: [0, 1, 2], current: difficultyValue, suffix: "") { v in
                settings.settings.difficulty = ["easy", "auto", "normal"][v]
                settings.save()
            } label: { v in ["简单", "自动适配", "标准"][v] }
            HStack(spacing: 10) {
                Button {
                    toast.show("跳过知识点功能将在二期提供")
                } label: {
                    Label("跳过知识点", systemImage: "forward.end")
                        .font(.kidBody(14))
                }
                .buttonStyle(.jellyCream)
            }
            Button {
                store.resetAll()
                timeManager.resetToday()
                toast.show("已重置全部学习进度")
            } label: {
                Label("重置全部进度", systemImage: "trash")
                    .font(.kidBody(14))
                    .foregroundColor(Color(hex: 0xC0392B))
            }
            .buttonStyle(JellyButtonStyle(
                base: Color(hex: 0xFFE3E0), dark: Color(hex: 0xFFCFC9),
                edge: Color(hex: 0xE8B7B0), textColor: Color(hex: 0xC0392B),
                fontSize: 14
            ))
        }
    }

    private var difficultyValue: Int {
        ["easy", "auto", "normal"].firstIndex(of: settings.settings.difficulty) ?? 1
    }

    private var promisesPanel: some View {
        panel("heart", "本产品承诺（家长可放心）") {
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())], alignment: .leading, spacing: 6) {
                promise("无广告 · 无推送 · 无外链")
                promise("无内购 · 无付费陷阱")
                promise("无社交 · 无陌生人接触")
                promise("数据只存在这台 iPad 上")
                promise("进入家长区需通过家长门")
                promise("超时自动提醒休息眼睛")
            }
        }
    }

    private func promise(_ text: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: "checkmark")
                .font(.system(size: 13, weight: .black))
                .foregroundColor(.brandGreenDk)
            Text(text).font(.kidBody(14)).foregroundColor(.inkSoft)
        }
    }
}
