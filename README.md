# Forever Boutique AI Chatbot

A professional AI-powered chatbot solution for Forever Boutique, designed to enhance customer service, drive sales, and provide valuable business insights.

## Features

- **Multi-Platform Integration**
  - Facebook Messenger
  - Line Official Account
  - Website Chat Widget

- **Business Intelligence**
  - Customer behavior tracking
  - Sales analytics
  - Performance metrics
  - Lead generation

- **Customer Service**
  - 24/7 automated responses
  - Product information
  - Order tracking
  - Appointment scheduling

- **Sales & Marketing**
  - Product recommendations
  - Special offers
  - Lead qualification
  - Customer feedback

## Project Structure

```
Forever-Boutique/
├── main.py                 # Main entry point
├── config/                 # Configuration files
├── core/                   # Core business logic
├── integrations/           # Platform integrations
├── data/                   # Data storage
├── analytics/             # Analytics and metrics
├── templates/             # Response templates
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/forever-boutique.git
   cd forever-boutique
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your settings
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## Development

- **Code Style**: Follow PEP 8 guidelines
- **Testing**: Run tests with `pytest`
- **Type Checking**: Use `mypy` for type checking
- **Formatting**: Use `black` for code formatting

## Documentation

- [Setup Guide](docs/setup_guide.md)
- [API Documentation](docs/api.md)
- [Case Study](docs/case_study.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please contact:
- Email: support@forever-boutique.com
- Website: https://forever-boutique.com 