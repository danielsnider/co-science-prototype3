Testing The Script
To test the script, you can make a new virtualenv and then install your package:

$ virtualenv venv
$ . venv/bin/activate
$ pip install --editable .
Afterwards, your command should be available:

$ yourscript
Hello World!

http://click.pocoo.org/5/setuptools/#setuptools-integration
