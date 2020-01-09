# abif-tools

Tools for anonymizing ABI files.

## Application:

This is a niche program for creating a copy of .ab1 files wherein sensitive information in the file metadata is replaced with underscores. Modifying .ab1 files is not straightforward because they are binary files with heterogeneous data structures, including Pascal-like strings (https://projects.nfstc.org/workshops/resources/articles/ABIF_File_Format.pdf) wherein the byte preceding the text indicates the length of the text string.

This program:
* creates an identical directory structure
* finds every .ab1 file in the original directory
* finds, redacts any ARUP accession numbers from the file name
* redacts the same accession from the file metadata
* saves redacted .ab1 file in the appropriate location in the new directory
* copies any non-.ab1 files without modification to the new directory
