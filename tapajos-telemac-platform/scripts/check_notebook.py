import ast, asyncio, contextlib, io, json
from pathlib import Path

path = Path("notebooks/03_parametrizacao_telemac.ipynb")
nb = json.loads(path.read_text())
scope = {"__name__": "__main__"}


async def main():
    count = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        count += 1
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            code = compile(
                "".join(cell["source"]),
                str(path),
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            result = eval(code, scope)
            if asyncio.iscoroutine(result):
                await result
        cell["execution_count"] = count
        cell["outputs"] = [
            {
                "output_type": "stream",
                "name": "stdout",
                "text": capture.getvalue().splitlines(keepends=True),
            }
        ]
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=2))
    print("Executed", count, "notebook cells with real solver")


asyncio.run(main())
