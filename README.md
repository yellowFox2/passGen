# passGen
simple password generator/vault
# Requirements
1. python 2.7
2. cryptography module (https://pypi.org/project/cryptography/)
# Install
1. run 'pip install cryptography'
2. run 'python ./passGen.py'
3. input site name alias (i.e. "reddit: = https://old.reddit.com)
4. input password seed
5. on first use, you will be prompted to create a password vault. if you choose to do so, you will then be prompted to generate a vault key. this key will be stored in the project's ./.hide folder. PLEASE MOVE KEY TO A SECURE LOCATION, PREFERABLY SOMEWHERE WITH ROOT-ONLY ACCESS. the script will default to the project's ./.hide folder for access, unless you run the 'updateKeyPath' at the main menu, or if you run 'python ./passGen.py --key "/path/to/key/example.key"'
