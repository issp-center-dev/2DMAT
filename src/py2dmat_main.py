if __name__ == "__main__":
    import sys
    import os.path

    script_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(script_dir)
    import py2dmat

    py2dmat.main_script()
