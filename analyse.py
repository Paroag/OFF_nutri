import pandas as pd
import numpy as np
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
    
def ndiff(row, nutriment) :
    if row[nutriment] == -1 or row[nutriment+"_predicted"]==-1 :
        return None
    else :
        return int(row[nutriment]-row[nutriment+"_predicted"])
            
if __name__ == "__main__" :
    
    nutriments_list = ["energy", "protein", "carbohydrate", "sugar", "salt", "fat", "saturated_fat", "fiber"]
    
    df = pd.read_csv("tmp.csv", sep = ";")#, nrows = 11000)
    """
    for nutriment in nutriments_list :
        df[nutriment+"_diff"] = df.apply(ndiff, nutriment=nutriment, axis = 1)
    """
   
### Error repartition per nutrient    
    
    df_result = pd.DataFrame(index = nutriments_list, columns = ["correct", "incorrect", "not predicted", "not specified"]).fillna(0)

    for index, row in df.iterrows():
        for nutriment in nutriments_list :
            if row[nutriment] == -1 :
                df_result["not specified"][nutriment] += 1
            elif row[nutriment+"_predicted"] == -1:
                df_result["not predicted"][nutriment] += 1
            else :
                if nutriment == "energy" :
                    if abs(row["energy_predicted"] - row[nutriment]) <= 1:
                        df_result["correct"][nutriment] += 1
                    elif abs(row[nutriment+"_predicted"] - row[nutriment]) > 1 :
                        df_result["incorrect"][nutriment] += 1 
                else :                    
                    if row[nutriment+"_predicted"] == row[nutriment] :
                        df_result["correct"][nutriment] += 1
                    elif row[nutriment+"_predicted"] != row[nutriment] :
                        df_result["incorrect"][nutriment] += 1
                
    
    df_result.plot.bar(stacked = True).legend(bbox_to_anchor=(1.35, 1.030))
    
### metrics
    
    for nutriment in df_result.index.tolist():
        print(nutriment + ": Detectabilite : "+str(round((df_result.loc[nutriment].correct+df_result.loc[nutriment].incorrect)/(df_result.loc[nutriment]["not predicted"]+df_result.loc[nutriment].correct+df_result.loc[nutriment].incorrect), 2))+",  Accuracy :"+str(round((df_result.loc[nutriment].correct)/(df_result.loc[nutriment].correct+df_result.loc[nutriment].incorrect), 2)))
    
### totally corrected predicted product
    
    df_2 = pd.DataFrame(index = range(len(nutriments_list), -1, -1), columns = ["prévision correcte", "prévision incorrecte"]).fillna(0)
    for index, row in df.iterrows() :
        state = len(nutriments_list)
        veracity = "prévision correcte"
        for nutriment in nutriments_list :
            if row[nutriment] != -1 and row[nutriment+"_predicted"] == -1 :
                state -= 1
            if row[nutriment+"_predicted"]!= -1 and row[nutriment] != row[nutriment+"_predicted"]:
                veracity = "prévision incorrecte"
        df_2[veracity][state] += 1
    df_2.plot.bar(stacked = True).legend(bbox_to_anchor=(1.00, 1.030))
        
                

### Heatmap for each nutrient
    
    for nutriment in nutriments_list[1:] :
        print(nutriment)
        heatmap = np.zeros([21, 21])
        for index, row in df.iterrows():
            if row[nutriment] != -1 and row[nutriment+"_predicted"]!= -1 :
                if row[nutriment] <= 20 :
                    if row[nutriment] != row[nutriment+"_predicted"] :
                        heatmap[int(row[nutriment])][min(int(row[nutriment+"_predicted"]), 20)] -= 1
        plt.imshow(heatmap, cmap = "hot")
        plt.show()