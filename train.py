from datasets import load_dataset
from sentence_transformers.losses import CosineSimilarityLoss
from setfit import SetFitModel, SetFitTrainer, sample_dataset
from setfit.exporters.onnx import export_onnx
import pickle
import onnxruntime as rt

#https://github.com/huggingface/setfit/tree/main/src/setfit

def retrain_model():
    # Load a dataset from the Hugging Face Hub
    dataset = load_dataset("sst2")

    train_dataset = sample_dataset(dataset["train"],label_column="label", num_samples=8)
    eval_dataset = dataset["validation"]

    # Load a SetFit model from Hub
    model = SetFitModel.from_pretrained("sentence-transformers/paraphrase-mpnet-base-v2")

    # Create trainer
    trainer = SetFitTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        loss_class=CosineSimilarityLoss,
        metric="accuracy",
        batch_size=16,
        num_iterations=20, # The number of text pairs to generate for contrastive learning
        num_epochs=1, # The number of epochs to use for contrastive learning
        column_mapping={"sentence": "text", "label": "label"} # Map dataset columns to text/label expected by trainer
    )

    # Train and evaluate
    trainer.train()
    metrics = trainer.evaluate()
    message = "\nModel sucessfully retrained.\n"
    print("~" * len(message) + "~" * len(message))
    # print(trainer.model.model_head.classes_)
    # print(model.model_head.classes_)
    return model


model = retrain_model()


def save_pickle(model):
    # Pickle
    pkl_filename = "model/setfit_model.pkl"
    with open(pkl_filename, 'wb') as file:
        pickle.dump(model, file)
    message = "\nModel exported to pkl format.\n"
    print("~" * len(message) + message + "~" * len(message))

def save_onnx(model):
    # Export the sklearn based model
    output_path = "model/setfit_model.onnx"
    export_onnx(model.model_body,
                model.model_head,
                opset=12,
                output_path=output_path)
    message = "\nModel exported to onnx format.\n"
    print("~" * len(message) + message + "~" * len(message))


save_pickle(model)
save_onnx(model)
