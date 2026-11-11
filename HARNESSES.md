# Harness Compatibility

This skill follows the portable Agent Skills layout:

```text
lab-report/
|-- SKILL.md
|-- references/
|-- scripts/
`-- assets/
```

The installed skill contains the shared DOCX builder, native PDF wrapper, cover assets, and report references. Generated report files stay in the consuming project.

Every harness listed below consumes the same `SKILL.md` plus its neighboring resources. Discovery roots and invocation commands differ, so the installer writes the same personalized skill to each selected harness's native user-level directory.

## Path matrix

| Harness | User-level installation | Project-level alternative | Notes |
|---|---|---|---|
| Codex / universal `.agents` | `~/.agents/skills/lab-report/` | `<repo>/.agents/skills/lab-report/` | Recommended universal path; some Codex builds also scan `~/.codex/skills/`. |
| Claude Code | `~/.claude/skills/lab-report/` | `<repo>/.claude/skills/lab-report/` | Loads directory-based `SKILL.md` skills. |
| OpenCode | `~/.config/opencode/skills/lab-report/` | `<repo>/.opencode/skills/lab-report/` | Also loads compatible `.claude/skills/` and `.agents/skills/` roots. |
| Hermes | `~/.hermes/skills/lab-report/` | Project-owned skill directories | Skills live under the Hermes home skills root. |
| Pi | `~/.pi/agent/skills/lab-report/` | `<repo>/.pi/skills/lab-report/` | Implements the Agent Skills specification. |
| Oh My Pi | `~/.omp/agent/skills/lab-report/` | `<repo>/.omp/skills/lab-report/` | Also has an `agents` provider for `.agents/skills/`. |
| DSH | `~/.dsh/skills/lab-report/` | `<repo>/.dsh/skills/lab-report/` | Also scans `.claude/skills/` and `.agents/skills/`; `$DSH_HOME` controls the home root. |
| ZCode | `~/.zcode/skills/lab-report/` | `<repo>/.zcode/skills/lab-report/` | Uses a directory containing `SKILL.md`. |
| WorkBuddy | `~/.workbuddy/skills/lab-report/` | `<repo>/.workbuddy/skills/lab-report/` | Per-user skills apply across projects. |

## Installer examples

Install for one harness:

```powershell
.\install.ps1 -Harness codex
.\install.ps1 -Harness claude-code
.\install.ps1 -Harness opencode
```

Install for multiple harnesses:

```powershell
.\install.ps1 -Harness codex,claude-code,opencode
```

Interactive selection:

```powershell
.\install.ps1
```

The interactive installer lists every supported target and accepts numbers or names. Use `-Force` to back up and replace existing installed copies.

Install to an arbitrary compatible skill directory:

```powershell
.\install.ps1 -TargetPath "D:\custom-agent\skills\lab-report"
```

## Linux and WSL installation

On Linux or inside WSL, use the Bash installer. It resolves the same user-level paths through `$HOME` and accepts the same harness keys:

```bash
bash install.sh --harness codex
bash install.sh --harness codex,claude-code,opencode
bash install.sh --harness all --dry-run
bash install.sh --harness all
```

Interactive installation uses the same numbered harness list:

```bash
bash install.sh
```

Use `--force` to back up and replace existing installations:

```bash
bash install.sh --harness codex --force
```

Install to an arbitrary compatible skill directory:

```bash
bash install.sh --target-path "$HOME/.local/share/agent-skills/lab-report"
```

WSL converts Windows drive paths through `wslpath` when a drive-letter path is passed to `--target-path` or an image option. The project itself can stay under `/mnt/<drive>/...`, while the installed skill normally belongs in the Linux `$HOME`.

After installation, the Bash report entry points are:

```bash
bash "$HOME/.agents/skills/lab-report/scripts/new-lab-report.sh" --help
bash "$HOME/.agents/skills/lab-report/scripts/compile-report.sh" --help
```

## Source references

- [Codex / Agent Skills](https://learn.chatgpt.com/docs/build-skills?kbid=111697)
- [Claude Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [OpenCode Skills](https://opencode.ai/docs/skills/)
- [Hermes Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)
- [Pi Skills](https://pi.dev/docs/latest/skills)
- [Oh My Pi configuration](https://github.com/can1357/oh-my-pi/blob/main/docs/config-usage.md)
- [DSH / dsh-cc Skills](https://dsh-cc.github.io/guide/skills)
- [ZCode Skills](https://www.zcode.network/en/docs/skill/)
- [WorkBuddy Skills](https://www.workbuddy.ai/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills)
