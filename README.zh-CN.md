<p align="right">
  <a href="README.md">English</a> · <strong>简体中文</strong>
</p>

# Open Source Launch

**把本地或私有项目转化为可移植、经过隐私审查、容易被发现并完成验证的 GitHub 开源版本。**

[![测试](https://github.com/JNHFlow21/open-source-launch/actions/workflows/test.yml/badge.svg)](https://github.com/JNHFlow21/open-source-launch/actions/workflows/test.yml)
[![版本](https://img.shields.io/github/v/release/JNHFlow21/open-source-launch?display_name=tag)](https://github.com/JNHFlow21/open-source-launch/releases)
[![许可证：MIT](https://img.shields.io/badge/License-MIT-18a558.svg)](LICENSE)

![Open Source Launch 概念流程：本地项目依次经过隐私审查、可移植打包和发布门禁，最终成为公开代码仓库](docs/assets/social-preview.png)

> **Beta：**工作流和配套脚本已经过测试，但每次发布仍需针对具体仓库完成隐私、许可证、平台和分发审查。

## 为什么需要它

把仓库设为 Public，不等于交付了一个真正的开源产品。精美的 README
无法修复只能从维护者源码目录运行的安装包，也无法删除 Git 历史里的凭据、
补上缺失的授权，或证明陌生用户能够完成第一次成功。

Open Source Launch 为 Codex 提供一套可重复执行的发布契约：

```text
私有/本地项目
  -> 隐私与知识产权门禁
  -> 可移植发布物
  -> 隔离环境首次成功
  -> README 与发现元数据
  -> 经授权公开发布
  -> 可衡量的采用闭环
```

它包含确定性的公开面审计工具，以及可选的白底 Repository Pulse 图表；
不会静默发布、合并、改变可见性，也不会把凭据写进文档。

## 快速开始

### 1. 安装到当前项目

```bash
DISABLE_TELEMETRY=1 npx skills add JNHFlow21/open-source-launch \
  --skill open-source-launch \
  --agent codex \
  --yes
```

这条已验证路径会把 Skill 安装到当前项目的
`.agents/skills/open-source-launch/`。`DISABLE_TELEMETRY=1` 用于关闭安装器 CLI
的匿名遥测；Open Source Launch 本身不包含遥测。

也可以让 Codex 内置 Skill Installer 完成安装：

```text
Use $skill-installer to install open-source-launch from
https://github.com/JNHFlow21/open-source-launch/tree/main/skills/open-source-launch
```

通过任一路径安装后，都要开启一个新的 Codex 轮次，让系统重新发现 Skill。

### 2. 执行只读发布审计

```text
使用 open-source-launch 审计这个仓库，不要修改文件或远程状态。
```

预期结果：得到一份区分阻断项、警告、已验证事实和缺失证据的门禁报告。
静态扫描只是第一道门禁，不能单独证明项目已经适合发布。

### 3. 准备或正式开源

```text
为这个项目准备开源 GitHub 发布，但不要真正公开。
```

当全部门禁通过，而且你准备授权远程发布时：

```text
把这个项目正式开源，完成经过验证的 PR、仓库元数据、Release 和线上回读流程。
```

## 四种工作模式

| 模式 | 作用 | 远程写入 |
| --- | --- | --- |
| `audit` | 只读检查发布准备度和缺口 | 永不 |
| `prepare` | 在隔离分支或 Worktree 中修复可移植性、公开面、文档和发布文件 | 不改变可见性，不发布版本 |
| `launch` | 完成验证后的正式公开流程 | 仅在明确授权后 |
| `refresh` | 更新现有公开项目的文档、发现页面、截图、指标或发布材料 | 仅限授权范围 |

## 它标准化了什么

### 先安全，后展示

- 当前文件和 Git 历史中的凭据检查；
- 个人数据、媒体、日志、数据库、内网地址和本机路径检查；
- 第三方代码、资源来源和许可证门禁；
- 发现阻断项就停止，报告不会回显匹配到的密钥值。

### 面向陌生用户的可移植性

- 明确运行时、依赖、配置、权限和网络要求；
- 不暗中依赖维护者的 `$HOME`、Shell Alias、Keychain 或源码目录；
- 记录全新克隆、隔离 HOME、正式安装、首次结果和更新/恢复证据。

### 公共仓库产品化

- 与实际维护模式相符的 LICENSE、SECURITY、CONTRIBUTING、CI、Release 和支持入口；
- 有证据支撑的主 README，以及内容同步、表达自然、可以独立阅读的多语言版本；
- 聚焦的仓库描述、Topics、Social Preview、自然搜索语言和稳定引用路径；
- 放在 README 靠后位置的可选隐私安全仓库活动图。

### 发布后的采用闭环

- 根据渠道分别起草发布内容，但不会自动发帖；
- 从有效发现、首次成功到留存的完整衡量；
- 明确区分 `observed`、`inferred` 和 `missing_evidence`。

## 发布门禁模型

```mermaid
flowchart LR
    A["公开意图"] --> B["隐私与知识产权"]
    B --> C["可移植性"]
    C --> D["分发"]
    D --> E["首次成功"]
    E --> F["信任与文档"]
    F --> G["发现"]
    G --> H["经授权发布"]
    H --> I["采用闭环"]
```

每一项重要公开声明都必须属于：

- **verified**：已在目标公开发布物或线上仓库中观察到；
- **planned**：明确标记为计划；
- **missing evidence**：证据不足，暂时不能宣传。

## 确定性审计工具

审计器只依赖 Python 标准库，并只报告位置，不回显匹配到的密钥：

```bash
python3 skills/open-source-launch/scripts/audit_open_source.py . --json
```

本地安装 Gitleaks 后，可以执行正式发布门禁：

```bash
python3 skills/open-source-launch/scripts/audit_open_source.py . \
  --run-gitleaks --strict
```

它检查仓库基础文件、疑似凭据、被跟踪的环境文件、私有或本机引用、
高风险数据文件、外部软链接、运行时声明和 Git 状态。启发式结果可能需要
人工复核；静态扫描通过不等于历史、媒体/IP、隔离安装、CI 和线上设置已验证。

## Repository Pulse

使用具有仓库 Owner 权限且已经认证的 `gh` 安装白底手绘风图表：

```bash
python3 skills/open-source-launch/scripts/install_repository_pulse.py \
  /path/to/repository \
  --repository OWNER/REPOSITORY \
  --collect-traffic
```

安装器只写入三个组件文件并打印 README 片段，不会编辑 README、提交、推送、
创建分支或改变可见性。GitHub Traffic 仅保存带日期的 14 天滚动聚合快照；
公开 README URL 永远不携带长期 Token。

## 要求与边界

- 为 Codex Skills 设计并验证；其他兼容 `SKILL.md` 的 Agent 可能可用，但不属于已验证支持声明。
- 只有项目级标准安装路径需要带 `npx` 的 Node.js；Skill 运行时不依赖 Node.js。
- 只有确定性辅助脚本需要 Python 3.10+。
- 需要 `git` 才能提供被跟踪文件和工作区状态证据。
- `gh`、仓库 Owner 权限和 Gitleaks 都是可选项，仅用于对应的 GitHub 或历史密钥门禁。
- 不包含遥测。
- 远程写入始终遵守所请求的模式和授权边界。
- 当前工作流面向 GitHub；其他代码托管平台需要适配。

## 仓库结构

```text
skills/open-source-launch/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── audit_open_source.py
│   └── install_repository_pulse.py
├── references/
└── assets/repository-pulse/
```

Skill 本身完整保存在 `skills/open-source-launch/`；面向人的仓库文档和社区文件
放在 Skill 包之外。

## 开发与验证

```bash
python3 -m unittest discover -s skills/open-source-launch/tests -v
python3 -m compileall -q skills/open-source-launch
```

发布前还要执行 `--run-gitleaks --strict`，从临时 Codex Home 验证真实安装路径，
并回读线上仓库和 Release 状态。

## 参考契约

- [准备度与发布门禁](skills/open-source-launch/references/readiness-contract.md)
- [陌生用户优先的可移植性](skills/open-source-launch/references/portability-contract.md)
- [README 转化契约](skills/open-source-launch/references/readme-contract.md)
- [GitHub 发现、SEO 与 GEO](skills/open-source-launch/references/discovery-contract.md)
- [Repository Pulse](skills/open-source-launch/references/repository-pulse.md)
- [开源采用闭环](skills/open-source-launch/references/adoption-contract.md)

## 支持与问题反馈

使用问题或可复现的非敏感故障，请通过
[GitHub Issues](https://github.com/JNHFlow21/open-source-launch/issues/new/choose)
提交，并使用合成示例。任何可能暴露凭据、私有仓库、个人数据或漏洞利用方式的
内容，都必须使用私密漏洞报告。

## 仓库活动

[![JNHFlow21/open-source-launch Repository Pulse](https://raw.githubusercontent.com/JNHFlow21/open-source-launch/metrics/repository-metrics.svg)](https://github.com/JNHFlow21/open-source-launch)

## 贡献、安全与许可证

- 提交 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。
- 请通过 [GitHub 私密漏洞报告](https://github.com/JNHFlow21/open-source-launch/security/advisories/new) 报告漏洞，不要公开创建 Issue。
- 项目采用 [MIT License](LICENSE) 开源。
