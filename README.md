# passGen
CLI password generator/vault. Easily generate and store passwords in (Fernet) encrypted file. Good for keeping passwords in a secure drive location.
# Requirements
1. Linux, Windows, or MacOS
2. Python 2.7 or above
3. Cryptography module (https://pypi.org/project/cryptography/)
4. Pillow module (https://pypi.org/project/Pillow/)
5. QRCode module (https://pypi.org/project/qrcode/)
4. [Optional] ipfshttpclient module (https://pypi.org/project/ipfshttpclient/)
# How to run
1. Run 'pip install cryptography'
2. Run 'python .\passGen.py'
3. Type "vaultInit"
4. Type "getVault" to retrieve initial vault values
5. [Recommended] rename and move .\\.vault\vault.json file to a secure location
6. [Recommended] update vaultPath element in .\config\config.xml to reflect new name and file location
7. [Recommended] rename and move vault.key (stored in .\\.hide\\) to secure location
<br/>**It is highly recommended to move vault.key file. After moving file, you can reference it at runtime using "--key=<path\to\key\keyname.key>"**
# Options
* To generate a new password, type "genPass"
* To update vault, type "updateVault" and input site alias and password -- copy and paste from password created with "genPass"
* To remove vault entry, type "deleteRecord" and input site alias
* To switch between different vaults and keys, keep multiple copies of .\config\config.xml (each referencing different vault locations), then run the script with following args: --key=<path\to\key\keyname.key> --config=<path\to\config\config.xml>
* To use different command aliases to run vault table queries, add/update \<aliases\> element attributes in config.xml *(name attribute = command name, method attribute = name of method to call, desc = alias description)*
* To create shortcut to bash script (that runs passGen.py), type "createShortcut" and input bash script location (source), argument (alias in .\config\config.xml), and location of shortcut (target) -- only on Linux (for now)
* To retrieve QR Code of vault table record or generated password, run "getRecordQR" or "genPassQR", respectively
## Using IPFS (Optional)
IPFS is a P2P file-hosting protocol that can give users access to files from a given cid (hash). <ins>Users are given the option to host their encrypted vault on IPFS and decrypting it client-side</ins> by referencing their vault's cid in .\config\config.xml (update the \<ipfsAddress\> element).
1. Download/install IPFS from https://dist.ipfs.io/#go-ipfs
2. Initialize IPFS node (Run 'ipfs init')
3. Start IPFS daemon ('ipfs daemon --enable-gc')
4. Run 'pip install ipfshttpclient'
### IPFS Options
* Type "ipfsUpload" to upload encrypted vault to IPFS
* Type "ipfsGetVault" to get vault stored on IPFS

