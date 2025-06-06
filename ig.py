# BERT model with Integrated Gradients (IG)

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import captum

#bert model finetuned on mnli
#swap Adam optimizer with M-FAC
model_name = "M-FAC/bert-tiny-finetuned-mnli" 

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


# 0:entailment, 1:neutral, 2:contradiction
target_label = int(1)

# forward
def forward_func(input_ids, attention_mask):
    input_ids = input_ids.long()
    logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
    probs = torch.nn.functional.softmax(logits, dim=1)
    return probs
    
#take an example
premise = "Your gift is appreciated by each and every student who will benefit from your generosity."
hypothesis = "Hundreds of students will benefit from your generosity."
encoded = tokenizer(premise,hypothesis,
                    return_tensors="pt",
                    truncation=True,
                    max_length=128,
                    padding="max_length")

input_ids = encoded["input_ids"]
attention_mask = encoded["attention_mask"]
baseline_ids  = torch.zeros_like(input_ids).long()

# IntegratedGradients
ig = captum.attr.IntegratedGradients(forward_func)

# attribution
attributions = ig.attribute(
    inputs=input_ids, 
    additional_forward_args=(attention_mask,),
    baselines=baseline_ids,
    return_convergence_delta=False,
    target=target_label)

# token-level IG value
tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
scores = attributions[0].sum(dim=1)
for tok, score in zip(tokens, scores):
    print(f"{tok:>12} : {score.item(): .4f}")
