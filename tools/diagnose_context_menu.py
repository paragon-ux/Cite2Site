"""Diagnose why Cite2Site context menu isn't appearing."""
import subprocess, sys

print("=== Checking registry entries ===")
try:
    r = subprocess.run(
        ['reg', 'query', r'HKEY_CLASSES_ROOT\*\shell\Cite2Site', '/s'],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print(r.stdout)
    else:
        print("  NOT FOUND — context menu was not registered.")
        print("  Run: c2s install-context-menu")
        sys.exit(1)
except Exception as e:
    print(f"  Error: {e}")

print("\n=== Checking c2s is on PATH ===")
r = subprocess.run(['where', 'c2s'], capture_output=True, text=True)
print(f"  {r.stdout.strip() or 'NOT FOUND'}")

print("\n=== Right-click menu location ===")
print("  The menu appears in Windows FILE EXPLORER only.")
print("  It does NOT appear in:")
print("    - Notepad++ (uses its own context menu)")
print("    - VS Code (uses its own context menu)")
print("    - Browser editors (use browser context menu)")
print("    - Any application with a custom right-click menu")
print()
print("  To test: open File Explorer (Win+E), navigate to a file,")
print("  right-click the file, look for 'Cite2Site' in the menu.")
print()
print("  If still missing, restart Explorer:")
print("    taskkill /f /im explorer.exe && start explorer.exe")
