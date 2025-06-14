import os
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import numpy as np
import json
from parameters import *

def upload_data_trained(path = TRAIN_FILE):
    """Load training data from JSON file."""
    print("Trained data loaded")
    
    train_data = load_json(path)
    
    list = []
    for item in train_data:
        trial = InputExample(texts=[item['text1'], item['text2']],label=float(item['similarity']))
        list.append(trial)
    
    leng = len(list)
    print(f"Loaded - {leng} ")
    return list

def train_modell(trained_data, transformerr = BASE_MODEL):
    """Train sentence transformer model."""
    print(f"Training {transformerr} with new data from the collections retrieved")
    
    model = SentenceTransformer(transformerr)
    
    load_training = DataLoader(trained_data, shuffle=True, batch_size=BATCH)
    
    lost_value = calc_loss(model)
    
    print(f"TRAINING EPOCHS: {EPOCHS}, BATCH SIZE: {BATCH}")
    
    model.fit(train_objectives=[(load_training, lost_value)], epochs=EPOCHS, warmup_steps=int(len(load_training) * 0.1), output_path=MODEL_DIR, show_progress_bar=True)
    
    print("Concluced training!")
    return model

def test_model(model, test_data):
    """Evaluate trained model."""
    print("Testing model")
    
    value_predict = []
    final_value = []
    
    for trial in test_data:
        embeddings = model.encode(trial.texts)
        sim = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        
        value_predict.append(sim)
        final_value.append(trial.label)
    
    value_predict = np.array(value_predict)
    final_value = np.array(final_value)
    
    mse = np.mean((value_predict - final_value) ** 2)
    mae = np.mean(np.abs(value_predict - final_value))
    correlation = np.corrcoef(value_predict, final_value)[0, 1]
    
    metrics = {'mse': float(mse),'mae': float(mae),'correlation': float(correlation)}
    
    print("Evaluation Metrics:")
    print(f"Mean Squared Error (MSE)     -   {metrics['mse']:.3f}")
    print(f"Mean Absolute Error (MAE)    -   {metrics['mae']:.3f}")
    
    return metrics

def save_trained_model(model, model_path = MODEL_DIR):
    """Save trained model."""
    checkfoldr(model_path)
    model.save(model_path)
    print(f"Modelo guardado em: {model_path}")

def load_trained_model(model_path = MODEL_DIR, transformerr = BASE_MODEL):
    """Load trained model or base model."""
    if os.path.exists(model_path):
        model = SentenceTransformer(model_path)
        print(f"Using {model_path}")
    else:
        print(f"Model not found using previous base model")
        model = SentenceTransformer(transformerr)
    
    return model


################################
############# UTILS ###########
################################

def checkfoldr(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_json(path) :
    """Load data from JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def calc_loss(model):
    """Calculate loss for training."""
    result = losses.CosineSimilarityLoss(model)

    return result

##################################
################### MAIN #########
##################################

def main():
    """Main function for model training."""
    trained_data = upload_data_trained()
    
    if not trained_data:
        print("No training examples found")
        return
    
    aux = int(0.8 * len(trained_data))
    train_data = trained_data[:aux]
    test_data = trained_data[aux:]
    
    print(f"Training set size: {len(train_data)} examples")
    print(f"Test set size: {len(test_data)} examples")
    
    model = train_modell(train_data)
    
    if test_data:
        metrics = test_model(model, test_data)
        print("Evaluation Metrics:")
        print(f"Mean Squared Error (MSE)    -  {metrics['mse']:.3f}")
        print(f"Mean Absolute Error (MAE)   -  {metrics['mae']:.3f}")

    save_trained_model(model)
    
    print("Model training completed successfully")

if __name__ == "__main__":
    main()
