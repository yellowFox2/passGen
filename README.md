# passGen
simple password generator/vault. Easily generate and store passwords in encrypted file. Good for keeping passwords on a secure drive location -- encrypted thumb drives preferrably
# Requirements
1. python 2.7
2. cryptography module (https://pypi.org/project/cryptography/)
# Install
1. run 'pip install cryptography'
2. run 'python ./passGen.py'
3. type "vaultInit"
4. type "encryptVault"
5. to view, type "getVault"
6. rename and (preferrably) move .\.vault\new-vault.json file to a secure location
7. update <vaultPath> element in .\config\config.xml to reflect new name and file location
8. it is highly recommended to move new-vault.key file as well. After moving file, you can reference it at runtime using "--key=<path/to/key/keyname.key>"

# Options
* To generate a new password, type "genPass" and type password seed
* To update vault, type "updateVault" and input site alias and password -- copy and paste from password created with "genPass"
* To switch between vaults and different vault keys, use --key=<path/to/key/keyname.key> and --config=<path/to/vault/vault.json> to reference vault key location and vault location, respectively
