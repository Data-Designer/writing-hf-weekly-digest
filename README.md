# writing-hf-weekly-digest

一个用于生成中文 Hugging Face / arXiv 论文周报的 Codex Skill，支持：

- 冻结指定自然周或日期区间的 Hugging Face Daily Papers 数据；
- 生成研究情报、详细周报或 PaperScope 风格微信公众号文章；
- 从论文官方项目页、arXiv HTML 和论文 PDF 选取原生框架图；
- 输出 Markdown、微信友好 HTML、图片清单和证据审计；
- 检查引用、数据口径、文章结构、论文原图比例和移动端排版。

## 环境要求

- Node.js 18 或更高版本；
- npm；
- Python 3.10 或更高版本；
- Codex 桌面版或其他支持本地 Skills 的 Codex 环境。

运行时 Python 脚本仅使用标准库，不需要额外执行 `pip install`。

## 两层安装

npm 安装分为两步：

1. 将 npm 包安装到系统，使 `hf-weekly-skill` 命令可用；
2. 用该命令把 Skill 安装到 Codex 的 Skills 目录。

这样做不会通过 `postinstall` 偷偷修改用户主目录。

## 从当前目录安装

进入本项目目录：

```bash
cd writing-hf-weekly-digest
npm install -g .
hf-weekly-skill install
```

默认安装位置：

```text
~/.codex/skills/writing-hf-weekly-digest
```

安装后重启 Codex，或重新打开一个会话，让 Skill 被重新发现。

## 从 npm 压缩包安装

先生成 `.tgz`：

```bash
cd writing-hf-weekly-digest
npm pack
```

然后安装生成的包：

```bash
sudo npm install -g ./writing-hf-weekly-digest-1.0.0.tgz
sudo hf-weekly-skill install
```

## 从 npm Registry 安装

包发布到 npm Registry 后可以使用：

```bash
npm install -g writing-hf-weekly-digest
hf-weekly-skill install
```

当前仓库提供的是可发布 npm 包结构；是否发布到公共 Registry 由维护者决定。

## CLI 命令

### 查看安装位置

```bash
hf-weekly-skill path
```

### 安装

```bash
hf-weekly-skill install
```

如果目标已存在，命令会拒绝覆盖。确认需要替换时：

```bash
hf-weekly-skill install --force
```

### 更新

先更新 npm 包，再更新 Codex 中的 Skill：

```bash
npm install -g .
hf-weekly-skill update
```

`update` 使用临时目录和备份进行原子替换；失败时会恢复旧版本。

### 卸载

先删除 Codex Skill：

```bash
hf-weekly-skill uninstall
```

再按需删除 npm 包：

```bash
npm uninstall -g writing-hf-weekly-digest
```

## 自定义 Codex 目录

如果设置了 `CODEX_HOME`：

```bash
export CODEX_HOME="$HOME/my-codex"
hf-weekly-skill install
```

安装位置将变为：

```text
$CODEX_HOME/skills/writing-hf-weekly-digest
```

也可以显式指定 Skills 根目录：

```bash
hf-weekly-skill install --target /absolute/path/to/skills
```

注意：`--target` 接收的是 `skills` 目录，不是最终 Skill 目录。最终目录名固定为
`writing-hf-weekly-digest`。

## 使用方式

安装后，可以在 Codex 中提出类似请求：

```text
使用 writing-hf-weekly-digest，总结 2026-W26 的 Hugging Face Papers，
生成一篇图文并茂的中文微信公众号文章。
```

Skill 会根据任务读取：

- `SKILL.md`：主工作流；
- `references/`：编辑模式、证据规则和论文原图工作流；
- `scripts/`：数据获取、图片收集、HTML 渲染和审计工具；
- `agents/openai.yaml`：Codex UI 元数据。

## 开发与测试

运行 Node 安装器测试：

```bash
npm run test:node
```

运行现有 Python 测试：

```bash
npm run test:python
```

运行全部测试：

```bash
npm test
```

检查 npm 发布内容：

```bash
npm run pack:check
```

验证 Skill 结构时，可使用 Codex `skill-creator` 自带的
`quick_validate.py`：

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
```

## npm 包内容

发布包只包含运行所需内容：

```text
SKILL.md
README.md
agents/
bin/
references/
scripts/
package.json
```

测试、Python 缓存、文章样例和本地生成物不会进入 npm 发布包。

## 常见问题

### npm 报错 `EACCES` 或 `cache folder contains root-owned files`

这是本机 npm 缓存的所有权问题，不是本包损坏。无需修改原缓存即可临时安装：

```bash
cache_dir="$(mktemp -d)"
NPM_CONFIG_CACHE="$cache_dir" npm install -g ./writing-hf-weekly-digest-1.0.0.tgz
rm -rf "$cache_dir"
```

如果希望永久修复 npm 给出的缓存权限问题，可先确认当前用户和组：

```bash
id -u
id -g
```

然后按 npm 错误信息修复 `~/.npm` 所有权。例如 macOS 当前用户为
`501:20` 时：

```bash
sudo chown -R 501:20 "$HOME/.npm"
```

不要把整个 `/opt/homebrew` 或系统目录递归改为当前用户；此问题只涉及 npm
缓存目录。

### `hf-weekly-skill: command not found`

确认 npm 全局可执行目录位于 `PATH`：

```bash
npm prefix -g
npm bin -g
```

部分新版 npm 不再提供 `npm bin -g`，可检查：

```bash
npm prefix -g
```

并将该前缀下的 `bin` 目录加入 `PATH`。

### 提示 Skill 已存在

安全更新请使用：

```bash
hf-weekly-skill update
```

明确需要重新安装时：

```bash
hf-weekly-skill install --force
```

### Codex 中没有出现 Skill

检查实际路径：

```bash
hf-weekly-skill path
```

确认该目录包含 `SKILL.md`，然后重启 Codex 或新建会话。

### 如何保留本地修改

`update` 和 `install --force` 会完整替换目标 Skill。若修改过已安装文件，请先备份，
或者直接在本 npm 包源码中修改、测试，再重新安装。
