import os


def generate_directory_tree(root, ignore_list):
    """
    Recursively generate a directory tree structure,
    skipping any files or directories whose names are in the ignore_list.
    """
    tree_lines = []

    def _walk(current_path, prefix=""):
        try:
            entries = sorted(os.listdir(current_path))
        except PermissionError:
            return  # Skip directories without permission

        # Filter out entries present in the ignore list.
        entries = [entry for entry in entries if entry not in ignore_list]

        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                tree_lines.append(prefix + entry + "/")
                _walk(full_path, prefix + "    ")
            else:
                tree_lines.append(prefix + entry)

    _walk(root)
    return "\n".join(tree_lines)


def process_files(root, ignore_list):
    """
    Process all files in the directory (ignoring those in the ignore list)
    and return a formatted string with each file's relative path and its content.
    """
    output = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out ignored directories from traversal.
        dirnames[:] = [d for d in dirnames if d not in ignore_list]
        for filename in filenames:
            if filename in ignore_list:
                continue
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {e}"
            # Get the relative path from the root for cleaner output.
            rel_path = os.path.relpath(file_path, root)
            # Append formatted file information.
            output.append(f"{rel_path}\n```\n{content}\n```")
    return "\n\n".join(output)


def main():
    # Hardcoded directory path and ignore list.
    root_dir = "/Users/qatoolist/Projects/python/pymock"
    ignore_list = [
        ".devcontainer",
        ".github",
        ".vscode",
        "tests",
        ".git",
        ".mypy_cache",
        ".ruff_cache",
        ".dockerignore",
        ".gitignore",
        ".pre-commit-config.yaml",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "LICENSE.txt",
        "README.md",
        "showinfo.py",
        "output.txt",
        "output2.txt",
        "bkp.rules_engine.py",
        "__pycache__",
        ".coverage",
        ".DS_Store",
        ".pytest_cache",
    ]  # list of file/folder names to ignore

    # Generate the directory structure.
    directory_structure = generate_directory_tree(root_dir, ignore_list)
    # Process files to capture each file's relative path and contents.
    files_info = process_files(root_dir, ignore_list)

    # Write the output to a file.
    output_file = "output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Directory Structure -\n")
        f.write(directory_structure)
        f.write("\n\n")
        f.write(files_info)

    print(f"Output written to {output_file}")  # noqa: T201


if __name__ == "__main__":
    main()
