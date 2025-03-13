# Invoice Management System

A cross-platform desktop application for generating and managing invoices with GST support. Built with Python and PyQt5.

## Features

- Generate professional invoices with GST calculations
- Manage client information with GST numbers
- Product management with SKU codes and HSN codes
- Export invoice data to Excel
- Print invoices directly
- Edit and delete existing invoices
- Signature support for invoices
- Advance payment tracking
- Modern and intuitive user interface

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

1. Clone the repository (or download the source code):
```bash
git clone https://github.com/yourusername/bill-generator.git
cd bill-generator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Managing Dependencies

### Adding New Dependencies

If you need to add new packages to the project:

1. Install the new package:
```bash
pip install package_name
```

2. Update requirements.txt:
```bash
pip freeze > requirements.txt
```

### Updating Dependencies

To update all packages to their latest versions:

1. Update pip first:
```bash
python -m pip install --upgrade pip
```

2. Update all packages:
```bash
pip install --upgrade -r requirements.txt
```

### Current Dependencies

The project uses the following main packages:
- `PyQt5`: For the graphical user interface
- `reportlab`: For PDF generation
- `fpdf`: For additional PDF functionality
- `num2words`: For converting numbers to words
- `pandas`: For data manipulation and Excel export
- `openpyxl`: For Excel file handling
- `pyinstaller`: For creating executable files

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
python app.py
```

## Application Structure

### Main Tabs

1. **Generate Bill**
   - Create new invoices
   - Add client details with GST numbers
   - Add products with quantities
   - Upload signature
   - Generate and print PDF invoices

2. **Display Bills**
   - View all generated invoices
   - Edit invoice details
   - Delete invoices
   - Export invoice data to Excel
   - View detailed invoice information

3. **Manage Clients**
   - Add new clients with GST numbers
   - Edit client information
   - Delete clients
   - View all client details

4. **Manage Products**
   - Add new products with SKU and HSN codes
   - Edit product information
   - Delete products
   - Set product prices

### Database Structure

The application uses SQLite database with the following tables:
- `companies`: Stores client information
- `products`: Stores product catalog
- `invoices`: Stores invoice headers
- `invoice_items`: Stores invoice line items

## Building the Application

### Using PyInstaller

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the application:
```bash
pyinstaller --onefile --windowed --icon=app.ico app.py
```

The executable will be created in the `dist` directory.

### Build Options

- `--onefile`: Create a single executable file
- `--windowed`: Run without console window
- `--icon=app.ico`: Add application icon
- `--add-data`: Include additional resources

## Directory Structure

```
bill-generator/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── signatures/        # Directory for invoice signatures
├── dist/             # Build output directory
└── build/            # Build temporary files
```

## Usage Guide

### Creating a New Invoice

1. Go to the "Generate Bill" tab
2. Enter client GST numbers (auto-fills company details)
3. Add products using the "Add Product" button
4. Set quantities and prices
5. Upload signature (optional)
6. Click "Generate Bill" to create PDF
7. Click "Print Bill" to print directly

### Managing Clients

1. Go to the "Manage Clients" tab
2. Click "Add Client" to create new client
3. Enter company name, GST number, and address
4. Use "Edit Client" or "Delete Client" for existing clients

### Managing Products

1. Go to the "Manage Products" tab
2. Click "Add Product" to create new product
3. Enter SKU code, product name, HSN code, and price
4. Use "Edit Product" or "Delete Product" for existing products

### Exporting Data

1. Go to the "Display Bills" tab
2. Click "Export to Excel"
3. Choose save location
4. Excel file will contain all invoice data

## Troubleshooting

### Common Issues

1. **Database Errors**
   - Ensure write permissions in the application directory
   - Check if database file is not locked by another process

2. **PDF Generation Issues**
   - Verify all required fields are filled
   - Check if signature file exists and is valid
   - Ensure sufficient disk space

3. **Excel Export Issues**
   - Install openpyxl package: `pip install openpyxl`
   - Check if target file is not open in Excel

4. **Dependency Issues**
   - Make sure all packages are installed: `pip install -r requirements.txt`
   - Try updating packages: `pip install --upgrade -r requirements.txt`
   - Check Python version compatibility

### Getting Help

If you encounter any issues:
1. Check the error message in the application
2. Review the console output for detailed errors
3. Ensure all dependencies are installed correctly
4. Check if you have the latest version of the application

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

