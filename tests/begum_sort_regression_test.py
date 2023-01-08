import argparse
from pathlib import Path

from compare_sort_outputs import compare_results, text_file


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
        description="Regression test to compare results of Begum sort in different environments."
    )

    parser.add_argument(
        "--results_directory",
        type=Path,
        required=True,
        help="Directory containing the results of multiple runs of Begum sort."
    )

    return parser.parse_args()


def execute_regression_test() -> None:

    cli_args = parse_cli_arguments()

    results_directory: Path = cli_args.results_directory

    summary_files = [
        text_file(summary_file)
        for summary_file in results_directory.rglob(pattern="*.summaryCounts")
    ]
    tag_info_files = [
        text_file(tag_info_file)
        for tag_info_file in results_directory.rglob(pattern="*.tagInfo")
    ]

    error_message = "Number of summary files differs from number of tag info files."
    assert len(summary_files) == len(tag_info_files), error_message

    compare_results(summary_files=summary_files, tag_info_files=tag_info_files)


if __name__ == "__main__":
    execute_regression_test()
