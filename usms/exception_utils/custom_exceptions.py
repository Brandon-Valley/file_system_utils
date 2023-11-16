# use when you have a function that has a set of incompatible 
# parameter options you would like to protect against
class ForbiddenParamValComboError(Exception): pass
class ParamKeyNotInWhitelistError(Exception): pass
class PathExtensionNotInWhitelistError(Exception): pass
class DirNotExistError(Exception): pass
class FileNotExistError(Exception): pass
class FsuObjNotExistError(Exception): pass
class PathNotAbsError(Exception): pass
class Not__File__Error(Exception): pass
class ParamTypeNotInWhitelistError(Exception): pass