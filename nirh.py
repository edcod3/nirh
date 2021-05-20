import argparse
import patoolib
import tempfile
import os

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
    pass


def getArgs():
    desc = "nirh: find a string in rar archive(s)"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('string', type=str,
                        help="search string (needle)")
    parser.add_argument(
        'dir', type=str, help="target directory (haystack)")
    parser.add_argument('-o',"--outfile", metavar="filename", type=str,
                        help="Output found string(s) and asssociated file(s) to file")
    parser.add_argument("-v", "--verbose", help="verbose output of extraction process",
                    action="store_true")
    #parser.print_help()
    args = Args()
    parser.parse_args(namespace=args)
    if (args.outfile != None):
        return (args.string, args.dir + "/", args.outfile + ".txt", bool(args.verbose))
    else:
        return (args.string, args.dir + "/", False, bool(args.verbose))

# Info/Error Messages


def printInfo(msg):
    return print("[*]", msg)


def printError(msg):
    return print("[!]", msg)


## Unpacking the tar file ##


def createTmpDir(verbose):
    temp_dir = tempfile.TemporaryDirectory()
    if verbose:
        print(f"Created temporary extract directory in {temp_dir.name}")
    return (temp_dir, temp_dir.name)


def closeTmpDir(tmpdir):
    try:
        tmpdir.cleanup()
        return True
    except:
        print("[!] Couldn't close temporary directory...")
        return False

def writeFind(msg, filename):
    file = open(filename, "a")
    file.write(msg)
    file.write("\n" * 2)
    file.close()
    return True

def doExtract(rar_location, temp_dir, verbose):
    try:
        patoolib.extract_archive(rar_location, outdir=temp_dir)
        #print(os.listdir(temp_dir))
        return True
    except patoolib.util.PatoolError as err:
        printError("Couldn't extract rar archive...")
        print(err)
        writeFind(err, "error.log")
        return False


def SearchDir(dir, search, outfile, count):
    for file in os.listdir(dir):
        file_dir = os.path.join(dir, file)
        if os.path.isdir(file_dir):
            SearchDir(file_dir, search, outfile, count)
        elif os.path.isfile(file_dir):    
            f = open(file_dir)
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
            os.remove(file_dir)
        else:
            printError("An error occured: Didn't find valid file")
    return count


def riterator(search_dir, tmp_dir, search_str, verbose, outputfile=False):
    find_count = 0
    file_count = 1
    for file in os.listdir(search_dir):
        if verbose:
            printInfo(f"Extracting rar archive {file_count}/{len(os.listdir(search_dir))}")
            print()
        file_count = file_count + 1
        file_path = search_dir + file
        if not file.endswith(".rar"):
            continue
        doExtract(file_path, tmp_dir, verbose)
        new_find_count = SearchDir(tmp_dir,search_str, outputfile, find_count)
        find_count = new_find_count
    return find_count


def main():
    (string, dir, outfile, verbose) = getArgs()
    (tmpdir_class, temp_path) = createTmpDir(verbose)
    iterated = riterator(dir, temp_path, string, verbose, outfile)
    print()
    count_msg = f"Found {iterated} occurences of {string}!"
    if outfile != False:
        writeFind(count_msg, outfile)
    printInfo(count_msg)
    print()
    printInfo("Thanks for using nirh! \nExiting...")
    print()
    tmpdir_class.cleanup()
    exit()


if __name__ == "__main__":
    main()
