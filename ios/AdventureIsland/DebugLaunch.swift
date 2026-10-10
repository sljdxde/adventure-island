import Foundation

#if DEBUG
/// 调试用启动参数（仅 DEBUG 编译进 App，正式包不含此代码）：
/// - `-AISeed all`：把全部学科关卡置为三星通关（用于验证「全部通关后重新开始」流程）
/// - `-AISeed none`：清空全部进度
/// - `-AIRoute map|lab|collection|parent|level:<subject>:<index>`：直接进入指定页面
enum DebugLaunch {

    static func seedIfNeeded(store: ProgressStore) {
        let args = ProcessInfo.processInfo.arguments
        if args.contains("-AISeed") {
            let value = value(after: "-AISeed", in: args) ?? ""
            switch value {
            case "all":
                for subject in ["cn", "math", "pinyin", "english", "astro"] {
                    for (i, id) in LevelCatalog.ids(subject).enumerated() {
                        _ = i
                        store.snapshot.levelStars[id] = 3
                    }
                }
                for id in ["sci-apple", "sci-rock", "sci-wood", "sci-key", "sci-sponge", "sci-balloon"] {
                    if !store.snapshot.collectedScience.contains(id) {
                        store.snapshot.collectedScience.append(id)
                    }
                }
                store.save()
            case "none":
                store.resetAll()
            default:
                break
            }
        }
    }

    static func initialRoute() -> Route {
        let args = ProcessInfo.processInfo.arguments
        guard args.contains("-AIRoute"), let target = value(after: "-AIRoute", in: args) else {
            return .map
        }
        if target == "map" { return .map }
        if target == "lab" { return .lab }
        if target == "collection" { return .collection }
        if target == "parent" { return .parent }
        if target.hasPrefix("level:") {
            let parts = String(target.dropFirst("level:".count)).components(separatedBy: ":")
            if parts.count == 2, let index = Int(parts[1]) {
                return .level(subject: parts[0], index: index)
            }
        }
        #if DEBUG
        if target.hasPrefix("ceremony:") {
            let parts = String(target.dropFirst("ceremony:".count)).components(separatedBy: ":")
            if parts.count == 2, let index = Int(parts[1]) {
                return .debugCeremony(subject: parts[0], index: index,
                                      total: LevelCatalog.ids(parts[0]).count)
            }
        }
        #endif
        return .map
    }

    static func arg(_ flag: String) -> String? {
        value(after: flag, in: ProcessInfo.processInfo.arguments)
    }

    private static func value(after flag: String, in args: [String]) -> String? {
        guard let i = args.firstIndex(of: flag), i + 1 < args.count else { return nil }
        return args[i + 1]
    }
}
#endif
