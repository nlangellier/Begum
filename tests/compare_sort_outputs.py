import argparse
import re
from collections import Counter
from pathlib import Path

File = list[str]
ParsedSummaryFile = dict[str, File]


def parse_summary_file(raw_summary_file: File) -> ParsedSummaryFile:

    section_separator = re.compile(pattern="^-+$")

    section_name = "header"
    parsed_summary_file: ParsedSummaryFile = {section_name: []}

    new_section = False

    for line in raw_summary_file:

        if new_section:
            assert section_separator.match(line) is not None, "New section does not contain section separator."
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

    print("\nComparing summary files...")

    error_message = "Summary files differ."

    for summary_file in summary_files[1:]:
        assert set(summary_files[0].keys()) == set(summary_file.keys()), error_message

    for section_name in summary_files[0].keys():
        for summary_file in summary_files[1:]:
            assert Counter(summary_files[0][section_name]) == Counter(summary_file[section_name]), error_message

    print("Summary files contain the same data.")


def compare_tag_info_files(tag_info_files: list[File]) -> None:

    print("\nComparing tag info files...")

    error_message = "Summary files differ."

    for tag_info_file in tag_info_files[1:]:
        assert tag_info_files[0][0] == tag_info_file[0], error_message
        assert Counter(tag_info_files[0]) == Counter(tag_info_file), error_message

    print("Tag info files contain the same data.")


def file(file_path: str) -> File:

    try:
        return Path(file_path).read_text().splitlines()
    except Exception as exception:
        raise TypeError(f"Unable to read {file_path}") from exception


def parse_cli_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser()

    parser.add_argument("--summary_files", type=file, nargs="+", required=True)
    parser.add_argument("--tag_info_files", type=file, nargs="+", required=True)

    cli_args = parser.parse_args()

    error_message = "Number of summary files must equal number of tag info files and must be greater than or equal to 2"
    assert len(cli_args.summary_files) == len(cli_args.tag_info_files) >= 2, error_message

    return cli_args


def main() -> None:

    cli_args = parse_cli_arguments()

    summary_files = tuple(
        parse_summary_file(raw_summary_file) for raw_summary_file in cli_args.summary_files
    )
    compare_summary_files(summary_files)

    compare_tag_info_files(cli_args.tag_info_files)

    print("\nAll comparisons resulted in identical data.\n")


if __name__ == "__main__":
    main()
