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
- Pillow (for icon generation)

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

4. Generate application icons:
```bash
python generate_icon.py
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
- `Pillow`: For image processing and icon generation

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

### Prerequisites for Building

Before building the application, ensure you have:
1. Python 3.7 or higher installed
2. Virtual environment activated
3. All dependencies installed via `pip install -r requirements.txt`
4. Generated application icons using `python generate_icon.py`

### Building on macOS

1. Clean any previous builds:
```bash
rm -rf build dist app.spec
```

2. Generate the macOS application bundle (.app):
```bash
pyinstaller --onefile --windowed --icon=icons/app.ico --add-data="icons/app.ico:." app.py
```

3. The build process will create:
   - `dist/app` - Command line executable
   - `dist/app.app` - macOS application bundle (use this)

4. Running the application:
   - Double-click `app.app` in Finder
   - Or run from terminal: `open dist/app.app`

5. Optional: Create a DMG for distribution:
   - Rename `app.app` to "Invoice Manager.app"
   - Create a new folder called "Invoice Manager"
   - Copy the .app file into this folder
   - Use Disk Utility to create a DMG

### Building on Windows

1. Clean any previous builds:
```cmd
rmdir /s /q build dist
del app.spec
```

2. Generate the Windows executable (.exe):
```cmd
pyinstaller --onefile --noconsole --icon=icons/app.ico --add-data="icons/app.ico;." app.py
```

3. The build process will create:
   - `dist/app.exe` - Windows executable

4. Running the application:
   - Double-click `app.exe` in File Explorer
   - Or run from command prompt: `dist\app.exe`

5. Optional: Create an installer:
   - Use NSIS or Inno Setup to create an installer
   - Include any necessary dependencies
   - Add Start Menu shortcuts

### Build Options Explained

Common options for both platforms:
- `--onefile`: Creates a single executable file
- `--icon=icons/app.ico`: Sets the application icon

Platform-specific options:
- macOS:
  - `--windowed`: Prevents terminal window from appearing
  - `--add-data="icons/app.ico:."`: Includes resources (uses colon separator)

- Windows:
  - `--noconsole`: Prevents command prompt from appearing
  - `--add-data="icons/app.ico;."`: Includes resources (uses semicolon separator)

### Troubleshooting Build Issues

#### macOS Build Issues

1. **Architecture Issues**
   - M1/M2 Macs: Use native ARM64 Python
   - Intel Macs: Use x86_64 Python
   - Check architecture: `python -c "import platform; print(platform.machine())"`

2. **Icon Issues**
   - Ensure icon file exists
   - Try regenerating icons: `python generate_icon.py`
   - Check file permissions

3. **Missing Libraries**
   - Verify all dependencies are installed
   - Check virtual environment is activated
   - Try reinstalling packages: `pip install -r requirements.txt`

#### Windows Build Issues

1. **DLL Issues**
   - Install Visual C++ Redistributable
   - Ensure PyQt5 is properly installed
   - Try reinstalling packages

2. **Icon Not Showing**
   - Verify icon path is correct
   - Regenerate icon: `python generate_icon.py`
   - Clear icon cache: `ie4uinit.exe -show`

3. **Antivirus Blocking**
   - Add exception for PyInstaller
   - Temporarily disable antivirus during build
   - Use trusted Python distribution

### Distribution Guidelines

#### macOS Distribution

1. Test the app bundle:
   ```bash
   # Verify app bundle contents
   ls -la dist/app.app/Contents/MacOS/
   # Check code signing
   codesign -vv dist/app.app
   ```

2. Optional: Code sign the application:
   ```bash
   codesign --sign "Developer ID" dist/app.app
   ```

#### Windows Distribution

1. Test the executable:
   ```cmd
   # Verify executable
   dist\app.exe
   # Check version info
   sigcheck dist\app.exe
   ```

2. Optional: Sign the executable:
   ```cmd
   signtool sign /f certificate.pfx /p password app.exe
   ```

## Directory Structure

```
bill-generator/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── generate_icon.py   # Icon generation script
├── icons/             # Application icons
│   ├── app.ico       # Windows icon
│   └── app_icon.png  # PNG version of icon
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

5. **Icon Generation Issues**
   - Ensure Pillow is installed: `pip install Pillow`
   - Check if the icons directory exists and has write permissions
   - Try running the icon generation script again

### Getting Help

If you encounter any issues:
1. Check the error message in the application
2. Review the console output for detailed errors
3. Ensure all dependencies are installed correctly
4. Check if you have the latest version of the application



