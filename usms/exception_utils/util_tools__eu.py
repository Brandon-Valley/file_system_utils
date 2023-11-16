# this file exists mostly for storing functions from other utils that I don't want to import as submodules



import os



''' Unique '''

def get_msg(custom_msg, default_msg):    
    if custom_msg == None:
        return default_msg
    else:
        return custom_msg



''' Copied '''

def is_dir(in_path):
    return os.path.isdir(in_path)

def is_file(in_path):
    return os.path.isfile(in_path)

''' more efficient to use one of the above funcs if you know the object type '''
def exists(in_path):
    return is_dir(in_path) or is_file(in_path)

def is_abs(path):
    '''
        Path does not need to exist, just needs to be abs
    '''
    return os.path.isabs(path)

''' not protected so it works on files and urls - file.tcl will return ".tcl"  '''
def get_extension(in_file_path):
    return os.path.splitext(in_file_path)[1]


def is_path_creatable(pathname):
    ''' 
        True if the current user has sufficient permissions to create the passed
        pathname; False otherwise. 
    '''
    # Parent directory of the passed path. If empty, we substitute the current
    # working directory (CWD) instead.
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)





