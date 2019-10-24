def soft_pop(dic: dict, key, default) :
    """
     Return dic[key] if it exists, else default
       @ input  : dic {dictionnary} Dictionnary
                  key {} Potential key
                  default {} Value to return if dic[key] does not exists
       @ output : {} dic[key] if key in dic else default
    """
    try :
        return(dic[key])
    except KeyError :
        return(default)