# Knowledge Base Issues

| 问题 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| scan_raw.py 参数缺失 | 调用时返回 Usage 报错 | 脚本设计需要 kb_dir 参数，调用时未传入 | 修改脚本或确保调用时传入正确参数 |
| update_registry.py 参数数量错误 | 传入 4 个参数返回 Usage 报错 | 脚本只接受 3 个参数，多传了日期参数 | 移除多余参数，脚本内部自动获取日期 |
| update_registry.py 破坏 registry 格式 | 更新后"已编译"写入产物路径列 | 脚本按固定列索引更新，未识别列名语义 | 改用列名匹配或增加列数校验 |
| syntax.py 扫描范围错误 | 直接调用扫描 `.agents/` 目录 | 脚本接收 KB 根目录而非 wiki 目录 | 合并脚本或增加参数校验防护 |
| lint 脚本架构混淆 | syntax.py/semantic.py 可独立运行但不应独立调用 | 脚本设计为独立可执行但实际只应被 lint.py 调用 | 合并到 lint.py 或改为内部模块 |
| raw/path/to/file.md 意外创建 | 空占位文件被创建 | Obsidian/工具解析 AGENTS.md wikilink 示例并自动创建文件 | 将示例改为代码块格式避免解析 |
| read_registry.py 无法解析表格 | 输出 total:0 | 分隔符格式不匹配（`|------` vs `| ---------------- |`） | 修改脚本正则匹配宽松格式 |
| entities 子目录冗余 | wiki/entities/ 下不细分 person/event/place | minimal 架构设计扁平化，无需子分类 | 移除模板中的子目录概念，扁平存放 |
| wiki 文档缺失 frontmatter | 生成的 wiki 文档无 YAML frontmatter | 模板未包含 frontmatter 示例 | 添加 frontmatter 到模板（version, type, created 等） |