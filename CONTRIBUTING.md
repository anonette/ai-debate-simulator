# Contributing to Kitchen Debate

Thank you for considering contributing to Kitchen Debate! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/KitchenDebate.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment:
   ```
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your API keys
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use type hints where appropriate
- Write clear docstrings for functions and classes
- Use descriptive variable names

### Git Workflow

1. Keep your branch up to date with main: `git pull origin main`
2. Make your changes in logical, focused commits
3. Push your changes to your fork: `git push origin feature/your-feature-name`
4. Create a pull request against the main repository

### Testing

- Add tests for new features
- Make sure all tests pass before submitting a pull request
- Run tests with: `pytest`

## Feature Requests and Bug Reports

- Use the GitHub Issues tab to report bugs or request features
- Provide detailed steps to reproduce any bugs
- For feature requests, explain the use case and benefits

## Adding New Debate Agents

To add a new AI personality:

1. Extend the config.yaml file with your new agent
2. Define the agent's personality and model details
3. Update any UI elements in debate_app.py to include the new agent
4. Add appropriate avatar and styling

## Code Review Process

All submissions will be reviewed by the project maintainers. We'll look for:

- Code quality and adherence to style guidelines
- Proper test coverage
- Documentation
- Overall fit with project goals

## License

By contributing to Kitchen Debate, you agree that your contributions will be licensed under the project's MIT License. 