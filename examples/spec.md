# Orchestrator Task Dashboard - UI Spec

## Goal

Build a single-page React app for a fictional "AI Orchestrator" that shows
a list of tasks and details for the selected task. This is a front-end-only
demo with hard-coded data.

The file to generate is `src/App.tsx` in a Vite + React + TypeScript + Tailwind CSS project.

## Tech Constraints

- React + TypeScript (TSX).
- Tailwind CSS utility classes for styling.
- No external state management libraries (no Redux, Zustand, etc.).
- No routing, all content on a single page.
- Use functional components and hooks only.

## Layout

The page layout should be a full-height, two-column layout:

1. **Header**
   - Stretches across the top.
   - Contains the app title: "AI Orchestrator – Task Dashboard".
   - Right side can show a small pill with text: "Demo Environment".

2. **Main Body**
   - Below the header, split into two columns:
     - **Left sidebar (30% width on desktop, full-width stacked on small screens):**
       - Title: "Tasks".
       - List of tasks (see Data Model).
       - Each task item shows:
         - Task name
         - Status badge (e.g., "idle", "running", "completed", "error")
       - The selected task is visually highlighted.
     - **Right content panel (remaining width):**
       - Shows details for the currently selected task:
         - Task name
         - Status badge
         - Description
         - List of steps with their statuses
         - A read-only JSON preview of the task payload/config.

## Data Model (Hard-Coded)

Use a hard-coded array of tasks in the component file:

Each task object should look like:

- `id: string`
- `name: string`
- `status: "idle" | "running" | "completed" | "error"`
- `description: string`
- `steps: { id: string; name: string; status: "pending" | "running" | "done" | "failed" }[]`
- `payload: Record<string, unknown>` (can be a simple object literal with a few keys)

Include at least 3 example tasks, for example:

1. "Generate App.tsx from spec"
2. "Sync project structure"
3. "Analyze dependency graph"

Make the payloads small but illustrative, e.g. `{ projectPath: "...", targetFile: "src/App.tsx" }`.

## Interaction Behavior

- When the app loads:
  - The first task in the list is selected by default.
- When the user clicks on a task in the sidebar:
  - That task becomes the selected task.
  - The right panel updates with that task's details.

This can all be local React state (`useState`). No network calls.

## Styling Guidelines

- Overall look: clean, modern, slightly "dev tool" vibe.
- Use a neutral background (e.g., `bg-slate-900` for the page, `bg-slate-800` for sidebar, etc.).
- Use Tailwind typography utilities (`text-slate-100`, `text-slate-400`, etc.).
- Status badges should be colored differently:
  - `idle`: subtle gray
  - `running`: blue or amber
  - `completed`: green
  - `error`: red
- Make the layout responsive:
  - On small screens, stack the sidebar above the content panel.
  - On medium+ screens, use a grid or flex layout with two columns.

## Component Structure

It is acceptable to implement everything in a single `App` component for this demo,
but the code should still be well-organized:

- Define the `Task` and `TaskStep` TypeScript types.
- Define the hard-coded tasks array at the top of the file.
- Use `useState` to store the `selectedTaskId`.
- Derive the `selectedTask` from the tasks array and `selectedTaskId`.
- If no task is selected for some reason, show a simple "No task selected" message.

## What to Output

Generate a complete `src/App.tsx` file that:

- Imports React.
- Exports a default `App` component.
- Uses Tailwind classes for styling.
- Contains all the logic and JSX as described above.
- Does not rely on any files other than what Vite + React + TS + Tailwind provides by default.
