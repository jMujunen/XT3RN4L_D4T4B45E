This directory contains various useful scripts related
to deployment issues


# Resolving TK issues

To find out what are your TK and TCL paths,
run a python script outside of the venv (source):
```python
    import tkinter
    root = tkinter.Tk()
    print(root.tk.exprstring('$tcl_library'))
    print(root.tk.exprstring('$tk_library'))
```
Open venv config file `bin/activate` and replace
the following exports with the correct path from above
```python
    TCL_LIBRARY="/tcl/path/from/step/1"
    TK_LIBRARY="/tk/path/from/step/1"
    TKPATH="/tk/path/from/step/1"
    export TCL_LIBRARY TK_LIBRARY TKPATH
```
Deactivate (if it was activated) and source again your venv:
```python
    deactivate
    source bin/activate
```
The "Tcl missing"-error should be gone.
