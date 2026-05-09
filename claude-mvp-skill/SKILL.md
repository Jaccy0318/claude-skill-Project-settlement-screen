---
name: terminal-mvp-animation
description: This skill should be considered when the user says phrases like "项目完成了", "给我来一个结算动画", "MVP时刻", "播放我的结算视频", or otherwise signals that a project or major milestone has been reached. IMPORTANT — this skill does NOT blindly trigger on keywords. It must first evaluate whether the user has genuinely completed a meaningful project or milestone before proceeding.
---

# MVP结算动画

## 核心原则：先判断，再庆祝

本 Skill 不是关键词机器人。触发词只是"候选信号"——你必须先独立判断用户的当前项目是否**真正达到了可结算的里程碑**，再决定是否进入动画流程。

---

## 第一步：决策判断（必须执行）

在输出任何内容之前，从以下维度评估：

### 判定为"应该结算"的信号（满足 1 项即可进入）
- 用户在当前对话中经历了**多轮迭代**（至少 3+ 轮有实质代码变更），现在宣告完成
- 用户明确说某个功能/模块/项目"做完了"、"上线了"、"发布了"、"可以用了"
- 用户完成了跨越多个文件的较大改动，且改动形成了闭环（从规划 → 实现 → 测试都做了）
- 对话上下文显示这是一个**持续了一段时间**的任务，而非单次问答

### 判定为"不应该结算"的信号（任一命中则跳过）
- 用户只是随口闲聊，比如"今天工作都做完了"（无具体项目上下文）
- 用户刚完成的是一个**单行修复 / 微小调整**（改个拼写、加个注释、问个问题）
- 用户只是问"这个完成了没有"或"还有多少没做"——这是进度询问，不是结算宣告
- 对话刚开始（少于 2 轮），没有积累任何实质工作

### 灰色地带处理
如果信号模糊，不要直接跳过。用一句简短的话确认，例如：
> "听起来这个阶段的开发告一段落了——要我给你来一个结算动画庆祝一下吗？🎮"
先确认，用户点头再继续。

---

## 第二步：输出喝彩文案 + 自动弹出全屏视频

通过判断后，同时做两件事：

### A. 输出结算面板

从对话历史中提取项目信息（能提取多少提取多少，提取不到的用估计值代替）：

**时间统计** — 根据对话轮次估算：
- 每轮对话约 2~5 分钟，乘以总轮次得出总耗时
- 如消息有时间戳，用首末消息时间差精确计算

**Token 统计** — 无法获取精确值时按以下规则估算：
- 每次你的回复约 500~2000 output tokens
- 每轮用户输入约 100~500 input tokens
- 汇总后取整，注明"（估算）"

```
========================================
  🎮 恭喜！项目《{项目名}》已通关！
========================================
  ⏱️  总耗时       : {估算值，如 "~45 分钟"}
  🔤 Token 消耗   : {估算值，如 "~24K"}
  📊 代码行数     : {统计值} 行
  🐛 Bug 击杀    : {统计值} 只
  📁 涉及文件     : {统计值} 个
  👥 通关角色     : 人类 × AI 联机小队
  ⭐ 评价等级     : {S/A/B}
========================================
```

评价等级逻辑：
- 改动 >5 个文件 或 对话 >10 轮 → **S**
- 3~5 个文件 或 5~10 轮 → **A**
- 其余 → **B**

### B. 自动启动全屏视频（关键）

**在输出文案的同时，用 Bash 工具在后台启动全屏视频播放**。

#### 视频文件：
视频已随 Skill 内置在 `~/.pixelplay/mvp_video.mp4`，无需用户提供任何外部路径。
分享 Skill 时，将整个 `~/.pixelplay/` 目录一起分发即可（包含 `pixelplay.py` + `mvp_video.mp4`）。

#### 命令（固定，不要改路径）：
```bash
python ~/.pixelplay/pixelplay.py ~/.pixelplay/mvp_video.mp4
```

#### 执行方式：
使用 Bash 工具的 `run_in_background: true` 参数，这样视频在后台弹出全屏窗口，不会阻塞对话。

#### 播放行为：
- OpenCV `WINDOW_FULLSCREEN` 纯全屏 — 无标题栏、无进度条、无任何 UI 铬
- `imageio-ffmpeg` 提取音频 → `pygame.mixer` 同步播放 — 音画合一
- 按 ESC / Q / Space 退出，视频播完自动关闭
- 若视频无音频轨道，静默降级为纯画面播放

#### 依赖（脚本自动检查，缺失时提示安装）：
- `opencv-python` — 视频帧读取 + 全屏渲染
- `pygame` — 音频播放
- `moviepy` / `imageio-ffmpeg` — 提供内置 ffmpeg 二进制，无需系统安装 ffmpeg

---

## 第三步：首次使用检测

如果 `~/.pixelplay/pixelplay.py` 不存在，使用 Write 工具现场生成。脚本架构：

1. OpenCV `WINDOW_FULLSCREEN` — 纯全屏无铬画面
2. `imageio-ffmpeg` 提取音频 → `pygame.mixer` 同步播放
3. 基于 `start_time + frame_idx * frame_delay` 的帧率控制，不累积漂移
4. 按 ESC / Q / Space 退出，播完自动清理临时音频文件

如果 `~/.pixelplay/mvp_video.mp4` 不存在（例如分享给别人后对方还没复制视频），提醒：
```
📦 结算视频缺失！请将 mvp_video.mp4 放入 ~/.pixelplay/ 目录。
   该文件应与 pixelplay.py 一起随 Skill 分发。
```

---

## 第四步：边界情况

| 场景 | 处理方式 |
|------|----------|
| 用户没有视频文件 | 只输出喝彩文案，提示放置视频 |
| 用户说"别放视频" | 只输出文案 |
| 大项目中间阶段完成 | 正常结算，文案加 "📦 模块《XXX》已交付！" |
| 连续两次触发 | 第二次精简版，不再弹视频 |
| opencv / pygame / imageio-ffmpeg 缺失 | 提示 `pip install opencv-python pygame moviepy` |
| 视频无音频轨道 | 静默降级，纯画面播放 |

---

## 核心约束总结

1. **先判断，再响应** — 不满足条件不触发
2. **模糊时先确认** — 不要替用户决定
3. **文案 + 视频双输出** — 文案在对话中，视频全屏弹出
4. **自动执行** — 用 `run_in_background: true` 启动视频，不等待返回
5. **按了就能播** — 如果脚本或视频缺失，现场生成或给出明确指引
