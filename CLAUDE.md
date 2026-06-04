# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 构建命令 Build Commands

### 构建 exe
```bash
python -m PyInstaller --onefile --name "番茄钟" main.py
```
输出: `dist/番茄钟.exe`

### 开发模式运行
```bash
python main.py
```

## 架构 Architecture

单文件应用，核心逻辑在 `main.py`:

- **PomodoroTimer 类** — 主应用类，管理所有 UI 和计时逻辑
- **计时循环** — `countdown()` 通过 `self.root.after(1000, self.countdown)` 实现每秒更新
- **模式切换** — 工作/休息状态存储在 `self.is_work`，通过 `transition_to_next()` 切换
- **进度条** — tkinter Canvas 绘制弧形 `create_arc(start=270, extent=-progress*360)`
- **音效** — `winsound.Beep()` 播放提示音

## PyInstaller 资源路径

素材目录在 `素材/`，运行时通过 `resource_path()` 解析:

```python
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, "素材", filename)
    return os.path.join(os.path.dirname(__file__), "素材", filename)
```

## Git

远程仓库: `git@github.com:c4wbbnb8cz-oss/pomodoro-timer.git`

本地已是干净状态，HEAD 位于 `29eeb93` (添加test666.png)。