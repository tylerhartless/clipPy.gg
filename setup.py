from cx_Freeze import setup, Executable

setup(
    name="clipPy.gg",
    version="1.0",
    description="Composite gaming clips vertically",
    executables=[Executable("main.py")],
)
