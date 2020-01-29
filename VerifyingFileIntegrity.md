# Verifying File Integrity

There are times when a file transfer may fail. For example, during the "Verify File Integrity" stage of a Globus transfer, even though the transfer itself was successful. If this happens for a large file, e.g. over 1 TB, reinitiating the transfer itself is not ideal. Instead, the user may generate a checksum on the source and destination machines and compare the two. 

### HPC Checksum

To generate a checksum on HPC is straightforward. It should be noted, however, that this process can take up to a few hours to complete depending on the size of the file. If this is the case, it may be advised to either run the command on the file transfer node or submit the command as a job through PBS to keep activity on the login nodes to a minimum. To generate the checksum:

```
md5sum /path/to/file/and/filename 
```

### Google Drive Checksum

If the transfer has been made to Google Drive, there is a [Google Chrome extension](https://chrome.google.com/webstore/detail/drive-checksum/gmkleokinbpmgpkpenljbobeffaobibk?hl=en-US) that can be downloaded and used to generate a spreadsheet of checksums.

To create a spreadsheet, open a new Google Sheets document and from the top menu, choose <p><kbd>Add-ons</kbd>&rarr;<kbd>Drive Checksum</kbd>&rarr;<kbd>Find</kbd><p> Then select <kbd>Entire Drive</kbd> and click <kbd>Find</kbd>. The spreadsheet will then autofill with filenames and their checksums. Once the relevant file is complete, you can compare it with the checksum from the source machine.

_Note: If you do not have a premium account, you only have the option of generating a spreadsheet for every document in your Drive. If you have a premium account, you have the option of being more selective._ 
