# GitHub Repo Analyzer

A simple Python script to find the most starred GitHub repository for a given search term, download its README, and save it as a clean text file.

## Features

*   Search for any term on GitHub.
*   Find the repository with the most stars.
*   Download the README file.
*   Clean the Markdown content into plain text.
*   Save the output to a file with a descriptive name.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/git-analysis.git
    cd git-analysis
    ```

2.  Install the required Python libraries:
    ```bash
    pip install requests beautifulsoup4 markdown
    ```

## Usage

Run the script from your terminal with a search term as an argument:

```bash
python start.py "<your_search_term>"
```

### Example

```bash
python start.py "wechat clone"
```

The script will create a file in the `output/` directory named `STARS_<star_count>_<owner>_<repo_name>.txt`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
