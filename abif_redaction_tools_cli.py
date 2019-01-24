# abif_redaction_tools_cli.py

import os
import shutil
import re
import argparse


## The command line interface needs to be tested end-to-end.

## Improvements:
## This code inventories the parent directory prior to redaction. It
##  would be more efficient if files were identified and redacted in
##  the same loop.


class ABIF_Handler:

    def __init__(self, args):
        
        self.args = args

        self.pdir = self.args.pd
        self.__parse_pdir()
        self.tdir = self.args.od


    def get_fdirs(self):
        return self.fdirs


    def get_tdir(self):
        return self.tdir


    def redact_ab1_files(self):

        """
        Function looks for accession re_patt in file names, removes it,
        looks for the same value in the file content, replaces it with
        an equal number of underscores (_), saves the accession-redacted
        file.
        The accession cannot be deleted entirely, because it exists in
        a Pascal-like byte string, wherein the first byte of the string
        is the number of characters in the string.
        """

        self.ap = args.ap

        self.od = args.od
        
        for path in self.fdirs:
            
            target_dir = args.od + "/" + path.split("\\")[-2]
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            new_fname, accession = self.__pop_accession(path)
            fdata = self.__parse_file(path)
            new_fdata = self.__anonymize_byte_list(fdata, accession)

            self.__save_byte_file(new_fname, new_fdata, target_dir)


    def move_non_ab1_files(self, target_directory):
        
        tpd = os.path.normpath(target_directory)
            
        for p in self.copy_only:
            target_dir = tpd + "/" + p.split("\\")[-2]
            fname = os.path.split(p)[1]
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.copy2(p, target_dir + "/" + fname)


    def __parse_pdir(self):

        self.fdirs = []
        self.copy_only = []
        
        if self.pdir:
            dwalker = os.walk(self.pdir)
            
            for subpath, folders, files in dwalker:
                for f in files:

                    path = os.path.normpath(subpath + "/" + f)
                    if f.endswith(".ab1"):
                        self.fdirs.append(path)
                    else:
                        self.copy_only.append(path)
        

    def __parse_file(self, fdir):
        
        byte_list = []
        
        with open(fdir, 'br') as bf:
            for line in bf:
                byte_list.append(line)

        return byte_list
    

    def __anonymize_byte_list(self, byte_list, accession):

        if not accession:
            return byte_list
        
        ba = bytes(accession, 'utf-8')
        pad = b'_' * len(accession)
        
        for i, el in enumerate(byte_list):
            if ba in el:
                byte_list[i] = pad.join(el.split(ba))
                break

        return byte_list


    def __pop_accession(self, path_or_fname):
        
        """
        Var "text" can be a path or a file name. Returns tuple with
        (<new file name>, <redacted accession number>)
        """
        
        fname = path_or_fname.split("\\")[-1]    
        fname_parts = fname.split(".")[0].split("_")
        accession = None

        for part in fname_parts:
            if self.__is_accession(part):
                accession = part
                fname_parts.remove(part)
            return ("_".join(fname_parts) + ".ab1", accession)
    

    def __is_accession(self, text_var):

        if self.accession_pattern:
            pattern = self.accession_pattern
        else:
            pattern = r'\b[01]\d-[0123]\d\d-\d{5,6}\b'
        
        if re.match(pattern, text_var):
            return True

        return False


    def __save_byte_file(self, name, byte_list, path):
        bs = b''.join(byte_list)
        with open(path + "/" + name, 'bw') as f:
            f.write(bs)
            

def main():
    
    parser = argparse.ArgumentParser(description='Tool for redacting .ab1 fil'\
                                     'es in batch. Ssensitive information is '\
                                     'must be contained in the file name as a'\
                                     'n accession number surrounded by unders'\
                                     'scores. The default accession number is'\
                                     ' defined as two digits (ints 0-9) follo'\
                                     'wed by a dash (-) followed by three dig'\
                                     'its, followed by another dash, then 5 o'\
                                     'r 6 more digits. Accession numbers that'\
                                     'are either 1) not part of the file name'\
                                     'or 2) do not meet the above criteria wi'\
                                     'll not be removed from the .ab1 file co'\
                                     'ntents or file name unless the pattern '\
                                     'is defined by the user (option "-ap").'
                                     'Sensitive info will be replaced with an'\
                                     'equal number of underscores in the file'\
                                     'name and in the .ab1 file metadata.')
    
    parser.add_argument('pd', '--parent_directory', type=str, help='Parent di'\
                        'rectory that contains .ab1 files or folders that con'\
                        'tain .ab1 files to be redacted.')
    
    parser.add_argument('od', '--output_directory', type=str, help='Directory'\
                        ' in which the parent directory will be re-constructe'\
                        'd using accession-redacted .ab1 files.')
    
    parser.add_argument('-ap', '--accession_pattern', type=str, help='Regular'\
                        ' expression defining the accession number pattern. D'\
                        'efault recognizes "12-345-678910" and "12-345-67891"'\
                        '\nTo recognize\nABC_12345678910, use:\n    [A-Z]{3}_'\
                        '[01]\d[0123]\d\d\d{5,6}\\b'
                        'For help with determining what regular expression wi'\
                        'll identify your accession number, go to:\nhttps://r'\
                        'egex101.com',
                        default=r'\b[01]\d-[0123]\d\d-\d{5,6}\b')
    
    parser.add_argument('-mof' '--move_other_files', action='store_true',
                        help='This option will copy files without the .ab1 ex'\
                        'tension. The output directory will then contain a co'\
                        'py of every file in the parent directory.')
    
    args = parser.parse_args()

    a = ABIF_Handler(args)
    a.redact_ab1_files()

    if not args.mof:
        a.move_non_ab1_files(args.od)

if __name__ == '__main__':
    main()

    

