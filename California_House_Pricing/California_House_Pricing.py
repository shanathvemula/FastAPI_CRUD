import pickle
import numpy as np
import pandas as pd
import os

from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.dirname(__file__))+"\California_House_Pricing"


class CHP(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


def CHP_Prediction(chp: CHP):
    print(type(chp))
    try:
        data = chp.dict()
    except:
        data = chp
    regmodel = pickle.load(open(BASE_DIR+'\\regmodel.pkl', 'rb'))
    scalar = pickle.load(open(BASE_DIR+'\\scaling.pkl', 'rb'))
    new_data = scalar.transform(np.array(list(data.values())).reshape(1, -1))
    output = regmodel.predict(new_data)
    return output[0]
