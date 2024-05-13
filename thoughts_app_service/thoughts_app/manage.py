# manage.py

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thoughts_app.settings")
    try:
        from django.core.management import execute_from_command_line
        import coverage
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Start coverage before importing any test modules
    cov = coverage.Coverage()
    cov.start()

    execute_from_command_line(sys.argv)

    # Stop and save the coverage data
    cov.stop()
    cov.save()

    # Report the coverage data
    cov.report()
    cov.html_report(directory="coverage_html_report")
    cov.xml_report(outfile="coverage.xml")


if __name__ == "__main__":
    main()
