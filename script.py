import requests
import json
import os
import time

from tqdm import tqdm 

class NotDownloadedError(Exception):
    pass

def split_bar_code(code) :
    return( "/".join([code[0:3], code[3:6], code[6:9], code[9:]]))
    
def get_ocr_cleaned(product_id):
    
    im_num = 1
    nutrients = {"nutrients": {}}
    
    while nutrients == {"nutrients": {}} :
        ocr_url = "https://static.openfoodfacts.org/images/products/" + split_bar_code(str(product_id)) + "/" + str(im_num) + ".json"
        param = {"ocr_url" : ocr_url}
        nutrients = requests.get("https://robotoff.openfoodfacts.org/api/v1/predict/nutrient", params = param).json()
        im_num += 1
        
    if nutrients == {'error': 'download_error', 'error_description': 'an error occurred during OCR JSON download'} :
        raise NotDownloadedError("Download error : an error occurred during OCR JSON download")
    else :
        return(nutrients)
        
def compare(dic1, dic2, marge_erreur = 0.1) :
    
    dic = {}
    
    try :
        dic["energy"] = dic2["energy_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["energy"][0]["value"]) <= dic2["energy_100g"]*(1+marge_erreur)
    except KeyError :
        dic["energy"] = None
        
    try :
        dic["protein"] = dic2["proteins_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["protein"][0]["value"]) <= dic2["proteins_100g"]*(1+marge_erreur)
    except KeyError :
        dic["protein"] = None
        
    try : 
        dic["carbohydrate"] = dic2["carbohydrates_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["carbohydrate"][0]["value"]) <= dic2["carbohydrates_100g"]*(1+marge_erreur)
    except KeyError :
        dic["carbohydrate"] = None   
        
    try : 
        dic["sugar"] = dic2["sugars_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["sugar"][0]["value"]) <= dic2["sugars_100g"]*(1+marge_erreur)
    except KeyError :
        dic["sugar"] = None
        
    try : 
        dic["salt"] = dic2["sodium_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["salt"][0]["value"]) <= dic2["sodium_100g"]*(1+marge_erreur)
    except KeyError :
        dic["salt"] = None
        
    try : 
        dic["fat"] = dic2["fat_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["fat"][0]["value"]) <= dic2["fat_100g"]*(1+marge_erreur)
    except KeyError :
        dic["fat"] = None
        
    try : 
        dic["saturated_fat"] = dic2["saturated-fat_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["trans_fat"][0]["value"]) <= dic2["saturated-fat_100g"]*(1+marge_erreur)
    except KeyError :
        dic["saturated_fat"] = None
        
    try : 
        dic["fiber"] = dic2["fiber_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["fiber"][0]["value"]) <= dic2["fiber_100g"]*(1+marge_erreur)
    except KeyError :
        dic["fiber"] = None
        
    return dic

def score_1 (dic) :
    if not dic.keys():
        raise ValueError("Applying score_1 on empty dictionnary")
    for key in dic :
        if dic[key]==False  :
            return 0
    return 1

def score_2 (dic) :
    if not dic.keys():
        raise ValueError("Applying score_2 on empty dictionnary")
    asint = [int(dic[key]) for key in dic if dic[key] is not None]
    try :
        return(round(sum(asint)/len(asint), 2))
    except ZeroDivisionError :
        return 0
            
        
        
if __name__ == "__main__" :
    
    product_ids = []
    
    for r, d, f in os.walk("./nutrition-lc-fr-country-fr-last-edit-date-2019-08/") :
        for file in f :
            if file[-16:] == ".nutriments.json" :
                product_ids.append(file[:-16])
                
    with open("result.csv", "a") as result :
        for index in tqdm(range(len(product_ids))) :
            val = product_ids[index]
            try :
                dic1 = get_ocr_cleaned(val)
                with open("./nutrition-lc-fr-country-fr-last-edit-date-2019-08/" + val + ".nutriments.json") as f :
                    dic2 = json.load(f)
                #print(split_bar_code(val))
                #print(dic1)
                #print(dic2)
                dic = compare(dic1, dic2)
                #print(dic)
                #print(score_1(dic), score_2(dic))
                result.write(";".join([str(val), str(len([key for key in dic if dic[key] is not None])), str(score_1(dic)), str(score_2(dic))])+"\n")
                
                """
                usefull to track missing nutrients
                
                dic1["nutrients"].pop("fat", None)
                dic1["nutrients"].pop("saturated_fat", None)
                dic1["nutrients"].pop("energy", None)
                dic1["nutrients"].pop("sugar", None)
                dic1["nutrients"].pop("salt", None)
                dic1["nutrients"].pop("carbohydrate", None)
                dic1["nutrients"].pop("protein", None)
                dic1["nutrients"].pop("fiber", None)
                
                if len(dic1["nutrients"].keys()) != 0 :
                    #print(dic1)
                    raise KeyError("missing nutrient")
                #print("\n")
                """

                
            except NotDownloadedError :
                result.write(str(val)+";;;\n")
            
            #if index%100 == 0 :
            #    time.sleep(1)

