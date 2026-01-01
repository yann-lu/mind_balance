# MindBalance Database Schema

## 1. Overview
This schema is designed for PostgreSQL (Supabase). It supports:
- **Multi-level Task Management:** Projects -> Tasks.
- **Energy Budgeting:** Tracking target allocation history.
- **Dual-Mode Time Tracking:** Real-time timer & Manual entry.
- **Analytics:** Efficient aggregation for variance analysis and heatmaps.

## 2. ER Diagram Description (Textual)

- **Users** `1` -- `*` **Projects**
- **Projects** `1` -- `*` **Tasks**
- **Projects** `1` -- `*` **ProjectBudgets** (History of target %)
- **Tasks** `1` -- `*` **TimeLogs**
- **Users** `1` -- `*` **TimeLogs** (Direct relation for faster user-level queries)

## 3. Table Definitions

### `users`
Standard authentication table (managed by Supabase Auth usually, but here is the public reference).

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Linked to `auth.users` |
| `email` | VARCHAR | UNIQUE | |
| `full_name` | VARCHAR | | |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |

### `projects`
Core categorization unit.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `user_id` | UUID | FK -> users.id | |
| `name` | VARCHAR(100) | NOT NULL | e.g., "Python Learning" |
| `color_hex` | VARCHAR(7) | | UI color coding |
| `status` | VARCHAR(20) | CHECK (status IN ('active', 'archived')) | Default 'active' |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | |

### `project_budgets`
Tracks the history of "Energy Budget" settings. This allows us to calculate "Planned vs Actual" correctly for past dates.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BIGINT | PK, GENERATED ALWAYS AS IDENTITY | |
| `project_id` | UUID | FK -> projects.id | |
| `target_percentage` | INTEGER | CHECK (0-100) | The desired energy allocation |
| `valid_from` | TIMESTAMPTZ | NOT NULL | When this budget became active |
| `valid_to` | TIMESTAMPTZ | NULLABLE | NULL means "currently active" |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |

*Note: When a user updates their budget, update the current row's `valid_to` to NOW(), and insert a new row.*

### `tasks`
Actionable items.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `project_id` | UUID | FK -> projects.id | |
| `title` | VARCHAR(255) | NOT NULL | |
| `status` | VARCHAR(20) | CHECK (status IN ('todo', 'in_progress', 'done')) | |
| `priority` | VARCHAR(10) | | low, medium, high |
| `due_date` | TIMESTAMPTZ | | |
| `next_review_at` | TIMESTAMPTZ | | For Ebbinghaus Spaced Repetition |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |
| `completed_at` | TIMESTAMPTZ | | |

### `time_logs`
The core of the tracking system. Handles both real-time sessions and manual entries.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `task_id` | UUID | FK -> tasks.id | |
| `user_id` | UUID | FK -> users.id | Denormalized for fast analytics |
| `project_id` | UUID | FK -> projects.id | Denormalized for fast grouping |
| `log_type` | VARCHAR(10) | CHECK (log_type IN ('TIMER', 'MANUAL')) | |
| `start_at` | TIMESTAMPTZ | NULLABLE | Required if log_type = 'TIMER' |
| `end_at` | TIMESTAMPTZ | NULLABLE | Required if log_type = 'TIMER' |
| `duration_seconds` | INTEGER | NOT NULL | Calculated for TIMER, User-input for MANUAL |
| `log_date` | DATE | NOT NULL | The "Accounting Date". Helps timezone handling. |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | |

## 4. Key Design Decisions

### Handling "Real-time" vs "Manual" (`time_logs`)
- **Real-time (TIMER):**
  1. User clicks Start: API creates a row with `log_type='TIMER'`, `start_at=NOW()`, `log_date=CURRENT_DATE`. `end_at` is NULL.
  2. User clicks Pause/Stop: API updates the row, setting `end_at=NOW()` and calculating `duration_seconds = end_at - start_at`.
- **Manual (MANUAL):**
  1. User enters "2 hours on 2023-10-27".
  2. API creates a row with `log_type='MANUAL'`, `log_date='2023-10-27'`, `duration_seconds=7200`. `start_at` and `end_at` can be NULL (or set to a default generic time like 12:00 PM if needed for sorting, but strictly they are not "real" timestamps).

### Handling "Budget History" (`project_budgets`)
- To calculate Variance for last week:
  1. Query `time_logs` grouped by `project_id` for last week to get **Actuals**.
  2. Query `project_budgets` where `valid_from <= last_week` and `(valid_to > last_week OR valid_to IS NULL)` to get the **Targets** that were active during that time.
  3. Compare.

### Indexes for Performance
```sql
CREATE INDEX idx_logs_user_date ON time_logs(user_id, log_date);
CREATE INDEX idx_logs_project ON time_logs(project_id);
CREATE INDEX idx_budgets_active ON project_budgets(project_id) WHERE valid_to IS NULL;
```

## 5. Execution
The full executable SQL script is available in `mindbalance/docs/setup.sql`. 
You can run it in your PostgreSQL console or via a tool like pgAdmin / Supabase SQL Editor.
