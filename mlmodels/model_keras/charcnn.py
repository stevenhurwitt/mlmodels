# coding: utf-8
"""
Generic template for new model.
Check parameters template in models_config.json

"model_pars":   { "learning_rate": 0.001, "num_layers": 1, "size": 6, "size_layer": 128, "output_size": 6, "timestep": 4, "epoch": 2 },
"data_pars":    { "data_path": "dataset/GOOG-year.csv", "data_type": "pandas", "size": [0, 0, 6], "output_size": [0, 6] },
"compute_pars": { "distributed": "mpi", "epoch": 10 },
"out_pars":     { "out_path": "dataset/", "data_type": "pandas", "size": [0, 0, 6], "output_size": [0, 6] }



"""
import os
from keras.callbacks import EarlyStopping



######## Logs
from mlmodels.util import os_package_root_path, log



#### Import EXISTING model and re-map to mlmodels
from mlmodels.model_keras.raw.char_cnn.data_utils import Data
from mlmodels.model_keras.raw.char_cnn.models.char_cnn_kim import CharCNNKim


from mlmodels.util import path_norm
print( path_norm("dataset") )


####################################################################################################

VERBOSE = False

MODEL_URI = os.path.dirname(os.path.abspath(__file__)).split("\\")[-1] + "." + os.path.basename(__file__).replace(".py",
                                                                                                                  "")


####################################################################################################
class Model:
    def __init__(self, model_pars=None, data_pars=None, compute_pars=None
                 ):
        ### Model Structure        ################################
        if model_pars is None :
            self.model = None

        else :
            self.model = CharCNNKim(input_size=data_pars["input_size"],
                                alphabet_size          = data_pars["alphabet_size"],
                                embedding_size         = model_pars["embedding_size"],
                                conv_layers            = model_pars["conv_layers"],
                                fully_connected_layers = model_pars["fully_connected_layers"],
                                num_of_classes         = data_pars["num_of_classes"],
                                dropout_p              = model_pars["dropout_p"],
                                optimizer              = model_pars["optimizer"],
                                loss                   = model_pars["loss"]).model


def fit(model, data_pars={}, compute_pars={}, out_pars={}, **kw):
    """
    """

    batch_size = compute_pars['batch_size']
    epochs = compute_pars['epochs']

    sess = None  #
    Xtrain, Xtest, ytrain, ytest = get_dataset(data_pars)

    early_stopping = EarlyStopping(monitor='val_acc', patience=3, mode='max')
    model.model.fit(Xtrain, ytrain,
                                  batch_size=batch_size,
                                  epochs=epochs,
                                  callbacks=[early_stopping],
                                  validation_data=(Xtest, ytest))

    return model, sess


def fit_metrics(model, data_pars={}, compute_pars={}, out_pars={}, **kw):
    """
       Return metrics ofw the model when fitted.
    """
    ddict = {}

    return ddict


def predict(model, sess=None, data_pars={}, out_pars={}, compute_pars={}, **kw):
    ##### Get Data ###############################################
    data_pars['train'] = False
    Xpred, ypred = get_dataset(data_pars)

    #### Do prediction
    ypred = model.model.predict(Xpred)

    ### Save Results

    ### Return val
    if compute_pars.get("return_pred_not") is  None:
        return ypred


def reset_model():
    pass


def save(model=None, session=None, save_pars={}):
    from mlmodels.util import save_keras
    print(save_pars)
    save_keras(session, save_pars['path'])


def load(load_pars={}):
    from mlmodels.util import load_keras
    print(load_pars)
    model0 = load_keras(load_pars['path'])

    model = Model()
    model.model = model0
    session = None
    return model, session


####################################################################################################
def get_dataset(data_pars=None, **kw):
    """
      JSON data_pars to get dataset
      "data_pars":    { "data_path": "dataset/GOOG-year.csv", "data_type": "pandas",
      "size": [0, 0, 6], "output_size": [0, 6] },
    """
    from mlmodels.util import path_norm
    
    if data_pars['train']:

        print('Loading data...')
        train_data = Data(data_source= path_norm( data_pars["train_data_source"]) ,
                             alphabet       = data_pars["alphabet"],
                             input_size     = data_pars["input_size"],
                             num_of_classes = data_pars["num_of_classes"])
        train_data.load_data()
        train_inputs, train_labels = train_data.get_all_data()


        # Load val data
        val_data = Data(data_source = path_norm( data_pars["val_data_source"]) ,
                               alphabet=data_pars["alphabet"],
                               input_size=data_pars["input_size"],
                               num_of_classes=data_pars["num_of_classes"])
        val_data.load_data()
        val_inputs, val_labels = val_data.get_all_data()

        return train_inputs, val_inputs, train_labels, val_labels


    else:
        val_data = Data(data_source = path_norm( data_pars["val_data_source"]) ,
                               alphabet=data_pars["alphabet"],
                               input_size=data_pars["input_size"],
                               num_of_classes=data_pars["num_of_classes"])
        val_data.load_data()
        Xtest, ytest = val_data.get_all_data()
        return Xtest, ytest


def get_params(param_pars={}, **kw):
    import json
    pp = param_pars
    choice = pp['choice']
    config_mode = pp['config_mode']
    data_path = pp['data_path']


    if choice == "json":
        from mlmodels.util import path_norm
        data_path = path_norm(data_path)
        cf = json.load(open(data_path, mode='r'))
        cf = cf[config_mode]
        return cf['model_pars'], cf['data_pars'], cf['compute_pars'], cf['out_pars']


    if choice == "test01":
        from mlmodels.util import  path_norm
        log("#### Path params   ##########################################")
        data_path  = path_norm( "dataset/text/imdb.csv"  )   
        out_path   = path_norm( "/ztest/model_keras/charcnn/" )   
        model_path = os.path.join(out_path , "model")


        data_pars = {"path": data_path, "train": 1, "maxlen": 400, "max_features": 10, }

        model_pars = {"maxlen": 400, "max_features": 10, "embedding_dims": 50,
                      }
        compute_pars = {"engine": "adam", "loss": "binary_crossentropy", "metrics": ["accuracy"],
                        "batch_size": 32, "epochs": 1
                        }

        out_pars = {"path": out_path, "model_path": model_path}

        return model_pars, data_pars, compute_pars, out_pars

    else:
        raise Exception(f"Not support choice {choice} yet")


################################################################################################
########## Tests are  ##########################################################################
def test(data_path="dataset/", pars_choice="json", config_mode="test"):
    ### Local test
    from mlmodels.util import path_norm
    data_path = path_norm(data_path)

    log("#### Loading params   ##############################################")
    param_pars = {"choice": pars_choice, "data_path": data_path, "config_mode": config_mode}
    model_pars, data_pars, compute_pars, out_pars = get_params(param_pars)

    log("#### Loading daaset   #############################################")
    Xtuple = get_dataset(data_pars)

    log("#### Model init, fit   #############################################")
    session = None
    model = Model(model_pars, data_pars, compute_pars)
    model, session = fit(model, data_pars, compute_pars, out_pars)

 
    log("#### Predict   #####################################################")
    data_pars["train"] = 0
    ypred = predict(model, session, data_pars, compute_pars, out_pars)

    log("#### metrics   #####################################################")
    metrics_val = fit_metrics(model, data_pars, compute_pars, out_pars)
    print(metrics_val)

    log("#### Plot   ########################################################")

    log("#### Save/Load   ###################################################")
    save(model, session, save_pars=out_pars)
    model2 = load(out_pars)
    #     ypred = predict(model2, data_pars, compute_pars, out_pars)
    #     metrics_val = metrics(model2, ypred, data_pars, compute_pars, out_pars)
    print(model2)



if __name__ == '__main__':
    VERBOSE = True
    test_path = os.getcwd() + "/mytest/"
    root_path = os_package_root_path(__file__,1)

    ### Local fixed params
    test(pars_choice="test01")

    ### Local json file
    test(pars_choice="json", data_path= f"{root_path}/model_keras/charcnn.json")

    ####    test_module(model_uri="model_xxxx/yyyy.py", param_pars=None)
    from mlmodels.models import test_module

    param_pars = {'choice': "json", 'config_mode': 'test', 'data_path': "model_keras/charcnn.json"}
    test_module(model_uri=MODEL_URI, param_pars=param_pars)

    ##### get of get_params
    # choice      = pp['choice']
    # config_mode = pp['config_mode']
    # data_path   = pp['data_path']

    ####    test_api(model_uri="model_xxxx/yyyy.py", param_pars=None)
    from mlmodels.models import test_api

    param_pars = {'choice': "json", 'config_mode': 'test', 'data_path': "model_keras/charcnn.json"}
    test_api(model_uri=MODEL_URI, param_pars=param_pars)


