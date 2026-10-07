# Contributing

Keep contributions small, testable, and operationally clear.

## Development

```sh
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Pull requests

- Explain the user or operational problem.
- Include regression tests for behavior changes.
- Preserve backwards compatibility unless discussed first.
- Use synthetic data in tests and examples.
- Do not commit credentials, private data, or datasets without clear redistribution rights.
- Do not describe the heuristic baseline as a validated safety or prediction model.
