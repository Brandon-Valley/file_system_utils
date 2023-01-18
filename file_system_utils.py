import filecmp
import glob
import os
from pprint import pprint
import shutil
import ntpath
from collections import namedtuple


if __name__ == "__main__":
    from   usms.exception_utils import exception_utils as eu
else:
    from . usms.exception_utils import exception_utils as eu



Path_basename_nt = namedtuple('Path_basename_nt', 'path basename')


''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Get info about GIVEN object
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

def abs_path(in_path):
    return os.path.abspath(in_path)

def is_dir(in_path):
    return os.path.isdir(in_path)

def is_file(in_path):
    return os.path.isfile(in_path)

''' more efficient to use one of the above funcs if you know the object type '''
def exists(in_path):
    return is_dir(in_path) or is_file(in_path)


''' gets size of dir (and maybe file?) in bytes '''
def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


''' not protected so it works on files and urls - file.tcl will return ".tcl"  '''
def get_extention(in_file_path):
    return os.path.splitext(in_file_path)[1]


''' file.tcl will return ".tcl" '''
def get_file_extension(in_file_path):
    if not is_file(in_file_path):
        raise Exception("ERROR:  in_file_path must point to a file that exists")

    return get_extention(in_file_path)


''' !!!!! ONLY WAY TO USE THIS FUNC:  file_system_utils.get_abs_path_to_parent_dir_of_file(__file__) !!!!!
    returns absolute path to the dir that contains the file that calls this function,
    NOT the current working directory '''
def get_abs_path_to_parent_dir_of_file(file_obj):
    return os.path.dirname(os.path.abspath(file_obj))


def raise_exception_if_object_not_exist(obj_path, custom_msg = None):
    if not is_file(obj_path) and not is_dir(obj_path):
        if custom_msg == None:
            raise Exception("ERROR:  This thing does not exist: ", obj_path)
        else:
            raise Exception(custom_msg)



''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Get info about objects inside GIVEN DIR
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

def get_newest_file_path(dir_path):
    list_of_files = glob.glob(dir_path + '/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    # print (latest_file)
    return latest_file


'''returns list - should update get_dir_content_l() instead of using this'''
def get_relative_path_of_files_in_dir(dir_path, file_type = None):
    # Getting the current work directory (cwd)
    thisdir = os.getcwd()

    path_list = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(dir_path):
        for file in f:
            if file_type == None or file_type in file:
#                 print(os.path.join(r, file))
                path_list.append(os.path.join(r, file))
    return path_list



''' in_dir_path - can be either abs or relative path '''
def get_dir_content_l(in_dir_path, object_type = 'all', content_type = 'abs_path', recurs_dirs = False, rel_to_path = None):
    if is_dir(in_dir_path) != True and in_dir_path != '':
        raise Exception("ERROR:  in_dir_path must point to dir, in_dir_path: " + in_dir_path)
    if object_type not in ['all', 'dir', 'file']:
        raise Exception("ERROR:  Invalid object_type: ", object_type, "  object_type must be one of:  ['all', 'dir', 'file']")
    if content_type not in ['abs_path', 'rel_path', 'name', 'abs_path_basename_nt', 'rel_path_basename_nt']:
        raise Exception("ERROR:  Invalid content_type: ", content_type, "  object_type must be one of:  ['abs_path', 'rel_path', 'name', 'abs_path_basename_nt', 'rel_path_basename_nt']")
    if content_type == 'rel_path' and rel_to_path == None:
        raise Exception("ERROR:  Invalid param combo: content_type == 'rel_path' and rel_to_path == None")

    # change content_type if needed for recursion
    og_content_type = content_type
    if content_type == 'abs_path_basename_nt':
        content_type = 'abs_path'
    elif content_type == 'rel_path_basename_nt':
        content_type = 'rel_path'


    abs_in_dir_path = get_abs_path_from_rel_path(in_dir_path)
    object_name_l = os.listdir(abs_in_dir_path) # list of names of all dirs and files in dir


    if content_type == 'name' and object_type == 'all':
        return object_name_l

    # get header - str that will be added in front of obj name
    header = ''
    if   content_type == 'abs_path':
        header = abs_in_dir_path + '//'
    elif content_type == 'rel_path':
#         raise Exception('ERROR: rel_path option not yet implemented') # look at get_relative_path_of_files_in_dir(dir_path, file_type)
        header = get_rel_path_from_compare(in_dir_path, rel_to_path) + '//'

    content_l = []

    # fill content_l
    for object_name in object_name_l:
        if object_type   == 'all' and not recurs_dirs:
            content_l.append(header + object_name)
        else:
            abs_obj_path = abs_in_dir_path + '//' + object_name

            if   object_type in ('all', 'file') and is_file(abs_obj_path):
                content_l.append(header + object_name)
            elif object_type in ('all', 'dir')  and is_dir (abs_obj_path):
                content_l.append(header + object_name)

#                 if recurs_dirs:
#                     content_l += get_dir_content_l(abs_obj_path, object_type, content_type, recurs_dirs, rel_to_path)

        if recurs_dirs and is_dir(abs_in_dir_path + '//' + object_name):
            content_l += get_dir_content_l(abs_obj_path, object_type, content_type, recurs_dirs, rel_to_path)


    # make final container if needed
    if og_content_type in ('abs_path_basename_nt', 'rel_path_basename_nt'):
        return path_l_to_path_basename_ntl(content_l)

    return content_l



"""returns oldest first, youngest last"""
def get_file_paths_in_dir_by_age(dirpath):
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))

    abs_path_l = []
    for rel_path in a:
        abs_path_l.append(dirpath + '/' + rel_path)
    return abs_path_l



''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Operate on or move given OBJECT(s)
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

def make_dir_if_not_exist(dir_path):
    abs_dir_path = get_abs_path_from_rel_path(dir_path)
    if not os.path.exists(abs_dir_path):
        os.makedirs(abs_dir_path)


def make_file_if_not_exist(file_path):
    if not is_file(file_path):
        parent_dir_path = get_parent_dir_path_from_path(file_path)
        make_dir_if_not_exist(parent_dir_path)
        file = open(file_path, "w")
        file.close()


def delete_single_fs_obj_fast(path):
    def onerror(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.

        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.

        If the error is for another reason it re-raises the error.

        Usage : ``shutil.rmtree(path, onerror=onerror)``
        """
        import stat
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    if os.path.exists(path):
        if   os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=False, onerror=onerror)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            raise Exception('ERROR:  Gave something that is not a file or a dir, bad path: ', path)


def delete_fs_obj_l_fast(path_l):
    for path in path_l:
        delete_single_fs_obj_fast(path)


# works for single path str or list of paths
def delete_if_exists(path_str_or_l):
    if not isinstance(path_str_or_l, list):
        path_str_or_l = [path_str_or_l]

    for path in path_str_or_l:
        delete_single_fs_obj_fast(path)


''' Works with dir also
    will do nothing if src_file_path == dest_file_path '''
def rename_file_overwrite(src_object_path, dest_object_path):
    if not paths_equal(src_object_path, dest_object_path):
        delete_if_exists(dest_object_path)
        try:
            os.rename(src_object_path, dest_object_path)
        except OSError:
            delete_if_exists(dest_object_path)
            shutil.move(src_object_path, dest_object_path)



def rename_dir_contents(dir_path, replace_d, object_type = 'all', recurs_dirs = False):
    ''' Only renames basenames '''

    eu.error_if_param_type_not_in_whitelist(dir_path   , ['str'])
    eu.error_if_not_is_dir                 (dir_path)
    eu.error_if_param_type_not_in_whitelist(replace_d  , ['dict'])
    eu.error_if_param_type_not_in_whitelist(object_type, ['str'])
    eu.error_if_param_key_not_in_whitelist (object_type, ['all', 'file', 'dir'])
    eu.error_if_param_type_not_in_whitelist(recurs_dirs, ['bool'])


    raw_dir_content_abs_path_l = get_dir_content_l(dir_path, object_type, 'abs_path', recurs_dirs)

    # must sort list by length so you don't rename a dir above another object
    sorted_dir_content_abs_path_l = sorted(raw_dir_content_abs_path_l, key=len, reverse = True)

    sorted_dir_content_abs_path_path_basename_ntl = path_l_to_path_basename_ntl(sorted_dir_content_abs_path_l)


    for sorted_dir_content_abs_path_path_basename_nt in sorted_dir_content_abs_path_path_basename_ntl:
        new_basename = sorted_dir_content_abs_path_path_basename_nt.basename

        for replace_str, replace_with_this_str in replace_d.items():
            new_basename = new_basename.replace(replace_str, replace_with_this_str)

        # only rename if something was replaced
        if new_basename != sorted_dir_content_abs_path_path_basename_nt.basename:
            parent_dir_path = os.path.dirname(sorted_dir_content_abs_path_path_basename_nt.path)
            new_path = os.path.join(parent_dir_path, new_basename)
            rename_file_overwrite(sorted_dir_content_abs_path_path_basename_nt.path, new_path)



''' can take a single str path for path_l '''
def copy_objects_to_dest(path_l_or_str, dest_parent_dir_path, copy_dir_content = True):
    eu.error_if_param_type_not_in_whitelist(path_l_or_str       , ['str', 'list'])
    eu.error_if_param_type_not_in_whitelist(dest_parent_dir_path, ['str'])
    eu.error_if_param_type_not_in_whitelist(copy_dir_content    , ['bool'])

    def ig_f(dir, files):
        return [f for f in files if os.path.isfile(os.path.join(dir, f))]

    if isinstance(path_l_or_str, str):
        path_l_or_str = [path_l_or_str]

    make_dir_if_not_exist(dest_parent_dir_path)

    for path in path_l_or_str:
        eu.error_if_not_is_file_or_is_dir(path)

        if  os.path.isdir(path):
            path_basename = get_basename_from_path(path)
            dest_dir_path = dest_parent_dir_path + '//' + path_basename
            delete_if_exists(dest_dir_path)

            if copy_dir_content:
                shutil.copytree(path, dest_dir_path)
            else:
                shutil.copytree(path, dest_dir_path, ignore=ig_f)


        elif os.path.isfile(path):
            shutil.copy(path, dest_parent_dir_path)


def copy_object_to_path(src_path_str, dest_path_str, copy_dir_content = True):
    """
    Copies the file or dir at src_path_str to dest_path_str
    """
    eu.error_if_param_type_not_in_whitelist(src_path_str    , ['str']) # only 1 at a time
    eu.error_if_param_type_not_in_whitelist(dest_path_str   , ['str'])
    eu.error_if_param_type_not_in_whitelist(copy_dir_content, ['bool'])
    eu.error_if_not_is_file_or_is_dir      (src_path_str)

    if os.path.isfile(src_path_str):
        shutil.copy(src_path_str, dest_path_str)
    elif os.path.isdir(src_path_str):
        raise Exception("ERROR: NOT YET IMPLEMENTED")
#         shutil.copy(src_path_str, dest_path_str) # does not work, perm error
    else:
        raise Exception("ERROR: How did you even get here?")




def copy_object_to_dest_then_rename(path_str, dest_parent_dir_path, new_object_name, copy_dir_content = True):
    """
    Deprecated: Do Not Touch!  Just use copy_object_to_path instead
    """

    eu.error_if_param_type_not_in_whitelist(path_str       , ['str']) # only 1 at a time
    eu.error_if_param_type_not_in_whitelist(new_object_name, ['str'])

    copy_objects_to_dest(path_str, dest_parent_dir_path, copy_dir_content)

    basename = get_basename_from_path(path_str, include_ext = True)

    og_dest_obj_path = os.path.join(dest_parent_dir_path, basename)
    new_dest_obj_path = os.path.join(dest_parent_dir_path, new_object_name)

    rename_file_overwrite(og_dest_obj_path, new_dest_obj_path)




'''copies then deletes'''
def move_objects_to_dest(path_l, dest_dir_path):
    copy_objects_to_dest(path_l, dest_dir_path)

    for path in path_l:
        delete_if_exists(path)


'''copies then deletes'''
def move_dir_contents_to_dest(in_dir_path, dest_dir_path):
    path_l = get_dir_content_l(in_dir_path, object_type = 'all', content_type = 'abs_path')
    move_objects_to_dest(path_l, dest_dir_path)



''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Operate on or move given objects in GIVEN DIR
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

def delete_all_files_in_dir(dir_path):
    for the_file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def delete_all_dirs_in_dir_if_exists(dir_path):
    if os.path.exists(dir_path):
        for the_file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, the_file)
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)


''' dont_del_path_l can be abs or rel paths '''
def delete_all_dir_content_except_given_in_root(dir_path, dont_del_fs_obj_name_l):
    if os.path.exists(dir_path):
        dir_content_path_l = get_dir_content_l(dir_path, object_type = 'all', content_type = 'abs_path')
        del_path_l = []

        for dir_content_path in dir_content_path_l:
            if not get_basename_from_path(dir_content_path) in dont_del_fs_obj_name_l:
                del_path_l.append(dir_content_path)

        # if VVV throws error, make exception to say so
        delete_fs_obj_l_fast(del_path_l)



''' copy all files and dirs in given dir into new dir '''
def copy_dir_contents_to_dest(src_dir_path, dest_dir_path):
    dir_content_l = get_dir_content_l(src_dir_path, object_type = 'all', content_type = 'abs_path')
    copy_objects_to_dest(dir_content_l, dest_dir_path)



''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Get info about or edit path
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

''' True if the current user has sufficient permissions to create the passed
    pathname; False otherwise. '''
def is_path_creatable(pathname):
    # Parent directory of the passed path. If empty, we substitute the current
    # working directory (CWD) instead.
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)


''' returns true if path could be created and ends with given extension '''
def is_file_path_valid(path, extension = None):
    if not is_path_creatable(path):
        return False
    if extension != None and not path.endswith(extension):
        return False
    return True


""" returns given path with replaced extension: mp4, jpg, etc... """
def replace_extension(in_file_path, new_extension):
    path_split = os.path.splitext(in_file_path)

    if len(path_split) < 2:
        raise Exception("ERROR:  in_file_path must contain at least 1 '.'")

    new_path = ''
    for str in path_split[0:-1]:
        new_path += str + '.'
    new_path += new_extension

    return new_path



def paths_equal(path_1_str_or_l, path_2_str_or_l):
    ''' Depreciated, use paths_compare()'''
    return paths_compare(path_1_str_or_l, path_2_str_or_l, compare_mode = 'paths_equal')


def paths_compare(path_1_str_or_l, path_2_str_or_l, compare_mode = 'equal'):
    '''
        Returns true if compare mode is true for any 2 combinations of paths

        Compare Modes:

            paths_equal:
                True if 2 paths point to the same place - rel / abs

            starts_with:
                True if any path 1 starts with any path 2

            is_component_name:
                True if given str is equal to any component of given path
                    Ex:    (a\b\c, b)   -> True
                           (a\box\c, b) -> False
    '''

    # make sure both params are lists
    if isinstance(path_1_str_or_l, str):
        path_1_str_or_l = [path_1_str_or_l]

    if isinstance(path_2_str_or_l, str):
        path_2_str_or_l = [path_2_str_or_l]

    for path_1 in path_1_str_or_l:
        for path_2 in path_2_str_or_l:

            abs_path_1 = os.path.abspath(path_1)
            abs_path_2 = os.path.abspath(path_2)


            if   compare_mode == 'paths_equal':
                if abs_path_1 == abs_path_2:
                    return True

            elif compare_mode == 'starts_with':
                if abs_path_1.startswith(abs_path_2):
                    return True

            elif compare_mode == 'is_component_name':
                if path_2 in split_path_into_component_name_l(path_1):
                    return True

            else:
                raise Exception('NOT IMPLEMENTED: compare_mode:' + compare_mode)

    return False


def get_rel_path_from_compare(child_path, parent_path):
    return os.path.relpath(child_path, parent_path)

def get_abs_path_from_rel_path(in_rel_path):
    return os.path.abspath(in_rel_path)

def get_basename_from_path(path, include_ext = True):
    if include_ext:
        return ntpath.basename(path)
    else:
        return os.path.splitext(ntpath.basename(path))[0]

def get_parent_dir_path_from_path(path):
    return os.path.dirname(path)

def get_top_level_parent_dir_name(path):
    return path.split('\\')[0].split('/')[0]

def is_abs(path):
    '''
        Path does not need to exist, just needs to be abs
    '''
    return os.path.isabs(path)

def split_path_into_component_name_l(path):
    path = path.replace('\\', '//')
    return path.strip('//').split('//')



''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Common Use Cases
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

def path_l_to_abs_path_l(path_l):
    abs_path_l = []
    for path in path_l:
        abs_path_l.append(abs_path(path))

    return abs_path_l


def path_l_to_basename_l(path_l):
    abs_path_l = []
    for path in path_l:
        abs_path_l.append(get_basename_from_path(path))

    return abs_path_l


def path_l_remove(path_l, to_remove_str_or_l, removal_mode = 'basename_equals'):
    eu.error_if_param_type_not_in_whitelist(path_l,             ['list', 'tuple'])
    eu.error_if_param_type_not_in_whitelist(to_remove_str_or_l, ['list', 'tuple', 'str'])
    eu.error_if_param_key_not_in_whitelist(removal_mode, ['basename_equals', 'in_basename', 'paths_equal', 'in_path', 'starts_with', 'is_component_name'])

    if isinstance(to_remove_str_or_l, str):
        to_remove_str_or_l = [to_remove_str_or_l]

    def path_l_remove__basename_equals():
        return [path for path in path_l if not get_basename_from_path(path) in to_remove_str_or_l]

    def path_l_remove__if_not_paths_compare():
        return [path for path in path_l if not paths_compare(path, to_remove_str_or_l, compare_mode = removal_mode)]

    if removal_mode == 'basename_equals':
        return path_l_remove__basename_equals()

    elif removal_mode in ['paths_equal', 'starts_with', 'is_component_name']:
        return path_l_remove__if_not_paths_compare()

    else:
        raise Exception('ERROR:  NOT IMPLEMENTED')


''' can take list of paths or single path '''
def path_l_to_path_basename_ntl(path_l):
    eu.error_if_param_type_not_in_whitelist(path_l, ['list', 'tuple', 'str'])

    # correct to list if given single path
    if isinstance(path_l, str):
        path_l = [path_l]

    # fill ntl
    path_basename_ntl = []

    for path in path_l:
        basename = get_basename_from_path(path)
        path_basename_ntl.append(Path_basename_nt(path, basename))

    return path_basename_ntl


def get_file_path_l_w_duplicate_files_removed(file_path_l, verbose = False):
    """ If 2 files are binary same, will keep whichever file appears first in file_path_l
        - Returns list of unique files in same relative order as file_path_l
        - file_path_l must be type 'list'
        - If len(file_path_l) < 2, just returns file_path_l
    """
    if not isinstance(file_path_l, list):
        raise TypeError(f"file_path_l must be of type list, not {type(file_path_l)}")
    if len(file_path_l) < 2:
        return file_path_l

    unique_file_path_l = [file_path_l[0]]

    for file_path in file_path_l[1:]:
        file_is_unique = True

        for unique_file_path in unique_file_path_l:
            if filecmp.cmp(file_path, unique_file_path):
                if verbose:
                    print(f"Found Duplicate File: F1:{file_path} == F2{unique_file_path}, Removing F1...")
                file_is_unique = False
                break
        if file_is_unique:
            unique_file_path_l.append(file_path)

    return unique_file_path_l









''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''
        Working
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''






if __name__ == '__main__':
    print('In Main:  file_system_utils')
    file_path_l = get_dir_content_l("C:/Users/Brandon/Documents/Other/temp/Family_Guy__Star_Trek__Clip____TBS", "file")
    new_l = get_file_path_l_w_duplicate_files_removed(file_path_l, True)
    print(f"{len(file_path_l)=}")
    print(f"{len(new_l)=}")

    print('End of Main:  file_system_utils')
