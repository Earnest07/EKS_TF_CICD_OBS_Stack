from pathlib import Path
import re


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DIRECTORY_FILE = BASE_DIR / "directory.txt"


# Files that do not have a traditional extension.
KNOWN_FILES_WITHOUT_EXTENSION = {
    "Dockerfile",
    "Jenkinsfile",
    "Makefile",
}


# =========================================================
# PARSE A SINGLE TREE LINE
# =========================================================

def parse_tree_line(line: str):
    """
    Parse one line from directory.txt.

    Examples:

        app/

        ├── main.py

        └── tests/

        │   ├── test_main.py

    Returns:

        (depth, name, is_directory)

    """

    line = line.rstrip()

    # -----------------------------------------------------
    # Ignore completely empty lines
    # -----------------------------------------------------

    if not line.strip():
        return None

    # -----------------------------------------------------
    # Ignore comment lines
    # -----------------------------------------------------

    if line.strip().startswith("#"):
        return None

    # -----------------------------------------------------
    # Ignore tree-only separator lines
    #
    # Example:
    #
    # │
    #
    # These are only visual formatting.
    # -----------------------------------------------------

    if line.strip() in {"│", "│   ", "├──", "└──"}:
        return None

    # -----------------------------------------------------
    # Detect whether this line has a tree branch.
    #
    # Examples:
    #
    # ├── main.py
    # └── tests/
    #
    # │   ├── test_main.py
    # -----------------------------------------------------

    branch_match = re.match(
        r"^(.*?)(?:├── |└── )(.*)$",
        line
    )

    if branch_match:

        prefix = branch_match.group(1)
        name = branch_match.group(2).strip()

        # -------------------------------------------------
        # Every ├── / └── represents one child level.
        #
        # Additional "│   " or "    " prefixes represent
        # further nesting.
        # -------------------------------------------------

        prefix_depth = len(prefix) // 4

        depth = prefix_depth + 1

    else:

        # -------------------------------------------------
        # No branch marker means this is a root-level item.
        #
        # Example:
        #
        # app/
        # docker/
        # terraform/
        # -------------------------------------------------

        name = line.strip()
        depth = 0

    # -----------------------------------------------------
    # Safety: remove remaining tree characters.
    # -----------------------------------------------------

    name = name.replace("│", "").strip()

    if not name:
        return None

    # -----------------------------------------------------
    # Explicit directory marker.
    #
    # Example:
    #
    # app/
    # tests/
    # dev/
    # -----------------------------------------------------

    is_directory = name.endswith("/")

    name = name.rstrip("/")

    if not name:
        return None

    # -----------------------------------------------------
    # Known files without extensions.
    # -----------------------------------------------------

    if name in KNOWN_FILES_WITHOUT_EXTENSION:
        is_directory = False

    # -----------------------------------------------------
    # Hidden files.
    #
    # .gitignore
    # .dockerignore
    # etc.
    # -----------------------------------------------------

    elif name.startswith("."):
        is_directory = False

    # -----------------------------------------------------
    # Files with extensions.
    #
    # main.py
    # deployment.yaml
    # README.md
    # -----------------------------------------------------

    elif Path(name).suffix:
        is_directory = False

    # -----------------------------------------------------
    # Anything else without an extension is treated as
    # a directory.
    # -----------------------------------------------------

    else:
        is_directory = True

    return depth, name, is_directory


# =========================================================
# READ directory.txt
# =========================================================

def parse_directory_file():

    entries = []

    lines = DIRECTORY_FILE.read_text(
        encoding="utf-8"
    ).splitlines()

    for line in lines:

        parsed = parse_tree_line(line)

        if parsed is not None:
            entries.append(parsed)

    return entries


# =========================================================
# CREATE STRUCTURE
# =========================================================

def create_structure():

    # -----------------------------------------------------
    # Check directory.txt
    # -----------------------------------------------------

    if not DIRECTORY_FILE.exists():

        print("ERROR: directory.txt was not found.")
        print()
        print(f"Expected location:")
        print(DIRECTORY_FILE)

        return

    print("=" * 70)
    print("EKS CI/CD PROJECT STRUCTURE CREATOR")
    print("=" * 70)

    print(f"Base directory : {BASE_DIR}")
    print(f"Structure file : {DIRECTORY_FILE}")

    print()

    entries = parse_directory_file()

    # -----------------------------------------------------
    # Directory stack.
    #
    # Example:
    #
    # depth 0 -> app
    # depth 1 -> tests
    # depth 2 -> something
    #
    # -----------------------------------------------------

    directory_stack = {}

    # -----------------------------------------------------
    # Statistics
    # -----------------------------------------------------

    created_directories = 0
    skipped_directories = 0

    created_files = 0
    skipped_files = 0

    errors = 0

    # =====================================================
    # PROCESS EVERY ENTRY
    # =====================================================

    for depth, name, is_directory in entries:

        # -------------------------------------------------
        # ROOT LEVEL
        # -------------------------------------------------

        if depth == 0:

            parent = BASE_DIR

        # -------------------------------------------------
        # CHILD LEVEL
        # -------------------------------------------------

        else:

            parent_depth = depth - 1

            if parent_depth not in directory_stack:

                print(
                    f"[ERROR] Parent directory not found "
                    f"for: {name}"
                )

                errors += 1
                continue

            parent = directory_stack[parent_depth]

        # -------------------------------------------------
        # Full target path
        # -------------------------------------------------

        target = parent / name

        # =================================================
        # DIRECTORY
        # =================================================

        if is_directory:

            if target.exists():

                if target.is_dir():

                    print(
                        f"[SKIP]   Directory : {target}"
                    )

                    skipped_directories += 1

                else:

                    print(
                        f"[ERROR]  File exists where "
                        f"directory is required: {target}"
                    )

                    errors += 1

                    continue

            else:

                target.mkdir(
                    parents=True,
                    exist_ok=True
                )

                print(
                    f"[CREATE] Directory : {target}"
                )

                created_directories += 1

            # -------------------------------------------------
            # Save directory for children.
            # -------------------------------------------------

            directory_stack[depth] = target

        # =================================================
        # FILE
        # =================================================

        else:

            # -------------------------------------------------
            # Make sure parent exists.
            # -------------------------------------------------

            parent.mkdir(
                parents=True,
                exist_ok=True
            )

            if target.exists():

                if target.is_file():

                    print(
                        f"[SKIP]   File      : {target}"
                    )

                    skipped_files += 1

                else:

                    print(
                        f"[ERROR]  Directory exists where "
                        f"file is required: {target}"
                    )

                    errors += 1

            else:

                # -------------------------------------------------
                # Create EMPTY file.
                #
                # IMPORTANT:
                # No existing file is ever opened for writing.
                # -------------------------------------------------

                target.touch()

                print(
                    f"[CREATE] File      : {target}"
                )

                created_files += 1

    # =====================================================
    # SUMMARY
    # =====================================================

    print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Directories created : {created_directories}"
    )

    print(
        f"Directories skipped : {skipped_directories}"
    )

    print(
        f"Files created       : {created_files}"
    )

    print(
        f"Files skipped       : {skipped_files}"
    )

    print(
        f"Errors              : {errors}"
    )

    print()

    if errors == 0:

        print(
            "Structure processing completed successfully."
        )

    else:

        print(
            "Structure processing completed with errors."
        )

    print(
        "Existing files were NOT overwritten."
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    create_structure()
