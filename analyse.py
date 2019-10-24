import pandas as pd
import matplotlib.pyplot as plt

def score_1 (dic) :
    """
     Return the score_1 for a given product, i.e. score_1 == 1 if all nutrients predicted are correct, else 0
       @ input  : dic {dictionnary} A dictionnary for a product with format { nutrient : prediction(nutrient)==user_input(nutrient) }
       @ output : {float} score_1 for this product
    """
    if not dic.keys():
        raise ValueError("Applying score_1 on empty dictionnary")
    for key in dic :
        if dic[key]==False  :
            return 0.
    return 1.

def score_2 (dic) :
    """
     Return the score_2 for a given product, i.e. % of nutrients predicted that are correct
       @ input  : dic {dictionnary} A dictionnary for a product with format { nutrient : prediction(nutrient)==user_input(nutrient) }
       @ output : {float} score_2 for this product
    """
    if not dic.keys():
        raise ValueError("Applying score_2 on empty dictionnary")
    asint = [int(dic[key]) for key in dic if dic[key] is not None]
    try :
        return(round(sum(asint)/len(asint), 2))
    except ZeroDivisionError :
        return 0.
            
if __name__ == "__main__" :
    
    nutriments_list = ["energy", "protein", "carbohydrate", "sugar", "salt", "fat", "saturated_fat", "fiber"]
    df = pd.read_csv("result.csv", sep = ";")
    
    fig, axes = plt.subplots(nrows=3, ncols=3)
    for index, nutriment in enumerate(nutriments_list) :
        df[nutriment].value_counts().plot.pie(ax = axes[index//3, index%3])
        
