import pytest
from pathlib import Path
from atlas.tools import list_files, read_file, write_file, run_shell_command


def test_list_files_basic(tmp_path):
    """Test listing files in a directory."""
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")

    files = list_files(tmp_path)

    assert len(files) == 2
    assert "file1.txt" in [Path(f).name for f in files]
    assert "file2.txt" in [Path(f).name for f in files]


def test_list_files_nonexistent_directory():
    """Test listing files from a nonexistent directory."""
    with pytest.raises(FileNotFoundError):
        list_files("/nonexistent/directory")


def test_read_file(tmp_path):
    """Test reading file contents."""
    file_path = tmp_path / "test.txt"
    content = "Hello, World!"
    file_path.write_text(content)

    result = read_file(file_path)

    assert result == content


def test_read_file_nonexistent():
    """Test reading a nonexistent file."""
    with pytest.raises(FileNotFoundError):
        read_file("/nonexistent/file.txt")


def test_write_file(tmp_path):
    """Test writing content to a file."""
    file_path = tmp_path / "subdir" / "test.txt"
    content = "Test content"

    write_file(file_path, content)

    assert file_path.exists()
    assert file_path.read_text() == content


def test_write_file_overwrite(tmp_path):
    """Test overwriting existing file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("original")

    write_file(file_path, "updated")

    assert file_path.read_text() == "updated"


def test_run_shell_command():
    """Test running a shell command."""
    result = run_shell_command("echo 'hello'")
    assert "hello" in result


def test_run_shell_command_error():
    """Test running a shell command that fails."""
    result = run_shell_command("ls /nonexistent")
    assert result != ""
