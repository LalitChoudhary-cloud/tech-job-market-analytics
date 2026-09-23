"""
Execute and populate cell outputs in all Jupyter Notebooks
==========================================================
Runs code cells using IPython's InteractiveShell, captures:
- stdout and stderr streams
- HTML / Plain text representations (Pandas DataFrames, etc.)
- Matplotlib / Seaborn figures as embedded base64 PNG images
- Execution counts and cell statuses
"""

import io
import os
import sys
import base64
import traceback
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless figure generation
import matplotlib.pyplot as plt


def run_and_populate_notebook(nb_path):
    print(f"--> Executing: {nb_path}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbf.read(f, as_version=4)

    # Initialize a fresh IPython shell instance for each notebook
    InteractiveShell.clear_instance()
    shell = InteractiveShell.instance()

    # Change working directory to notebooks directory during execution if needed
    orig_cwd = os.getcwd()

    exec_count = 1
    for cell_idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue

        source = cell.source
        outputs = []
        captured_figs = []

        # Hook into plt.show to intercept figures
        def custom_show(*args, **kwargs):
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                captured_figs.append(img_base64)
            plt.close("all")

        orig_show = plt.show
        plt.show = custom_show

        try:
            with capture_output() as captured:
                result = shell.run_cell(source, store_history=True)

            # Check if any lingering figures exist
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                captured_figs.append(img_base64)
            plt.close("all")

            # 1. Capture stdout
            if captured.stdout:
                outputs.append(nbf.v4.new_output(
                    output_type="stream",
                    name="stdout",
                    text=captured.stdout
                ))

            # 2. Capture stderr
            if captured.stderr:
                outputs.append(nbf.v4.new_output(
                    output_type="stream",
                    name="stderr",
                    text=captured.stderr
                ))

            # 3. Capture captured figures as display_data
            for img_b64 in captured_figs:
                outputs.append(nbf.v4.new_output(
                    output_type="display_data",
                    data={
                        "image/png": img_b64,
                        "text/plain": "<Figure size ...>"
                    }
                ))

            # 4. Capture return value (execute_result) if expression returned value
            if result.result is not None:
                res = result.result
                data = {}
                if hasattr(res, "_repr_html_") and callable(res._repr_html_):
                    try:
                        html_repr = res._repr_html_()
                        if html_repr:
                            data["text/html"] = html_repr
                    except Exception:
                        pass
                data["text/plain"] = repr(res)

                outputs.append(nbf.v4.new_output(
                    output_type="execute_result",
                    data=data,
                    execution_count=exec_count
                ))

            # 5. Capture error if exception occurred
            if result.error_in_exec:
                err = result.error_in_exec
                ename = type(err).__name__
                evalue = str(err)
                tb = traceback.format_exception(type(err), err, err.__traceback__)
                outputs.append(nbf.v4.new_output(
                    output_type="error",
                    ename=ename,
                    evalue=evalue,
                    traceback=tb
                ))

        finally:
            plt.show = orig_show

        cell.outputs = outputs
        cell.execution_count = exec_count
        exec_count += 1

    with open(nb_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f" Successfully executed and saved outputs to: {nb_path}")


def main():
    notebooks = [
        "notebooks/01_data_cleaning.ipynb",
        "notebooks/02_eda.ipynb",
        "notebooks/03_nlp_skill_analysis.ipynb",
        "notebooks/04_ml_models.ipynb"
    ]

    for nb in notebooks:
        if os.path.exists(nb):
            run_and_populate_notebook(nb)
        else:
            print(f"File not found: {nb}")


if __name__ == "__main__":
    main()
