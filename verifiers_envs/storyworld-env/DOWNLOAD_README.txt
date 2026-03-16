SWEEPWEAVE RL ENVIRONMENT - DOWNLOAD PACKAGE
=============================================

You have THREE options for getting this code:

OPTION 1: Download Archive (Recommended)
-----------------------------------------
File: /mnt/user-data/sweepweave-env-complete.tar.gz (72KB)

Extract with:
    tar -xzf sweepweave-env-complete.tar.gz
    cd outputs/

Then follow QUICKSTART.md


OPTION 2: Single All-in-One File
---------------------------------
File: ALL_IN_ONE.py (39KB)

This contains the entire environment in one Python file.
Good for quick testing or copying into your own project.

Usage:
    python ALL_IN_ONE.py --estimate
    python ALL_IN_ONE.py --generate 100


OPTION 3: Copy Individual Files
--------------------------------
All files are in /mnt/user-data/outputs/

Core files to copy:
- sweepweave/__init__.py       (environment)
- test_sweepweave_env.py        (tests)
- corpus_amplification.py       (scaling)
- pyproject.toml                (package metadata)
- deploy.sh                     (automation)

Documentation:
- INDEX.md
- QUICKSTART.md
- README.md
- INTEGRATION_GUIDE.md
- ARCHITECTURE.md
- PROJECT_SUMMARY.md


QUICK START AFTER DOWNLOAD
---------------------------
1. Extract archive or copy files
2. Install: ./deploy.sh setup
3. Test: ./deploy.sh test
4. Evaluate: ./deploy.sh eval-baseline
5. See QUICKSTART.md for next steps


WHAT YOU GET
------------
✅ Production-ready verifiers environment
✅ 382 trillion configuration space
✅ 15.4B token generation capability
✅ Complete documentation
✅ Test suite
✅ Deployment automation
✅ QFT-MCP integration hooks


FILE SIZES
----------
sweepweave-env-complete.tar.gz    72KB (all files)
ALL_IN_ONE.py                     39KB (environment only)
Individual files                  ~117KB total


DEPENDENCIES
------------
- Python 3.10+
- verifiers>=0.1.7
- datasets>=2.14.0
- pytest (for testing)


SUPPORT
-------
See documentation in order:
1. INDEX.md              (overview)
2. QUICKSTART.md         (getting started)
3. INTEGRATION_GUIDE.md  (deployment)
4. ARCHITECTURE.md       (technical details)


LICENSE
-------
Apache 2.0
