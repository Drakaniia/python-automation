# TUI UX Design

## Revised Prompt

Act as a UX designer specializing in keyboard-first terminal user interfaces built
with the Rust `ratatui` framework.

The app is `magic`, a terminal port killer for local development. It scans a
configured set of TCP and UDP ports, lists listener processes in an interactive
TUI, lets the user mark one or more processes, shows an explicit confirmation
view, and then terminates the selected PIDs.

Provide a UX design document covering:

- Layout strategy: how to divide the screen for scanning, browsing,
  confirmation, results, and errors.
- Visual hierarchy: how to use ratatui styles, borders, color, bold, and muted
  text to make active state and danger actions obvious.
- Keyboard navigation: a logical keyboard-first scheme using arrows and
  Vim-style keys, including focus changes between the process table and
  confirmation view.
- Feedback mechanisms: how to show loading, errors, confirmations, and kill
  results without disrupting the layout.

## Layout Strategy

Use one stable vertical layout so the screen does not jump between states:

- Header, 3 rows: app name, scanned ports, protocol filter, listener count, and
  marked count.
- Status, 3 rows: current mode badge plus the latest message.
- Main region, flexible height: process table plus selected-process inspector
  on wide terminals, a single process table on narrow terminals, empty state, or
  confirmation review.
- Footer, 5 rows: mode-specific keyboard help and the most recent kill result
  lines.

The browsing main region uses a single-focus model even when the screen splits
into two columns. The process table owns focus; the inspector is read-only and
tracks the selected row. During confirmation, the main region becomes a danger
review with a short `Kill Review` banner and a target table, so the user can
review exact PIDs, ports, protocols, and command identity before acting.

## Visual Hierarchy

Use the header for orientation, the status row for state, and the main table for
action. The footer is secondary help text and should not compete visually with
the active region.

- App title: cyan and bold.
- Header metadata: muted labels with bright values.
- Marked count and marked rows: light magenta.
- Active main table border: cyan and bold.
- Inspector border: quiet gray.
- Busy states: light yellow and bold with a spinner.
- Success states: green.
- Destructive confirmation and errors: red and bold.
- Muted metadata: dark gray.
- Selected row: blue background, white foreground, bold text.
- Marked but unfocused rows: light magenta text.

Rows use a combined cursor and checkbox marker:

```text
> [x]  focused and marked
> [ ]  focused but not marked
  [x]  marked but not focused
  [ ]  not focused and not marked
```

## Keyboard Navigation

Browsing mode supports both standard arrow keys and Vim-style movement:

```text
Up/Down or k/j    move selection
g/Home            jump to first process
G/End             jump to last process
Space             mark or unmark focused process
a                 mark all or clear all
Enter             open confirmation view
r                 rescan
q or Esc          quit
```

Confirmation mode narrows available actions to the decision being made:

```text
y                 graceful termination, then force fallback if needed
f                 force termination immediately
n or Esc          cancel confirmation and return to browsing
q                 quit
```

Focus does not cycle through multiple widgets because the current app has one
primary task at a time. The focus transition is mode-based: browsing focuses the
process table, confirmation focuses the kill target review.

## Feedback Mechanisms

Loading and destructive work stay in the status row:

- Scanning shows a spinner and the scanned port list.
- Killing shows a spinner and preserves the main layout.
- Marking or unmarking updates the status line with the PID and selected count.
- Toggle-all reports whether all processes were marked or selections were
  cleared.
- Confirmation changes the main region to an explicit kill review banner and
  target table.
- Kill results remain visible in the footer until another scan or action.
- Errors use the status row and danger styling, while preserving the same
  header, main region, and footer.

This keeps feedback close to the action without opening transient popups for
normal states.
