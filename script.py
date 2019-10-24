import requests
import json
import os
import argparse

from utils import soft_pop

from tqdm import tqdm 

class NotDownloadedError(Exception):
    pass

def split_bar_code(code) :
    """
     Split a bar code with appropriate '/'
       @ input  : code {string} "3228857000852"
       @ output : {string} "322/885/700/0852"
    """
    return( "/".join([code[0:3], code[3:6], code[6:9], code[9:]]))
    
def get_nutrients_prediction(code):
    """
     Return the nutrients prediction of a product using Robotoff API
       @ input  : code {string} "3228857000852"
       @ output : {dictionnary} nutrients prediction
    """
    product_info = requests.get("https://world.openfoodfacts.org/api/v0/product/"+str(code)+".json").json()
    imgid = product_info["product"]["images"]["nutrition_fr"]["imgid"]  
    ocr_url = "https://static.openfoodfacts.org/images/products/" + split_bar_code(str(code)) + "/" + str(imgid) + ".json"
    param = {"ocr_url" : ocr_url}
    nutrients = requests.get("https://robotoff.openfoodfacts.org/api/v1/predict/nutrient", params = param).json()
        
    if nutrients == {'error': 'download_error', 'error_description': 'an error occurred during OCR JSON download'} :
        raise NotDownloadedError("Download error : an error occurred during OCR JSON download")
    else :
        return(nutrients)
        
def compare(dic1, dic2, marge_erreur = 0.1) :
    """
     Compare nutrients value inputed by a user with nutrients prediction
       @ input  : dic1 {dictionnary} nutrients predicted by Robotoff
                  dic2 {dictionnary} nutrients inputed by a user
                  marge_erreur {int, float} (optionnal) tolerance range for the prediction, in portion of user inputed value
       @ output : {dictionnary} Evaluation of every nutrient prediction with format { nutrient : (1 if prediction is correct, 0 if prediction is incorrect, -1 if we are lacking prediction or user input) }
    """
    dic = {}
    
    try :
        dic["energy"] = int(dic2["energy_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["energy"][0]["value"]) <= dic2["energy_100g"]*(1+marge_erreur))
    except KeyError :
        dic["energy"] = -1
     
    try :
        dic["protein"] = int(dic2["proteins_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["protein"][0]["value"]) <= dic2["proteins_100g"]*(1+marge_erreur))
    except KeyError :
        dic["protein"] = -1
        
    try : 
        dic["carbohydrate"] = int(dic2["carbohydrates_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["carbohydrate"][0]["value"]) <= dic2["carbohydrates_100g"]*(1+marge_erreur))
    except KeyError :
        dic["carbohydrate"] = -1  
        
    try : 
        dic["sugar"] = int(dic2["sugars_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["sugar"][0]["value"]) <= dic2["sugars_100g"]*(1+marge_erreur))
    except KeyError :
        dic["sugar"] = -1
        
    try : 
        dic["salt"] = int(dic2["sodium_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["salt"][0]["value"]) <= dic2["sodium_100g"]*(1+marge_erreur))
    except KeyError :
        dic["salt"] = -1
        
    try : 
        dic["fat"] = int(dic2["fat_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["fat"][0]["value"]) <= dic2["fat_100g"]*(1+marge_erreur))
    except KeyError :
        dic["fat"] = -1
        
    try : 
        dic["saturated_fat"] = int(dic2["saturated-fat_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["saturated_fat"][0]["value"]) <= dic2["saturated-fat_100g"]*(1+marge_erreur))
    except KeyError :
        dic["saturated_fat"] = -1
        
    try : 
        dic["fiber"] = int(dic2["fiber_100g"]*(1-marge_erreur) <= float(dic1["nutrients"]["fiber"][0]["value"]) <= dic2["fiber_100g"]*(1+marge_erreur))
    except KeyError :
        dic["fiber"] = -1
        
    return dic
    
def format_prediction(dic1):
    return([soft_pop(dic1["nutrients"], "energy", [{"value":-1}])[0]["value"], soft_pop(dic1["nutrients"], "protein", [{"value":-1}])[0]["value"], \
            soft_pop(dic1["nutrients"], "carbohydrate", [{"value":-1}])[0]["value"], soft_pop(dic1["nutrients"], "sugar", [{"value":-1}])[0]["value"], \
            soft_pop(dic1["nutrients"], "salt", [{"value":-1}])[0]["value"], soft_pop(dic1["nutrients"], "fat", [{"value":-1}])[0]["value"], \
            soft_pop(dic1["nutrients"], "saturated_fat", [{"value":-1}])[0]["value"], soft_pop(dic1["nutrients"], "fiber", [{"value":-1}])[0]["value"]])

def format_user_input(dic2) :
    return([soft_pop(dic2, "energy_100g", -1), soft_pop(dic2, "proteins_100g", -1), \
            soft_pop(dic2, "carbohydrates_100g", -1), soft_pop(dic2, "sugars_100g", -1), \
            soft_pop(dic2, "sodium_100g", -1), soft_pop(dic2, "fat_100g", -1), \
            soft_pop(dic2, "saturated-fat_100g", -1), soft_pop(dic2, "fiber_100g", -1)])
        
if __name__ == "__main__" :
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required = True)
    parser.add_argument("--verbose")
    args = parser.parse_args()
    arguments = args.__dict__
    
    data_dir = arguments.pop("data_dir")
    if data_dir[-1] != "/" :
        data_dir += "/"
    #verbose = arguments.pop("verbose")
    
    
    # list all product ids (ie bar code) in the data_dir
    product_ids = []
    for r, d, f in os.walk(data_dir) :
        for file in f :
            if file[-16:] == ".nutriments.json" :
                product_ids.append(file[:-16])
                
    # perform comparison for every product and write down results in result.csv file
    nutriments_list = ["energy", "protein", "carbohydrate", "sugar", "salt", "fat", "saturated_fat", "fiber"]
    with open("result.csv", "w") as result :
        result.write(";".join(["code"]+nutriments_list+[nutriment+"_predicted" for nutriment in nutriments_list])+"\n")
        for index in tqdm(range(len(product_ids))) :
            val = product_ids[index]
            try :
                dic1 = get_nutrients_prediction(val)
                with open(data_dir + val + ".nutriments.json") as f :
                    dic2 = json.load(f)
                result.write(";".join([str(val)]+[str(val) for val in format_user_input(dic2)]+[str(val) for val in format_prediction(dic1)])+"\n")
            except NotDownloadedError :
                pass                
            except json.decoder.JSONDecodeError :
                pass

