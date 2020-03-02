''' -- VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV -- All Utilities Standard Header -- VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV -- '''
import sys, os    ;     sys.path.insert(1, os.path.join(sys.path[0], os.path.dirname(os.path.abspath(__file__)))) # to allow for relative imports, delete any imports under this line

util_submodule_l = []  # list of all imports from local util_submodules that could be imported elsewhere to temporarily remove from sys.modules

# temporarily remove any modules that could conflict with this file's local util_submodule imports
og_sys_modules = sys.modules    ;    pop_l = [] # save the original sys.modules to be restored at the end of this file
for module_descrip in sys.modules.keys():  
    if any( util_submodule in module_descrip for util_submodule in util_submodule_l )    :    pop_l.append(module_descrip) # add any module that could conflict local util_submodule imports to list to be removed from sys.modules temporarily
for module_descrip in pop_l    :    sys.modules.pop(module_descrip) # remove all modules put in pop list from sys.modules
util_submodule_import_check_count = 0 # count to make sure you don't add a local util_submodule import without adding it to util_submodule_l

''' -- VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV -- All Utilities Standard: Local Utility Submodule Imports  -- VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV -- '''



''' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ '''
if util_submodule_import_check_count != len(util_submodule_l)    :    raise Exception("ERROR:  You probably added a local util_submodule import without adding it to the util_submodule_l")
''' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ '''

import glob
import os
import shutil
from distutils.dir_util import copy_tree
import ntpath


''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''                                                                           
        Get info about GIVEN object
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''

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


def get_file_extension(in_file_path):
    if not is_file(in_file_path):
        raise Exception("ERROR:  in_file_path must point to a file that exists")
    
    extension = os.path.splitext(in_file_path)[1]
    return extension


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
def get_relative_path_of_files_in_dir(dir_path, file_type):
    # Getting the current work directory (cwd)
    thisdir = os.getcwd()
    
    path_list = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(dir_path):
        for file in f:
            if file_type in file:
#                 print(os.path.join(r, file))
                path_list.append(os.path.join(r, file))
    return path_list



''' in_dir_path - can be either abs or relative path '''
def get_dir_content_l(in_dir_path, object_type = 'all', content_type = 'abs_path'):
    if is_dir(in_dir_path) != True and in_dir_path != '':
        raise Exception("ERROR:  in_dir_path must point to dir")
    if object_type not in ['all', 'dir', 'file']:
        raise Exception("ERROR:  Invalid object_type: ", object_type, "  object_type must be one of:  ['all', 'dir', 'file']")
    if content_type not in ['abs_path', 'rel_path', 'name']:
        raise Exception("ERROR:  Invalid content_type: ", content_type, "  object_type must be one of:  ['abs_path', 'rel_path', 'name']")
    
    abs_in_dir_path = get_abs_path_from_rel_path(in_dir_path)
    object_name_l = os.listdir(abs_in_dir_path) # list of names of all dirs and files in dir
    
    if content_type == 'name' and object_type == 'all':
        return object_name_l
    
    # get header - str that will be added in front of obj name
    header = '' 
    if   content_type == 'abs_path':
        header = abs_in_dir_path + '//' 
    elif content_type == 'rel_path':
        raise Exception('ERROR: rel_path option not yet implemented')
    
    content_l = []
    
    # fill content_l
    for object_name in object_name_l:
        if object_type   == 'all':
            content_l.append(header + object_name)
        else:
            abs_obj_path = abs_in_dir_path + '//' + object_name
            
            if   object_type == 'file' and is_file(abs_obj_path):
                content_l.append(header + object_name)
            elif object_type == 'dir'  and is_dir (abs_obj_path):
                content_l.append(header + object_name)

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
    if os.path.exists(path):
        if   os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            raise Exception('ERROR:  Gave something that is not a file or a dir, bad path: ', path)


def delete_fs_obj_l_fast(path_l):
    for path in path_l:
        delete_single_fs_obj_fast(path)   
        
        
# works for single path str or list of paths
def delete_if_exists(path_str_or_l):
    if isinstance(path_str_or_l, str):
        path_str_or_l = [path_str_or_l]
    
    for path in path_str_or_l:
        delete_single_fs_obj_fast(path)


''' will do nothing if src_file_path == dest_file_path '''
def rename_file_overwrite(src_file_path, dest_file_path):
    if not paths_equal(src_file_path, dest_file_path):        
        delete_if_exists(dest_file_path)
        os.rename(src_file_path, dest_file_path)


''' can take a single str path for path_l '''
def copy_objects_to_dest(path_l, dest_parent_dir_path):
    if type(path_l) == 'class <str>':
        path_l = [path_l]
        
    make_dir_if_not_exist(dest_parent_dir_path)
    
    for path in path_l:
        if   os.path.isdir(path):
            copy_tree(path, dest_parent_dir_path)
        elif os.path.isfile(path):
            shutil.copy(path, dest_parent_dir_path)

        
'''copies then deletes'''
def move_objects_to_dest(path_l, dest_dir_path): 
    copy_objects_to_dest(path_l, dest_dir_path)
    
    for path in path_l:
        delete_if_exists(path)



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
        
        
''' returns T/F if 2 paths point to same place '''
def paths_equal(path_1, path_2):
    return os.path.abspath(path_1) == os.path.abspath(path_2)

def get_abs_path_from_rel_path(in_rel_path):
    return os.path.abspath(in_rel_path)
    
def get_basename_from_path(path):
    return ntpath.basename(path)

def get_parent_dir_path_from_path(path):
    return os.path.dirname(path)
    
    
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''
'''                                                                           
        Working
'''
''' VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV '''





''' -- VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV -- All Utilities Standard Footer -- VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV -- '''
sys.modules = og_sys_modules
''' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ '''
if __name__ == '__main__':    
    print('In Main:  file_system_utils')
    dir_path = 'C:\\Users\\mt204e\\Documents\\projects\\Bitbucket_repo_setup\\ip_auto_tests\\ip__auto_test__1'

    delete_all_dir_content_except_given_in_root(dir_path, ['.git', 's.txt'])


#     print(get_parent_dir_path_from_path("C:\\Users\\mt204e\\Documents\\projects\\Bitbucket_repo_setup\\bitbucket_repo_setup_scripts\\submodules\\testing_utils\\util_submodules\\exception_utils\\exception_utils.py"))
#     print(is_file("C:\\Users\\mt204e\\Documents\\projects\\Bitbucket_repo_setup\\bitbucket_repo_setup_scripts\\submodules\\testing_utils\\util_submodules\\exception_utils\\exception_usdfetils.py"))

#     print(os.path.abspath(""))
#     print(get_names_of_files_in_dir("C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools_big_data"))
    
#     print(glob.glob("C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools_big_data" + '/*') )# * means all if need specific format then *.csv)
#     print(paths_equal('ptest.py', "C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools\\ptest.py"))
#     print(rename_file_overwrite('ptest.py', "C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools\\ptest.py"))
    
    
    
    
#     in_dir_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools_big_data\\test_vids"
#     out_parent_dir_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools_big_data\\out_dir"
#     aaa_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools_big_data\\out_dir\\test_vids\\aaa.sss"
#     mkv_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\my_movie_tools_big_data\\test_vids\\Screen_MAKE_SUERE_THIS_WORKS_WITH_SPACE.mkv"
#     l = ['.avi', '.mkv']
#     
#     print(replace_extension(mkv_path, 'mp4'))
#     
# #     print(get_file_extension(mkv_path) in l)
#     
#     
# #     print(get_file_extension(aaa_path))















    print('End of Main:  file_system_utils')
