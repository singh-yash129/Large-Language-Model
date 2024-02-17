# DataWorks Agent

DataWorks Agent is an automation agent that uses an LLM to parse task descriptions and execute the required steps. It supports various tasks categorized into Phase A and Phase B.

## Features

- Install packages and run scripts
- Format files using Prettier
- Count specific days in date lists
- Sort and process JSON data
- Extract information from text files
- Compress and resize images
- Transcribe audio files
- Convert Markdown to HTML
- Filter and process CSV data

## Requirements

- Docker
- Python 3.9+
- Node.js and npm
- SQLite3
- Pandoc
- ImageMagick

## Usage

### Run a Task

To run a task, send a POST request to the `/run` endpoint with the task description as a query parameter.

Example:
```sh
curl -X POST "http://localhost:8000/run?task=Format+/data/format.md+with+prettier+3.4.2"
```

### Read a File

To read a file, send a GET request to the `/read` endpoint with the file path as a query parameter.

Example:
```sh
curl "http://localhost:8000/read?path=/data/format.md"
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

