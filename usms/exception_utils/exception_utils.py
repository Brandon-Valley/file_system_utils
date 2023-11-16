if __name__ == "__main__": 
    import        custom_exceptions as ce 
    import        util_tools__eu    as ut
else:
    from . import custom_exceptions as ce
    from . import util_tools__eu    as ut
        


def error_if_param_type_not_in_whitelist(param, param_type_whitelist, custom_msg = None):
    type_str = str(type(param)).split("'")[1]
    if type_str not in param_type_whitelist:
                    
        default_msg = "ERROR:  Invalid Param Type:  " + str(param) + " is type: " + str(type(param)) + ", must be one of: " + str(param_type_whitelist)            
        msg = ut.get_msg(custom_msg, default_msg)
            
        raise ce.ParamTypeNotInWhitelistError(msg)



def error_if_param_key_not_in_whitelist(param, param_key_whitelist, custom_msg = None):
    if param not in param_key_whitelist:
        
        default_msg = "ERROR:  Invalid Param:  " + str(param) + ", must be one of: " + str(param_key_whitelist)        
        msg = ut.get_msg(custom_msg, default_msg)
         
        raise ce.ParamKeyNotInWhitelistError(msg)   
    

def error_if_path_ext_not_in_whitelist(path, path_ext_whitelist, custom_msg = None):
    '''
        ex:  path_ext_whitelist = [".git", ".png", ...]   
        will treat no extension the same as a wrong extension 
    '''
    extension = ut.get_extension(path)
     
    if extension not in path_ext_whitelist:
     
        default_msg = "ERROR:  Invalid Path Extension:  " + str(path) + ", must end with one of: " + str(path_ext_whitelist)        
        msg = ut.get_msg(custom_msg, default_msg)
        
        raise ce.PathExtensionNotInWhitelistError(msg)
    
    
def error_if_not_is_dir(path, custom_msg = None):
    '''
        No need to check for type
    '''
    if not ut.is_dir(path):
        
        default_msg = 'ERROR:  Directory Does Not Exist:  "' + str(path) + '" must point to an existing directory.'        
        msg = ut.get_msg(custom_msg, default_msg)
         
        raise ce.DirNotExistError(msg)     
    
    
def error_if_not_is_file(path, custom_msg = None):
    '''
        No need to check for type
    '''    
    if not ut.is_file(path):
        
        default_msg = 'ERROR:  File Does Not Exist:  "' + str(path) + '" must point to an existing file.'        
        msg = ut.get_msg(custom_msg, default_msg)
         
        raise ce.FileNotExistError(msg)    
    

def error_if_not_is_file_or_is_dir(path, custom_msg = None):
    '''
        No need to check for type
    '''
    if not (ut.exists(path)):
        
        default_msg = 'ERROR:  FSU Object Does Not Exist:  "' + str(path) + '" must point to an existing file or directory."'        
        msg = ut.get_msg(custom_msg, default_msg)
         
        raise ce.FsuObjNotExistError(msg)      
    
    
def error_if_not_is_abs(path, custom_msg = None):
    '''
        Path does not need to exist, just needs to be abs
    '''
    
    if not ut.is_abs(path):
        default_msg = 'ERROR:  Path is Not ABS:  "' + str(path) + '" does not need to exist, but it does need to be an absolute path."'        
        msg = ut.get_msg(custom_msg, default_msg)
         
        raise ce.PathNotAbsError(msg)     


def error_if_not__file__(path):
    error_if_not_is_file              (path,          custom_msg = "ERROR: Can't be __file__ Because File Does Not Exist:  " + '"' + str(path) + '" must point to an existing file.')
    error_if_path_ext_not_in_whitelist(path, ['.py'], custom_msg = "ERROR: Can't be __file__ Because Invalid Path Extension:  " + str(path) + ", must end with .py")  
    error_if_not_is_abs               (path,          custom_msg = "ERROR: Can't be __file__ Because Path is Not ABS:  " + '"' + str(path) + '" needs to be an absolute path."')
         
     
     
     
     
# raises exception if all keys == their values in param_combo_d    
# {log_file_path : None, print_output : False}
def error_if_forbidden_param_val_combo(param_combo_d, reason = None, custom_msg = None):
    raise_error = True
     
    for param, value in param_combo_d.items():
        if param != value:
            raise_error = False
            break
         
    if raise_error:
        if custom_msg == None:
            msg = 'Param Combo Forbidden.'
                 
            if reason != None:
                msg += '\nForbidden Because:  ' + reason
        else:
            msg = custom_msg
        raise ce.ForbiddenParamValComboError(msg)





if __name__ == '__main__':
    print('In Main:  exception_utils')
#     error_if_not_is_file(44)
    error_if_not_is_abs("C:\\Users\\mt204e\\Documents\\projects\\Bitbucket_repo_setup\\version_control_scripts\\CE\\submodules\\exception_utils\\custom_exceptfions.py")
#     error_if_not_is_abs("custom_exceptions.py")
    print('End of Main:  exception_utils')