## 2024-05-23 - Installation UX Feedback
**Learning:** For CLI installation scripts, verbose per-file logging ("Copied X") creates noise that hides errors. Users prefer a "Searching..." indicator followed by a summary ("Copied N files") and clearly formatted Next Steps.
**Action:** When creating installation scripts, use summary statistics instead of individual file logs and group "Next Steps" into a visually distinct block.

## 2025-05-15 - Interactive CLI Recovery
**Learning:** When a CLI tool fails to auto-detect a resource (like a directory), exiting immediately frustrates users. It's better to interactively ask for the path, allowing them to recover without re-running the command with flags.
**Action:** Replace `sys.exit()` on missing resources with `Prompt.ask()` to give users a chance to provide input.
