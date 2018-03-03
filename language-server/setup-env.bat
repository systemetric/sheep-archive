@echo off
mkdir env
cd env
echo Setting up virtual environment...
virtualenv .
echo Installing python-language-server...
Scripts\pip install python-language-server
echo Setup complete!