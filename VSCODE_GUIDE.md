# Using VSCode

You can run and debug the project directly inside VSCode.

## 1. Setup
Ensure you have the **Python** extension installed in VSCode.

## 2. Running with Terminal (Easiest)
1.  Open VSCode in the project folder (`code .`).
2.  Open the integrated terminal (Shortcut: `` Ctrl + ` ``).
3.  Run the helper script:
    ```bash
    ./run_dev.sh
    ```

## 3. Running with Debugger (Advanced)
If you want to set breakpoints and debug line-by-line:

1.  Click the **Run and Debug** icon on the left sidebar (Play button with a bug).
2.  Select **"Debug API (FastAPI)"** from the dropdown at the top.
3.  Click the green **Play Button (F5)**.
4.  The API will start, and you can pause execution by clicking on line numbers to add red dots (breakpoints).

> [!NOTE]
> Make sure your Python interpreter is set to the `venv` environment (Bottom right corner in VSCode).
