# SMRO-accountcrawler

To use this put your account data into _accounts.json_, see _example_accounts.json_ for an example  

Parameter:  
name - login username  
password - login password  
count_zeny - should zeny of this account be counted towards total?  
char_slot - slot to pull character from, 0 -> scan entire account and report back all chars  

Then just call _main.py_

It should open up a terminal that spit outs the zeny of all the characters it scans and afterwards open up a tab in your
browser with an overview of all the chars where you can see the details on each char
(just click the link with the chars name)

Requirements
A python install on your PC, see https://www.python.org/downloads/windows/
