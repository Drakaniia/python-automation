# Run all dev_mode tests
pytest tests/test_dev_mode/ -v

# Or run specific test files
pytest tests/test_dev_mode/test_menu_routing.py -v
pytest tests/test_dev_mode/test_create_frontend_noninteractive.py -v
pytest tests/test_dev_mode/test_other_modules.py -v

# Run with coverage
pytest tests/test_dev_mode/ -v --cov=automation/dev_mode --cov-report=html

# Run with more detailed output
pytest tests/test_dev_mode/ -vv -s