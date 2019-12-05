# SMRO-accountcrawler

### Requirements  
- A python install on your PC, see https://www.python.org/downloads/windows/  
- [Download the script itself](https://github.com/Keridos/SMRO-accountcrawler/archive/master.zip)  

### Usage
To use this, download, extract to an empty folder then put your account data into (new file) _accounts.json_,
 see _example_accounts.json_ for an example. 

_accounts.json_ parameters:  
- name - login username  
- password - login password  
- count_zeny - should zeny of this account be counted towards total? false -> no, true -> yes
- char_slot - slot to pull character from, 0 -> scan entire account and report back all chars  

To start it up just open _main.py_ in the same folder.

It should open up a terminal that spit outs the zeny of all the characters it scans and afterwards open up a tab in your
browser with an overview of all the chars where you can see the details on each char
(just click the link with the chars name)

### Additional notes
Currently it is not possible to grab the zeny from the bank. This causes the total value to be lacking the zeny in each
accounts bank.
