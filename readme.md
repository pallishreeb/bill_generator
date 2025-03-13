pip install pyinstaller

brew install create-dmg


pyinstaller --name=BillGenerator --windowed --onefile main.py

Run this command to create the .exe file:
pyinstaller BillGenerator.spec 


Create a .dmg File on macOS (Create an App Bundle (macOS Only))
pyinstaller --windowed --onefile --name=BillGenerator --icon=your_icon.icns main.py


Use create-dmg to Build .dmg File
create-dmg dist/BillGenerator.app


source venv/bin/activate
.\venv\Scripts\activate


pip freeze > requirements.txt
pip install -r requirements.txt

cat requirements.txt  # For macOS/Linux
type requirements.txt  # For Windows
