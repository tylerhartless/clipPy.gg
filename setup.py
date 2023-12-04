from cx_Freeze import setup, Executable


base = "Win32GUI" if sys.platform == "win32" else None


setup(
    name="clipPy.gg",
    version="1.0",
    description="Composite gaming clips vertically",
    executables=[Executable("main.py")],
)
