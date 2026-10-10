import SwiftUI

// MARK: - v0.9 新题型总线（write / muldiv / cards / sudoku / clock / money / mappuzzle）
// 判题只做 schema 字段比较；答对庆祝+自动推进，答错轻提示不扣分可重答（防挫败铁律）。
// DEBUG 下每个交互题提供「自动完成」按钮（#if DEBUG），对齐 -AIStep/-AIFlip 调试缝。

extension Color {
    /// "#RRGGBB" → Color（地图块配色等）
    init(hexString: String) {
        let s = hexString.replacingOccurrences(of: "#", with: "")
        var v: UInt64 = 0
        Scanner(string: s).scanHexInt64(&v)
        self.init(red: Double((v & 0xFF0000) >> 16) / 255.0,
                  green: Double((v & 0xFF00) >> 8) / 255.0,
                  blue: Double(v & 0xFF) / 255.0)
    }
}

/// SVG path(M/L/Q) 拍平成 100 坐标系点列（写字描红用）
enum StrokePath {
    static func points(_ d: String) -> [CGPoint] {
        let regex = try! NSRegularExpression(pattern: "M|L|Q|-?\\d+(?:\\.\\d+)?")
        let range = NSRange(d.startIndex..., in: d)
        let matches = regex.matches(in: d, range: range)
        var toks: [String] = []
        for m in matches { toks.append(String(d[Range(m.range, in: d)!])) }
        var pts: [CGPoint] = []
        var cur = CGPoint.zero
        var cmd = "M"
        var i = 0
        func num(_ idx: Int) -> CGFloat? {
            guard idx < toks.count else { return nil }
            return Double(toks[idx]).map(CGFloat.init)
        }
        while i < toks.count {
            let t = toks[i]
            if t == "M" || t == "L" || t == "Q" { cmd = t; i += 1; continue }
            if cmd == "Q",
               let c1x = num(i), let c1y = num(i + 1),
               let c2x = num(i + 2), let c2y = num(i + 3) {
                let c1 = CGPoint(x: c1x, y: c1y), c2 = CGPoint(x: c2x, y: c2y)
                for k in 1...14 {
                    let tt = CGFloat(k) / 14
                    let x = (1 - tt) * (1 - tt) * cur.x + 2 * (1 - tt) * tt * c1.x + tt * tt * c2.x
                    let y = (1 - tt) * (1 - tt) * cur.y + 2 * (1 - tt) * tt * c1.y + tt * tt * c2.y
                    pts.append(CGPoint(x: x, y: y))
                }
                cur = c2
                i += 4
                continue
            }
            if let x = num(i), let y = num(i + 1) {
                let p = CGPoint(x: x, y: y)
                if cmd == "M" { pts = [p] } else { pts.append(p) }
                cur = p
                i += 2
                continue
            }
            i += 1
        }
        return pts
    }

    /// 多段线最近点：返回(参数 t∈0..1, 距离)
    static func closest(on pts: [CGPoint], to p: CGPoint) -> (t: CGFloat, dist: CGFloat) {
        guard pts.count >= 2 else { return (0, 1e9) }
        var lengths: [CGFloat] = [0]
        for i in 1..<pts.count {
            lengths.append(lengths.last! + hypot(pts[i].x - pts[i-1].x, pts[i].y - pts[i-1].y))
        }
        let total = lengths.last!
        var bestD = CGFloat(1e9), bestCum = CGFloat(0)
        for i in 1..<pts.count {
            let a = pts[i-1], b = pts[i]
            let abx = b.x - a.x, aby = b.y - a.y
            let len2 = abx*abx + aby*aby
            var t = len2 > 0 ? ((p.x - a.x) * abx + (p.y - a.y) * aby) / len2 : 0
            t = max(0, min(1, t))
            let px = a.x + t * abx, py = a.y + t * aby
            let d = hypot(p.x - px, p.y - py)
            if d < bestD { bestD = d; bestCum = lengths[i-1] + t * (lengths[i] - lengths[i-1]) }
        }
        return (total > 0 ? bestCum / total : 0, bestD)
    }
}

#if DEBUG
/// 仅 DEBUG 显示的「自动完成」小按钮（交互题调试缝）
struct AutoSolveButton: View {
    let action: () -> Void
    var body: some View {
        Button { action() } label: {
            Text("自动完成")
                .font(.system(size: 12, weight: .heavy, design: .rounded))
                .foregroundColor(.white)
                .padding(.horizontal, 12).padding(.vertical, 5)
                .background(Capsule().fill(LinearGradient(colors: [.brandPurple, .brandPurpleDk], startPoint: .top, endPoint: .bottom)))
        }
        .buttonStyle(.plain)
    }
}
#endif

// MARK: 题目头胶囊（与既有题型一致）
private struct StepHeader: View {
    let text: String
    var body: some View {
        Text(text)
            .font(.kidHead(23))
            .foregroundColor(.ink)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 28).padding(.vertical, 11)
            .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFF3D8), Color(hex: 0xFFE9BC)], startPoint: .top, endPoint: .bottom)))
    }
}

// MARK: - write（写字：田字格逐笔描红）

struct WriteStepView: View {
    let step: Step
    let subject: String
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var store: ProgressStore
    @Environment(\.soundService) private var sound
    @State private var strokeIndex = 0
    @State private var done: [Bool] = []
    @State private var progress: CGFloat = 0
    @State private var finished = false
    @State private var demoTick = 0
    @State private var demoProgress: CGFloat = 0

    private var strokes: [[CGPoint]] {
        (step.strokes ?? []).map { StrokePath.points($0.d) }
    }

    var body: some View {
        VStack(spacing: 16) {
            StepHeader(text: step.question ?? "写一写：看一笔、描一笔")
            HStack(spacing: 20) {
                // 左：田字格
                ZStack {
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(Color(hex: 0xFFFDF6))
                        .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Color(hex: 0xE86A5A), lineWidth: 3))
                    // 十字中线（随田字格框居中缩放）
                    TianGridLines()
                        .stroke(Color(hex: 0xF0B7AE), style: StrokeStyle(lineWidth: 1, dash: [3, 3]))
                    // 全部笔画淡底
                    ForEach(0..<strokes.count, id: \.self) { i in
                        StrokePolyline(pts: strokes[i])
                            .stroke(done[safe: i] == true ? Color(hex: 0xE2582A) : Color(hex: 0xE7DCC8),
                                    style: StrokeStyle(lineWidth: 6, lineCap: .round, lineJoin: .round))
                    }
                    // 当前笔已描部分
                    if strokeIndex < strokes.count, done[safe: strokeIndex] != true {
                        StrokePolyline(pts: sampledProgress(strokes[strokeIndex]))
                            .stroke(Color(hex: 0x4FA9E8), style: StrokeStyle(lineWidth: 7, lineCap: .round, lineJoin: .round))
                    }
                    // 「看一笔」演示：当前笔按路径生长（运笔方向动画）
                    if demoProgress > 0, strokeIndex < strokes.count {
                        let demoPts = strokes[strokeIndex]
                        let upto = max(1, Int(CGFloat(demoPts.count) * demoProgress))
                        StrokePolyline(pts: Array(demoPts.prefix(upto)))
                            .stroke(Color(hex: 0xE2582A),
                                    style: StrokeStyle(lineWidth: 8, lineCap: .round, lineJoin: .round))
                    }
                }
                .frame(width: 280, height: 280)
                .aspectRatio(1, contentMode: .fit)
                .overlay(GeometryReader { geo in
                    Color.clear.contentShape(Rectangle())
                        .gesture(DragGesture(minimumDistance: 0)
                            .onChanged { v in
                                trace(at: v.location, size: geo.size)
                            })
                })

                // 右：演示 + 完成
                VStack(spacing: 14) {
                    Text(step.char ?? "")
                        .font(.hanzi(96))
                        .foregroundColor(Color(hex: 0xE2582A))
                    if let py = step.pinyin, !py.isEmpty {
                        Text(py).font(.kidTitle(26)).foregroundColor(.brandCoralDk)
                    }
                    Button {
                        demoTick += 1
                        demoProgress = 0
                        sound.systemTap()
                        withAnimation(.linear(duration: 0.8)) { demoProgress = 1 }
                    } label: {
                        Label("看一笔", systemImage: "play.fill").font(.kidHead(17))
                    }
                    .buttonStyle(.jellyBlue)
                    if finished {
                        Text(step.praise ?? "写得真好！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
                    }
                    #if DEBUG
                    AutoSolveButton { autoFinish() }
                    #endif
                }
                .frame(maxWidth: .infinity)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
        .onAppear { if done.isEmpty { done = Array(repeating: false, count: strokes.count) } }
    }

    /// 取前 progress 比例的点列（用于画已描部分）
    private func sampledProgress(_ pts: [CGPoint]) -> [CGPoint] {
        guard pts.count > 1 else { return pts }
        let upto = max(1, Int(CGFloat(pts.count) * progress))
        return Array(pts.prefix(upto))
    }

    private func trace(at loc: CGPoint, size: CGSize) {
        guard !finished, strokeIndex < strokes.count, done[safe: strokeIndex] != true else { return }
        let unit = CGPoint(x: loc.x / size.width * 100, y: loc.y / size.height * 100)
        let pts = strokes[strokeIndex]
        let r = StrokePath.closest(on: pts, to: unit)
        let tol: CGFloat = 16   // 容差（约 12~16 单位，宽容防挫败）
        if r.dist < tol {
            progress = max(progress, r.t)
            if progress >= 0.92 {
                done[strokeIndex] = true
                sound.systemTap()
                progress = 0
                if strokeIndex < strokes.count - 1 {
                    strokeIndex += 1
                } else {
                    finish()
                }
            }
        }
    }

    private func finish() {
        finished = true
        if subject == "cn", let ch = step.char { store.learnHanzi(ch) }   // 写完才入册
        sound.correct()
        onCorrectCelebrate()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { onNext() }
    }

    private func autoFinish() {
        for i in done.indices { done[i] = true }
        strokeIndex = strokes.count
        finish()
    }
}

/// 把 100 坐标点列画在 0..100 画布内
struct StrokePolyline: Shape {
    let pts: [CGPoint]
    func path(in rect: CGRect) -> Path {
        var p = Path()
        guard let first = pts.first else { return p }
        let sx = rect.width / 100, sy = rect.height / 100
        p.move(to: CGPoint(x: first.x * sx, y: first.y * sy))
        for pt in pts.dropFirst() { p.addLine(to: CGPoint(x: pt.x * sx, y: pt.y * sy)) }
        return p
    }
}

/// 田字格十字中线（随矩形居中）
struct TianGridLines: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: rect.midX, y: rect.minY)); p.addLine(to: CGPoint(x: rect.midX, y: rect.maxY))
        p.move(to: CGPoint(x: rect.minX, y: rect.midY)); p.addLine(to: CGPoint(x: rect.maxX, y: rect.midY))
        return p
    }
}

// MARK: - muldiv（乘除可视化）

struct MulDivStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongValue: Int?

    private var options: [Int] { step.options?.intList ?? step.arithOptions ?? [] }

    var body: some View {
        VStack(spacing: 18) {
            StepHeader(text: step.question ?? "")
            visualization
            HStack(spacing: 22) {
                ForEach(Array(options.enumerated()), id: \.offset) { _, n in
                    numberBlock(n)
                }
            }
            if solved {
                Text(step.praise ?? "答对啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    @ViewBuilder
    private var visualization: some View {
        let icon = step.icon ?? "duck"
        if step.op == "×" {
            // groups 组 × per 个
            let g = step.groups ?? 1, per = step.per ?? 1
            VStack(spacing: 8) {
                ForEach(0..<g, id: \.self) { _ in
                    HStack(spacing: 6) { ForEach(0..<per, id: \.self) { _ in IconView(name: icon, size: 40) } }
                }
            }
        } else if step.mode == "average" {
            // total 个平均分到 groups 盘
            let groups = step.groups ?? 1, total = step.total ?? 1
            let per = max(1, total / max(1, groups))
            HStack(spacing: 12) {
                ForEach(0..<groups, id: \.self) { _ in
                    VStack {
                        HStack(spacing: 2) { ForEach(0..<per, id: \.self) { _ in IconView(name: icon, size: 26) } }
                        Text("盘").font(.kidBody(12)).foregroundColor(.inkSoft)
                    }
                }
            }
        } else {
            // contain：每盘 per 个，共 total/per 盘
            let per = step.per ?? 1, total = step.total ?? 1
            let plates = max(1, total / max(1, per))
            HStack(spacing: 10) {
                ForEach(0..<plates, id: \.self) { _ in
                    VStack {
                        HStack(spacing: 2) { ForEach(0..<per, id: \.self) { _ in IconView(name: icon, size: 26) } }
                    }
                }
            }
        }
    }

    private func numberBlock(_ n: Int) -> some View {
        Button {
            guard !solved else { return }
            if n == correctAnswer {
                solved = true
                sound.correct()
                onCorrectCelebrate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { onNext() }
            } else {
                wrongValue = n
                sound.wrong()
                onWrong()
                toast.show(step.hint ?? "再数一数图上有几个", seconds: 2.0)
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongValue = nil }
            }
        } label: {
            Text("\(n)")
                .font(.kidTitle(42))
                .foregroundColor(Color(hex: 0x8A5B00))
                .frame(width: 92, height: 84)
                .background(RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom)))
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Color(hex: 0xB8770A), lineWidth: 3.5))
        }
        .buttonStyle(.plain)
        .modifier(ShakeModifier(shake: wrongValue == n))
    }

    private var correctAnswer: Int {
        // answer 是正确选项下标（schema）
        let a = step.answer ?? 0
        return options[safe: a] ?? 0
    }
}

// MARK: - cards（扑克凑十 / 凑目标）

struct CardsStepView: View {
    let step: Step
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var selected: Set<Int> = []
    @State private var solved = false
    @State private var bad = false

    private let suits = ["♠️", "♥️", "♦️", "♣️"]
    private var cards: [Int] { step.cards?.valueList ?? [] }
    private var target: Int { step.target ?? 10 }
    private var pick: Int { step.pick ?? (step.mode == "make10" ? 2 : 3) }

    var body: some View {
        VStack(spacing: 18) {
            StepHeader(text: step.question ?? "点牌凑一凑")
            Text("目标 \(target) ｜ 已选 \(selected.count)/\(pick) 张")
                .font(.kidHead(17)).foregroundColor(.inkSoft)
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 96, maximum: 120), spacing: 14)], spacing: 14) {
                ForEach(Array(cards.enumerated()), id: \.offset) { i, v in
                    cardView(i, v)
                }
            }
            if solved {
                Text(step.praise ?? "凑成啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            }
            #if DEBUG
            AutoSolveButton { autoSolve() }
            #endif
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func cardView(_ i: Int, _ v: Int) -> some View {
        let isSel = selected.contains(i)
        return Button {
            guard !solved else { return }
            if isSel { selected.remove(i) } else {
                guard selected.count < pick else { return }
                selected.insert(i)
                sound.systemTap()
                if selected.count == pick { evaluate() }
            }
        } label: {
            ZStack(alignment: .topTrailing) {
                VStack(spacing: 2) {
                    Text("\(v)").font(.system(size: 30, weight: .heavy, design: .rounded))
                    Text(suits[i % 4]).font(.system(size: 16))
                }
            }
            .frame(width: 84, height: 104)
            .background(RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(isSel ? LinearGradient(colors: [Color(hex: 0xD7F0DB), .white], startPoint: .top, endPoint: .bottom) : LinearGradient(colors: [.white, Color(hex: 0xF6F9FF)], startPoint: .top, endPoint: .bottom)))
            .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(isSel ? Color(hex: 0x3BA851) : Color(hex: 0xD8E2F8), lineWidth: isSel ? 4 : 2.5))
            .scaleEffect(isSel ? 1.06 : 1)
            .modifier(ShakeModifier(shake: bad && isSel))
        }
        .buttonStyle(.plain)
    }

    private func evaluate() {
        let chosen = selected.map { cards[$0] }
        let ok: Bool
        if step.mode == "make10" {
            ok = chosen.reduce(0, +) == target
        } else {
            // target：三张可加可减，存在符号组合等于 target
            ok = signComboSums(chosen).contains(target)
        }
        if ok {
            solved = true
            sound.correct()
            onCorrectCelebrate()
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { onNext() }
        } else {
            bad = true
            sound.wrong()
            toast.show("再换一换，凑成 \(target) 哦", seconds: 1.6)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                selected.removeAll(); bad = false
            }
        }
    }

    private func signComboSums(_ nums: [Int]) -> [Int] {
        guard let first = nums.first else { return [] }
        var results: Set<Int> = [first, -first]
        for n in nums.dropFirst() {
            var next: Set<Int> = []
            for r in results { next.insert(r + n); next.insert(r - n) }
            results = next
        }
        return Array(results)
    }

    private func autoSolve() {
        // 数据保证至少一组合法解：make10 找两张和为 target；target 找前三张里可行组合
        if step.mode == "make10" {
            for i in cards.indices { for j in i+1..<cards.count {
                if cards[i] + cards[j] == target { selected = [i, j]; evaluate(); return }
            }}
        } else {
            // 试所有三元组的符号组合
            for i in cards.indices { for j in i+1..<cards.count { for k in j+1..<cards.count {
                let trio = [cards[i], cards[j], cards[k]]
                if signComboSums(trio).contains(target) { selected = [i, j, k]; evaluate(); return }
            }}}
        }
    }
}

// MARK: - sudoku（4×4 图标数独）

struct SudokuStepView: View {
    let step: Step
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var grid: [[Int?]] = Array(repeating: Array(repeating: nil, count: 4), count: 4)
    @State private var locked: [[Bool]] = Array(repeating: Array(repeating: false, count: 4), count: 4)
    @State private var selected: (r: Int, c: Int)?
    @State private var wrongCell: (r: Int, c: Int)?
    @State private var solved = false

    private let n = 4
    private var symbols: [String] { step.symbols ?? [] }
    private var solution: [[Int]] { step.solution ?? [] }

    var body: some View {
        VStack(spacing: 16) {
            StepHeader(text: step.question ?? "图案数独")
            gridView
            palette
            if solved { Text(step.praise ?? "推理成功！").font(.kidHead(20)).foregroundColor(.brandGreenDk) }
            #if DEBUG
            AutoSolveButton { autoSolve() }
            #endif
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
        .onAppear { setup() }
    }

    private func setup() {
        grid = Array(repeating: Array(repeating: nil, count: n), count: n)
        locked = Array(repeating: Array(repeating: false, count: n), count: n)
        for g in step.givens ?? [] where g.r < n && g.c < n {
            grid[g.r][g.c] = g.v
            locked[g.r][g.c] = true
        }
    }

    private var gridView: some View {
        VStack(spacing: 4) {
            ForEach(0..<n, id: \.self) { r in
                HStack(spacing: 4) {
                    ForEach(0..<n, id: \.self) { c in
                        cell(r, c)
                    }
                }
            }
        }
        .padding(8)
        .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Color(hex: 0xEFE7D2)))
    }

    private func cell(_ r: Int, _ c: Int) -> some View {
        let v = grid[safe: r]?[safe: c] ?? nil
        let isSel = selected?.r == r && selected?.c == c
        let isLocked = locked[safe: r]?[safe: c] ?? false
        return Button {
            guard !isLocked, !solved else { return }
            selected = (r, c)
        } label: {
            ZStack {
                if let v, v < symbols.count {
                    IconView(name: symbols[v], size: 40)
                }
            }
            .frame(width: 72, height: 72)
            .background(RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(isLocked ? Color(hex: 0xE3D8BC) : (isSel ? Color(hex: 0xFFF0C2) : .white)))
            .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(isSel ? Color(hex: 0xF0A030) : Color(hex: 0xD8CBAF), lineWidth: isSel ? 3 : 1.5))
            .modifier(ShakeModifier(shake: wrongCell?.r == r && wrongCell?.c == c))
        }
        .buttonStyle(.plain)
    }

    private var palette: some View {
        HStack(spacing: 12) {
            ForEach(0..<symbols.count, id: \.self) { i in
                Button { place(i) } label: {
                    IconView(name: symbols[i], size: 46)
                        .frame(width: 60, height: 60)
                        .background(Circle().fill(Color(hex: 0xFFF3D8)))
                        .overlay(Circle().stroke(Color(hex: 0xE8C878), lineWidth: 2))
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func place(_ v: Int) {
        guard let (r, c) = selected, !locked[r][c], !solved else { return }
        // 行列宫冲突则弹回（不扣分）
        if createsConflict(r, c, v) {
            wrongCell = (r, c)
            sound.wrong()
            toast.show("这一行/列/宫已经有它啦", seconds: 1.4)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { wrongCell = nil }
            return
        }
        grid[r][c] = v
        sound.systemTap()
        checkComplete()
    }

    private func createsConflict(_ r: Int, _ c: Int, _ v: Int) -> Bool {
        for i in 0..<n {
            if i != c && grid[r][i] == v { return true }
            if i != r && grid[i][c] == v { return true }
        }
        let br = (r / 2) * 2, bc = (c / 2) * 2
        for rr in br..<br+2 { for cc in bc..<bc+2 {
            if rr != r || cc != c { if grid[rr][cc] == v { return true } }
        }}
        return false
    }

    private func checkComplete() {
        // 与 solution 完全一致即完成（数据保证唯一解）
        for r in 0..<n { for c in 0..<n {
            if grid[safe: r]?[safe: c] ?? nil != (solution[safe: r]?[safe: c] ?? -1) { return }
        }}
        solved = true
        sound.correct()
        onCorrectCelebrate()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { onNext() }
    }

    private func autoSolve() {
        for r in 0..<n { for c in 0..<n { if !locked[r][c] { grid[r][c] = solution[safe: r]?[safe: c] } } }
        checkComplete()
    }
}

// MARK: - clock（看钟选时间 / 拨针）

struct ClockStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var hour: Int
    @State private var minute: Int
    @State private var solved = false
    @State private var wrongIndex: Int?

    init(step: Step, onWrong: @escaping () -> Void, onNext: @escaping () -> Void, onCorrectCelebrate: @escaping () -> Void) {
        self.step = step
        self.onWrong = onWrong
        self.onNext = onNext
        self.onCorrectCelebrate = onCorrectCelebrate
        _hour = State(initialValue: step.hour ?? 3)
        _minute = State(initialValue: step.minute ?? 0)
    }

    private var options: [String] { step.options?.stringList ?? [] }

    var body: some View {
        VStack(spacing: 18) {
            StepHeader(text: step.question ?? "看钟面")
            ClockFace(hour: hour, minute: minute)
                .frame(width: 220, height: 220)
            if step.mode == "set" {
                setControls
            } else {
                HStack(spacing: 18) {
                    ForEach(Array(options.enumerated()), id: \.offset) { i, t in
                        optionButton(i, t)
                    }
                }
            }
            if solved { Text(step.praise ?? "认时小达人！").font(.kidHead(20)).foregroundColor(.brandGreenDk) }
            #if DEBUG
            AutoSolveButton { autoSolve() }
            #endif
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func optionButton(_ i: Int, _ t: String) -> some View {
        Button {
            guard !solved else { return }
            if i == (step.answer ?? 0) {
                solved = true; sound.correct(); onCorrectCelebrate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { onNext() }
            } else {
                wrongIndex = i; sound.wrong(); onWrong()
                toast.show("再看看时针和分针", seconds: 1.6)
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { wrongIndex = nil }
            }
        } label: {
            Text(t).font(.kidTitle(30)).foregroundColor(.ink)
                .frame(width: 120, height: 64)
                .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(wrongIndex == i ? Color(hex: 0xFFE0DA) : Color(hex: 0xFFF3D8)))
                .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(Color(hex: 0xE8C878), lineWidth: 2))
        }
        .buttonStyle(.plain)
        .modifier(ShakeModifier(shake: wrongIndex == i))
    }

    private var setControls: some View {
        VStack(spacing: 10) {
            HStack(spacing: 14) {
                stepper("时", hour, { hour = (hour % 12) + 1 }, { hour = hour == 1 ? 12 : hour - 1 })
                stepper("分", minute == 30 ? 30 : 0, { minute = 30 }, { minute = 0 })
            }
            Button {
                if hour == (step.hour ?? 3) && minute == (step.minute ?? 0) {
                    solved = true; sound.correct(); onCorrectCelebrate()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { onNext() }
                } else {
                    sound.wrong(); onWrong()
                    toast.show("再拨一拨，对准目标时间", seconds: 1.6)
                }
            } label: {
                Label("确认", systemImage: "checkmark").font(.kidHead(19))
            }.buttonStyle(.jellyGreen)
        }
    }

    private func stepper(_ label: String, _ value: Int, _ up: @escaping () -> Void, _ down: @escaping () -> Void) -> some View {
        HStack(spacing: 8) {
            Text(label).font(.kidHead(18)).foregroundColor(.inkSoft)
            Button(action: down) { Image(systemName: "minus").font(.system(size: 16, weight: .heavy)) }
                .buttonStyle(.plain).frame(width: 34, height: 34).background(Circle().fill(Color(hex: 0xFFE3B3)))
            Text(label == "时" ? "\(hour)" : (minute == 30 ? "30" : "00")).font(.kidTitle(24)).foregroundColor(.ink).frame(width: 44)
            Button(action: up) { Image(systemName: "plus").font(.system(size: 16, weight: .heavy)) }
                .buttonStyle(.plain).frame(width: 34, height: 34).background(Circle().fill(Color(hex: 0xFFE3B3)))
        }
    }

    private func autoSolve() {
        hour = step.hour ?? 3; minute = step.minute ?? 0
        if step.mode == "set" {
            solved = true; sound.correct(); onCorrectCelebrate()
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { onNext() }
        }
    }
}

/// 程序化钟面：1-12 刻度 + 短时针 + 长分针
struct ClockFace: View {
    let hour: Int
    let minute: Int
    var body: some View {
        ZStack {
            Circle().fill(LinearGradient(colors: [.white, Color(hex: 0xFFF6E0)], startPoint: .top, endPoint: .bottom))
                .overlay(Circle().stroke(Color(hex: 0xE8C878), lineWidth: 4))
            ForEach(1...12, id: \.self) { h in
                let angle = Angle(degrees: Double(h) * 30 - 90)
                Text("\(h)").font(.system(size: 15, weight: .bold)).foregroundColor(.ink)
                    .position(x: 110 + cos(angle.radians) * 84, y: 110 + sin(angle.radians) * 84)
            }
            // 时针（短）
            hand(angle: Double(hour % 12) * 30 + Double(minute) * 0.5, length: 46, width: 6, color: .ink)
            // 分针（长）
            hand(angle: Double(minute) * 6, length: 68, width: 4, color: .brandCoralDk)
            Circle().fill(Color.hex_ink).frame(width: 10, height: 10)
        }
    }
    private func hand(angle: Double, length: CGFloat, width: CGFloat, color: Color) -> some View {
        Rectangle().fill(color).frame(width: width, height: length)
            .offset(y: -length / 2)
            .rotationEffect(Angle(degrees: angle))
    }
}
extension Color {
    static let hex_ink = Color(hex: 0x57433A)
}

// MARK: - money（人民币选币，角为单位）

struct MoneyStepView: View {
    let step: Step
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var selected: [Int] = []   // 选中的 denomination 下标（可重复）
    @State private var solved = false

    private var price: Int { step.price ?? 0 }
    private var denoms: [Denomination] { step.denominations ?? [] }
    private var total: Int { selected.reduce(0) { $0 + denoms[$1].value } }

    var body: some View {
        VStack(spacing: 16) {
            StepHeader(text: step.question ?? "买东西，付钱")
            Text("标价 \(yuanText)")
                .font(.kidTitle(30)).foregroundColor(Color(hex: 0xC24836))
            Text("已付 \(total) 角（\(paidText)）")
                .font(.kidHead(17)).foregroundColor(.inkSoft)
            HStack(spacing: 12) {
                ForEach(Array(denoms.enumerated()), id: \.offset) { i, d in
                    Button {
                        guard !solved else { return }
                        selected.append(i)
                        sound.systemTap()
                    } label: {
                        VStack(spacing: 2) {
                            IconView(name: d.icon ?? "coin", size: 40)
                            Text(d.label).font(.system(size: 12, weight: .bold)).foregroundColor(.ink)
                        }
                        .frame(width: 78, height: 84)
                        .background(RoundedRectangle(cornerRadius: 12, style: .continuous)
                            .fill(LinearGradient(colors: [Color(hex: 0xEAFBE7), Color(hex: 0xCDEFC8)], startPoint: .top, endPoint: .bottom)))
                        .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(Color(hex: 0x9BD08E), lineWidth: 2))
                    }
                    .buttonStyle(.plain)
                }
            }
            // 已选币（点一下去掉）
            if !selected.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(Array(selected.enumerated()), id: \.offset) { idx, di in
                            Text("\(denoms[di].label)")
                                .font(.system(size: 14, weight: .bold)).foregroundColor(.white)
                                .padding(.horizontal, 10).padding(.vertical, 6)
                                .background(Capsule().fill(Color(hex: 0x58C96B)))
                                .onTapGesture { selected.remove(at: idx) }
                        }
                    }
                }
                .frame(maxWidth: 320)
            }
            Button { confirm() } label: { Label("确认付钱", systemImage: "checkmark").font(.kidHead(19)) }
                .buttonStyle(.jellyGreen)
            if solved { Text(step.praise ?? "正好付清！").font(.kidHead(20)).foregroundColor(.brandGreenDk) }
            #if DEBUG
            AutoSolveButton { autoSolve() }
            #endif
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private var yuanText: String {
        let y = price / 10, j = price % 10
        return y > 0 ? (j > 0 ? "\(y)元\(j)角" : "\(y)元") : "\(j)角"
    }
    private var paidText: String {
        let y = total / 10, j = total % 10
        return y > 0 ? (j > 0 ? "\(y)元\(j)角" : "\(y)元") : "\(j)角"
    }

    private func confirm() {
        guard !solved else { return }
        if total == price {
            solved = true; sound.correct(); onCorrectCelebrate()
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { onNext() }
        } else if total > price {
            sound.wrong()
            toast.show("付多啦，点已选的钱币去掉一些", seconds: 1.8)
        } else {
            sound.wrong()
            toast.show("还差 \(price - total) 角，再加点钱", seconds: 1.8)
        }
    }

    private func autoSolve() {
        selected.removeAll()
        var remain = price
        for d in denoms.sorted(by: { $0.value > $1.value }) where remain > 0 {
            while remain >= d.value { selected.append(denoms.firstIndex(of: d)!); remain -= d.value }
        }
        confirm()
    }
}

// MARK: - mappuzzle（地理拼图：上地图 + 下托盘，严格吸附归位）

struct MapPuzzleStepView: View {
    let step: Step
    let subject: String
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var store: ProgressStore
    @Environment(\.soundService) private var sound
    @State private var placed: Set<String> = []
    @State private var dragging: MapRegion?
    @State private var fingerMap: CGPoint = .zero   // 手指在地图 viewBox(0..100, 0..60) 中的位置
    @State private var mapFrame: CGRect = .zero       // 地图区在 named 坐标空间中的位置
    @State private var solved = false

    private var regions: [MapRegion] { step.regions ?? [] }
    private let snapTolerance: CGFloat = 12          // viewBox 单位容差

    var body: some View {
        VStack(spacing: 12) {
            StepHeader(text: step.question ?? "把地图块拖回虚线轮廓")

            // 上方：地图区（viewBox 0 0 100 60）
            mapArea
                .aspectRatio(100.0 / 60.0, contentMode: .fit)
                .padding(.horizontal, 22)

            // 下方：托盘（未归位块横向排列，固定高度，不与地图重叠）
            tray
                .frame(height: 96)
                .padding(.horizontal, 22)

            Text(placed.count == regions.count ? (step.praise ?? "拼好啦！") : "已拼 \(placed.count)/\(regions.count) 块")
                .font(.kidHead(17)).foregroundColor(placed.count == regions.count ? .brandGreenDk : .inkSoft)
            #if DEBUG
            AutoSolveButton { autoSolve() }
            #endif
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
        .coordinateSpace(name: "mapPuzzle")
    }

    private var mapArea: some View {
        GeometryReader { geo in
            ZStack {
                // 轮廓：未归位=浅色虚线；归位=实色填充+白描边
                ForEach(regions) { r in
                    RegionShape(points: r.points)
                        .fill(placed.contains(r.id) ? Color(hexString: r.color ?? "#999999") : Color.clear)
                        .overlay(
                            RegionShape(points: r.points)
                                .stroke(placed.contains(r.id) ? Color.white : Color(hexString: r.color ?? "#999999"),
                                        style: StrokeStyle(lineWidth: placed.contains(r.id) ? 2 : 1.5,
                                                           dash: placed.contains(r.id) ? [] : [4, 4]))
                        )
                }
                // 跟随手指的被拖块（居中在手指位置）
                if let r = dragging {
                    RegionShape(points: r.points)
                        .fill(Color(hexString: r.color ?? "#999999").opacity(0.92))
                        .overlay(RegionShape(points: r.points).stroke(.white, lineWidth: 2))
                        .overlay(Text(r.label).font(.system(size: 10, weight: .heavy)).foregroundColor(.white))
                        .frame(width: 96, height: 58)
                        .position(x: fingerMap.x / 100 * geo.size.width,
                                  y: fingerMap.y / 60 * geo.size.height)
                }
            }
            .frame(width: geo.size.width, height: geo.size.height)
            .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Color(hex: 0xEAF6FF)))
            .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(Color(hex: 0xBBDDF2), lineWidth: 2))
            .onAppear { mapFrame = geo.frame(in: .named("mapPuzzle")) }
            .onChange(of: geo.size) { _ in mapFrame = geo.frame(in: .named("mapPuzzle")) }
        }
    }

    private var tray: some View {
        HStack(spacing: 16) {
            ForEach(regions.filter { !placed.contains($0.id) && dragging?.id != $0.id }) { r in
                VStack(spacing: 2) {
                    RegionShape(points: r.points)
                        .fill(Color(hexString: r.color ?? "#999999"))
                        .overlay(RegionShape(points: r.points).stroke(.white, lineWidth: 1.5))
                        .frame(width: 60, height: 38)
                    Text(r.label).font(.system(size: 12, weight: .heavy)).foregroundColor(.ink)
                }
                .gesture(dragGesture(r))
            }
        }
        .frame(maxWidth: .infinity, alignment: .center)
    }

    private func dragGesture(_ r: MapRegion) -> some Gesture {
        DragGesture(minimumDistance: 5, coordinateSpace: .named("mapPuzzle"))
            .onChanged { v in
                dragging = r
                fingerMap = toMapVB(v.location)
            }
            .onEnded { v in
                // 严格吸附：手指落点 vs 该块自己的目标质心（viewBox 距离）
                let pt = toMapVB(v.location)
                let c = regionCenter(r)
                let d = hypot(pt.x - c.x, pt.y - c.y)
                if d < snapTolerance {
                    placed.insert(r.id)
                    sound.correct()
                    if placed.count == regions.count { finish() }
                }
                // 否则弹回托盘（不扣分、无负面文案）
                dragging = nil
            }
    }

    /// named 坐标点 → 地图 viewBox(0..100, 0..60)
    private func toMapVB(_ p: CGPoint) -> CGPoint {
        guard mapFrame.width > 0, mapFrame.height > 0 else { return .zero }
        let lx = p.x - mapFrame.origin.x
        let ly = p.y - mapFrame.origin.y
        return CGPoint(x: lx / mapFrame.width * 100, y: ly / mapFrame.height * 60)
    }

    private func regionCenter(_ r: MapRegion) -> CGPoint {
        let xs = r.points.map { $0[0] }, ys = r.points.map { $0[1] }
        guard let x0 = xs.min(), let x1 = xs.max(), let y0 = ys.min(), let y1 = ys.max() else { return .zero }
        return CGPoint(x: (x0 + x1) / 2, y: (y0 + y1) / 2)
    }

    private func finish() {
        for r in regions { store.learnGeo(r.id) }
        solved = true
        onCorrectCelebrate()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) { onNext() }
    }

    private func autoSolve() {
        placed = Set(regions.map { $0.id })
        finish()
    }
}

/// viewBox 0 0 100 60 多边形
struct RegionShape: Shape {
    let points: [[Double]]
    func path(in rect: CGRect) -> Path {
        var p = Path()
        guard let first = points.first else { return p }
        let sx = rect.width / 100, sy = rect.height / 60
        p.move(to: CGPoint(x: first[0] * sx, y: first[1] * sy))
        for pt in points.dropFirst() { p.addLine(to: CGPoint(x: pt[0] * sx, y: pt[1] * sy)) }
        p.closeSubpath()
        return p
    }
}
