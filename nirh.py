import argparse
import patoolib
import tempfile
import os
import logging

# Remove patoollib logging
logging.getLogger("patoolib").setLevel(logging.WARNING)

"""
-- nihr (needle in a rar-haystack) --

This python script will iterate over every rar file in a directory,
unrar the files to a temporary & check for the supplied string.
If the string is found, it (along with the file name) 
will be printed and/or written to a output file.
After the check, the contents of the folder are cleared
and the next rar file is unpacked.

Demo:
There are 2 rar archives with 5 text documents each. 
Use the demo string "SUPERSECRETMESSAGE" 
to find the secret messages.
"""

## Argument Parsing ##


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def getURL(self):
        if "://" not in self.url:
            return "http://" + self.url
        else:
            return self.url
    pass


def getArgs():
    desc = "nirh: find a string in rar archive(s)"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('string', type=str,
                        help="search string (needle)")
    parser.add_argument(
        'dir', type=str, help="target directory (haystack)")
    parser.add_argument('-o', metavar="filename", type=str,
                        help="Output found string(s) and asssociated file(s) to file")
    # parser.print_help()
    args = Args()
    parser.parse_args(namespace=args)
    if (args.o != None):
        return (args.string, args.dir + "/", args.o + ".txt")
    else:
        return (args.string, args.dir + "/", False)

# Info/Error Messages


def printInfo(msg):
    return print("[*]", msg)


def printError(msg):
    return print("[!]", msg)


## Unpacking the tar file ##


def createTmpDir():
    temp_dir = tempfile.TemporaryDirectory()
    #print(f"Created temporary extract directory in {temp_dir.name}")
    return (temp_dir, temp_dir.name)


def closeTmpDir(tmpdir):
    try:
        tmpdir.cleanup()
        return True
    except:
        print("[!] Couldn't close temporary directory...")
        return False


def doExtract(rar_location, temp_dir):
    try:
        patoolib.extract_archive(rar_location, outdir=temp_dir)
        # print(os.listdir(temp_dir))
        return True
    except patoolib.util.PatoolError as err:
        printError("Couldn't extract rar archive...")
        print(err)
        return False


def writeFind(msg, filename):
    file = open(filename, "a")
    file.write(msg)
    file.write("\n" * 2)
    file.close()
    return True


def SearchDir(dir, file_dir, search, outfile, count):
    for file in os.listdir(dir):
        f = open(file_dir + file)
        content = f.readlines()
        for line in content:
            if search not in line:
                continue
            find_msg = f"Found {search} in {file}:\n{line}"
            printInfo(find_msg)
            if outfile != False:
                writeFind(find_msg, outfile)
            count = count + 1
        f.close()
        os.remove(file_dir + file)
    return count


def riterator(search_dir, tmp_dir, search_str, outputfile=False):
    count = 0
    if os.name == "nt":
        temp_file_dir = tmp_dir + "\\"
    else:
        temp_file_dir = tmp_dir + "/"
    for file in os.listdir(search_dir):
        file_path = search_dir + file
        if not file.endswith(".rar"):
            continue
        doExtract(file_path, tmp_dir)
        new_count = SearchDir(tmp_dir, temp_file_dir,
                              search_str, outputfile, count)
        count = new_count
    return count


def main():
    (string, dir, outfile) = getArgs()
    (tmpdir_class, temp_path) = createTmpDir()
    iterated = riterator(dir, temp_path, string, outfile)
    print()
    count_msg = f"Found {iterated} occurences of {string}!"
    writeFind(count_msg, outfile)
    printInfo(count_msg)
    print()
    printInfo("Thanks for using nirh! \nExiting...")
    print()

    tmpdir_class.cleanup()
    exit()


if __name__ == "__main__":
    main()
