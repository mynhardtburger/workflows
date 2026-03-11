## Instruction Test Results

**Tested:** [date]
**Environment:** [OS, key tool versions]
**Instruction blocks found:** N
**Tested:** N
**Skipped:** N (reasons)

### [path/to/document.md] — "[Section Name]"

#### Test: [brief command description]

- **Severity:** Error
- **Dimension:** Accuracy
- **Location:** quickstart.md, "Step 3: Run the server", line 45
- **Command:** `myapp serve --port 8080`
- **Expected output:** (from docs)

  ```
  Server running on http://localhost:8080
  ```

- **Actual output:**

  ```
  Error: unknown flag --port, did you mean --listen-port?
  ```

- **Assessment:** The `--port` flag was renamed to `--listen-port`. Docs need
  updating.
