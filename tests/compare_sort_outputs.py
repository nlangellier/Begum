"""
Script to compare the outputs from multiple runs of ``Begum sort``. The order of lines for each
section in each file is not enforced. Thus, two files are considered the same if the lines are the
same but in a different order. The help for this script can be obtained by running
"python compare_sort_outputs.py --help". The intended use case for this test is to compare results
of ``Begum sort`` when run in different virtual environments, but with the same inputs. E.g. running
``Begum sort`` with the same inputs but different versions of ``biopython`` or different versions of
Python.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    File = list[str]
    ParsedSummaryFile = dict[str, list[str]]
else:
    File = "list[str]"
    ParsedSummaryFile = "dict[str, list[str]]"


def parse_summary_file(raw_summary_file: File) -> ParsedSummaryFile:
    """
    Parses a raw summary text file from ``Begum sort``.

    Parameters
    ----------
    raw_summary_file
        A list of strings where each string is one line of the summary file.

    Returns
    -------
    ParsedSummaryFile
        A dictionary where the keys are the section names of the summary file and the values are
        lists of strings where each string is one line of the associated section in the summary
        file.

    Raises
    ------
    AssertionError
        If each section is not separated by a line of hyphens.
    """

    section_separator = re.compile(pattern="^-+$")

    section_name = "header"
    parsed_summary_file: ParsedSummaryFile = {section_name: []}

    new_section = False

    for line in raw_summary_file:

        if new_section:
            error_message = "New section does not contain section separator."
            assert section_separator.match(line) is not None, error_message
            new_section = False
            continue

        if len(line.split("\t")) == 1:
            section_name = line
            parsed_summary_file[section_name] = []
            new_section = True
            continue

        parsed_summary_file[section_name].append(line)

    return parsed_summary_file


def compare_summary_files(summary_files: tuple[ParsedSummaryFile, ...]) -> None:
    """
    Compares multiple (at least 2) summary files to ensure the contents are the same for each
    section of the summary file.

    Parameters
    ----------
    summary_files
        A list of summary files where each file has the format returned by ``parse_summary_file``.

    Raises
    ------
    AssertionError
        If any 2 summary files differ in their contents.
    """

    print("\nComparing summary files...")

    error_message = "Summary files differ."

    reference_summary_file = summary_files[0]

    for summary_file in summary_files[1:]:
        assert reference_summary_file.keys() == summary_file.keys(), error_message

    for section_name in reference_summary_file.keys():
        reference_section_counter = Counter(reference_summary_file[section_name])
        for summary_file in summary_files[1:]:
            assert reference_section_counter == Counter(summary_file[section_name]), error_message

    print("Summary files contain the same data.")


def compare_tag_info_files(tag_info_files: list[File]) -> None:
    """
    Compares multiple (at least 2) tag info files to ensure the contents are the same.

    Parameters
    ----------
    tag_info_files
        A list of tag info files where each file is a list of strings representing the lines of the
        associated file.

    Raises
    ------
    AssertionError
        If any 2 tag info files differ in their contents.
    """

    print("\nComparing tag info files...")

    error_message = "Summary files differ."

    reference_tag_info_file = tag_info_files[0]

    for tag_info_file in tag_info_files[1:]:
        assert reference_tag_info_file[0] == tag_info_file[0], error_message
        assert Counter(reference_tag_info_file) == Counter(tag_info_file), error_message

    print("Tag info files contain the same data.")


def text_file(file_path: str | Path) -> File:
    """
    Returns the contents of a text file as a list of strings with each string representing each line
    of the file. This function is intended to be used as the value of the ``type`` argument in
    ``argparse.ArgumentParser.add_argument``.

    Parameters
    ----------
    file_path
        The local file path of the file to open.

    Returns
    -------
    File
        The file contents as a list of strings representing the lines of the file.

    Raises
    ------
    TypeError
        All exceptions are caught and re-thrown as a ``TypeError`` so that
        ``argparse.ArgumentParser.parse_args`` will return a useful error message
        (see <https://docs.python.org/3/library/argparse.html#type>).
    """

    try:
        return Path(file_path).read_text().splitlines()
    except Exception as exception:
        raise TypeError(f"Unable to read {file_path}") from exception


def parse_cli_arguments() -> argparse.Namespace:
    """
    Parses the command line arguments.

    Returns
    -------
    Namespace
        The values of the parsed command line arguments.

    Raises
    ------
    AssertionError
        If the number of summary files is not equal to the number of tag info files or if the number
        of files for either is less than 2.
    """

    parser = argparse.ArgumentParser(
        description="Script to compare the results of multiple runs of Begun sort"
    )

    parser.add_argument(
        "--summary-files",
        type=text_file,
        nargs="+",
        required=True,
        metavar="FILE",
        help="List of file paths to summary counts files to compare."
    )
    parser.add_argument(
        "--tag-info-files",
        type=text_file,
        nargs="+",
        required=True,
        metavar="FILE",
        help="List of file paths to tag info files to compare."
    )

    parsed_args = parser.parse_args()

    error_message = "Number of summary files must equal number of tag info files and must be " \
                    "greater than or equal to 2"
    assert len(parsed_args.summary_files) == len(parsed_args.tag_info_files) >= 2, error_message

    return parsed_args


def compare_results(summary_files: list[File], tag_info_files: list[File]) -> None:
    """
    Executes the comparison of outputs from multiple (at least 2) runs of ``Begum sort``.
    """

    parsed_summary_files = tuple(
        parse_summary_file(raw_summary_file) for raw_summary_file in summary_files
    )
    compare_summary_files(parsed_summary_files)

    compare_tag_info_files(tag_info_files)


if __name__ == "__main__":

    cli_args = parse_cli_arguments()
    compare_results(summary_files=cli_args.summary_files, tag_info_files=cli_args.tag_info_files)
    print("\nAll comparisons resulted in identical data.\n")
