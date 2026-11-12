""





import sys


def _run():
    try:
        from .app import main

        return main(sys.argv[1:]) or 0
    except SystemExit:
        raise
    except BaseException:


        import traceback

        text = traceback.format_exc()
        try:
            from sitecustomize import _fatal
        except Exception:
            sys.stderr.write(text)
        else:
            _fatal(text)
        return 1


sys.exit(_run())
