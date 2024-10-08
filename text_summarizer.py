# -*- coding: utf-8 -*-
"""Text_Summarizer

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pq7O3h7d6wQnWikbomcV0KtABfVN5_qf
"""
import accelerate
import sklearn
import py7zr
import sentencepiece
import transformers
import umap
import urllib3
from transformers.data import datasets

# !pip install -U transformers
# !pip install -U accelerate
# !pip install -U datasets
# !pip install -U bertviz
# !pip install -U umap-learn
# !pip install -U sentencepiece
# !pip install -U urllib3
# !pip install py7zr


def load_dataset(param, param1):
    pass


dataset = load_dataset("cnn_dailymail", "3.0.0")

print("hello")

dataset['train']

dataset['train'][1]['article'][:300]

dataset['train'][1]['highlights']

from transformers import pipeline

pipe = pipeline("text-generation", model="gpt2-medium")

dataset['train'][1]['article'][:1000]
input_text = dataset['train'][1]['article'][:2000]

query = input_text + "\nTL;DR:\n"

pipe_out = pipe(query, max_length=512, clean_up_tokenization_spaces=True)

len(input_text)

pipe_out[0]['generated_text']

pipe_out[0]['generated_text'][len(query):]

summaries = {}
summaries['gpt2-medium-380M'] = pipe_out[0]['generated_text'][len(query):]

# Try out T5 Transformers

pipe = pipeline('summarization', model='t5-base')

pipe_out = pipe(input_text)

summaries['t5-base-223M'] = pipe_out[0]['summary_text']

pipe = pipeline('summarization', model='facebook/bart-large-cnn')
pipe_out = pipe(input_text)

summaries['bart-large-cnn-400M'] = pipe_out[0]['summary_text']

# PEGASUS Model

pipe = pipeline('summarization', model='google/pegasus-cnn_dailymail')

pipe_out = pipe(input_text)

summaries['pegasus-cnn-568M'] = pipe_out[0]['summary_text']

for model in summaries:
  print(model.upper())
  print(summaries[model])
  print("")

"""Fine-Tuning Summarization Model on Custom Dataset
https://huggingface.co/datasets/samsum
"""

from datasets import load_dataset
from transformers import pipeline

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

device = 'gpu'
model_ckpt = 'facebook/bart-large-cnn'
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = AutoModelForSeq2SeqLM.from_pretrained(model_ckpt)

samsum = load_dataset('samsum')
samsum

samsum['train'][0]

dialogue_len = [len(x['dialogue'].split()) for x in samsum['train']]
summary_len = [len(x['summary'].split()) for x in samsum['train']]

import pandas as pd

data = pd.DataFrame([dialogue_len, summary_len]).T
data.columns = ['Dialogue Length', 'Summary Length']

data.hist(figsize=(15,5))

# lets build Data Collator

def get_feature(batch):
  encodings = tokenizer(batch['dialogue'], text_target=batch['summary'],
                        max_length=1024, truncation=True)

  encodings = {'input_ids': encodings['input_ids'],
               'attention_mask': encodings['attention_mask'],
               'labels': encodings['labels']}

  return encodings

samsum_pt = samsum.map(get_feature, batched=True)

samsum_pt

columns = ['input_ids', 'labels', 'attention_mask']
samsum_pt.set_format(type='torch', columns=columns)

from transformers import DataCollatorForSeq2Seq
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir = 'bart_samsum',
    num_train_epochs=1,
    warmup_steps = 500,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    weight_decay = 0.01,
    logging_steps = 10,
    evaluation_strategy = 'steps',
    eval_steps=500,
    save_steps=1e6,
    gradient_accumulation_steps=16
)

trainer = Trainer(model=model, args=training_args, tokenizer=tokenizer, data_collator=data_collator,
                  train_dataset = samsum_pt['train'], eval_dataset = samsum_pt['validation'])

trainer.train()

trainer.save_model('bart_samsum_model')

# custome Dialogue Prediction

pipe = pipeline('summarization', model='bart_samsum_model')
gen_kwargs = {'length_penalty': 0.8, 'num_beams': 8, "max_length": 56}

custom_dialogue="""
Laxmi Kant: what work you planning to give Tom?
Juli: i was hoping to send him on a business trip first.
Laxmi Kant: cool. is there any suitable work for him?
Juli: he did excellent in last quarter. i will assign new project, once he is back.
"""
print("Summarized Text is:\n\n")
summary = pipe(custom_dialogue, **gen_kwargs)[0]['summary_text']

# Split the summary into sentences and print each on a new line
formatted_summary = '\n'.join(summary.split('. '))
print(formatted_summary)

# custome Dialogue Prediction

pipe = pipeline('summarization', model='bart_samsum_model')
gen_kwargs = {'length_penalty': 0.8, 'num_beams': 8, "max_length": 88}

custom_dialogue="""
Artificial intelligence (AI) is transforming industries across the globe, revolutionizing how we work,
communicate, and live. From healthcare to finance, AI-driven solutions are enabling businesses to operate
more efficiently, make data-driven decisions, and deliver personalized experiences to their customers.
The rapid advancement of machine learning algorithms and the availability of vast amounts of data have accelerated AI's growth,
allowing it to tackle complex tasks such as natural language processing, image recognition, and predictive analytics.
As AI continues to evolve, it holds the potential to address some of the world's most pressing challenges, ranging from climate change to healthcare disparities.
However, ethical considerations, data privacy, and the need for transparency in AI decision-making processes remain critical issues that must be addressed to ensure
the technology benefits society as a whole.
"""
print("\n\nSummarized Text is:\n\n")
summary = pipe(custom_dialogue, **gen_kwargs)[0]['summary_text']

# Split the summary into sentences and print each on a new line
formatted_summary = '\n'.join(summary.split('. '))
print(formatted_summary)

from transformers import pipeline

# Custom Dialogue Prediction
pipe = pipeline('summarization', model='bart_samsum_model')
gen_kwargs = {'length_penalty': 0.8, 'num_beams': 8, "max_length": 88}

custom_dialogue = """
Artificial intelligence (AI) is transforming industries across the globe, revolutionizing how we work,
communicate, and live. From healthcare to finance, AI-driven solutions are enabling businesses to operate
more efficiently, make data-driven decisions, and deliver personalized experiences to their customers.
The rapid advancement of machine learning algorithms and the availability of vast amounts of data have accelerated AI's growth,
allowing it to tackle complex tasks such as natural language processing, image recognition, and predictive analytics.
As AI continues to evolve, it holds the potential to address some of the world's most pressing challenges, ranging from climate change to healthcare disparities.
However, ethical considerations, data privacy, and the need for transparency in AI decision-making processes remain critical issues that must be addressed to ensure
the technology benefits society as a whole.
"""

print("\n\nSummarized Text is:\n\n")
summary = pipe(custom_dialogue, **gen_kwargs)[0]['summary_text']

# Split the summary into sentences and print each on a new line
formatted_summary = '\n'.join(summary.split('. '))
print(formatted_summary)

from transformers import pipeline

# Custom Dialogue Prediction
pipe = pipeline('summarization', model='bart_samsum_model')
gen_kwargs = {'length_penalty': 0.8, 'num_beams': 8, "max_length": 56}

custom_dialogue = """
The concept of mindfulness has gained popularity in recent years as a tool for enhancing mental well-being.
Originating from ancient Buddhist practices, mindfulness involves paying attention to the present moment without judgment.
Techniques such as meditation and deep-breathing exercises are commonly used to cultivate mindfulness.
Research suggests that regular mindfulness practice can reduce stress, improve focus, and increase emotional resilience.
As more people embrace these practices, various apps and programs have emerged to help individuals integrate mindfulness into their busy lives.
"""
print("\n\nSummarized Text is:\n\n")
summary = pipe(custom_dialogue, **gen_kwargs)[0]['summary_text']

# Split the summary into sentences and print each on a new line
formatted_summary = '\n'.join(summary.split('. '))
print(formatted_summary)

from transformers import pipeline

# Custom Dialogue Prediction
pipe = pipeline('summarization', model='bart_samsum_model')
gen_kwargs = {'length_penalty': 0.8, 'num_beams': 8, "max_length": 56}

custom_dialogue = """
The concept of mindfulness has gained popularity in recent years as a tool for enhancing mental well-being.
Originating from ancient Buddhist practices, mindfulness involves paying attention to the present moment without judgment.
Techniques such as meditation and deep-breathing exercises are commonly used to cultivate mindfulness.
Research suggests that regular mindfulness practice can reduce stress, improve focus, and increase emotional resilience.
As more people embrace these practices, various apps and programs have emerged to help individuals integrate mindfulness into their busy lives.
"""
print("\n\nSummarized Text is:\n\n")
summary = pipe(custom_dialogue, **gen_kwargs)[0]['summary_text']

# Split the summary into sentences and print each on a new line
formatted_summary = '\n'.join(summary.split('. '))
print(formatted_summary)

from transformers import pipeline

# Custom Dialogue Prediction
pipe = pipeline('summarization', model='bart_samsum_model')
gen_kwargs = {'length_penalty': 0.8, 'num_beams': 8, "max_length": 88}

custom_dialogue = """
The history of human civilization is a complex tapestry woven from countless cultures, innovations, and historical events.
From the dawn of agriculture, which began around 10,000 years ago in the Fertile Crescent, to the rise of ancient empires like Mesopotamia, Egypt, and the Indus Valley, humans transitioned from nomadic lifestyles to settled communities.
This shift enabled the development of trade, writing systems, and the establishment of laws, which laid the groundwork for modern societies.
The invention of the wheel and advancements in metallurgy significantly improved transportation and tool-making, further propelling human progress.
Fast forward to classical antiquity, where civilizations such as Greece and Rome made monumental contributions to philosophy, art, and governance.
The Greek philosophers like Socrates, Plato, and Aristotle explored the nature of existence and ethics, while Roman law and engineering have had a lasting impact on Western civilization.
However, this period was also marked by conflicts, including the conquests of Alexander the Great and the expansion of the Roman Empire, which shaped cultural exchanges and the spread of ideas.
As we moved into the Middle Ages, the fall of the Roman Empire in the 5th century led to a fragmentation of power in Europe, giving rise to feudal systems and the influence of the Catholic Church.
The Renaissance, beginning in the 14th century, rekindled interest in classical learning and spurred remarkable advancements in science, literature, and art, exemplified by figures such as Leonardo da Vinci and Michelangelo.
This period paved the way for the Enlightenment, which emphasized reason, individualism, and skepticism of traditional authority.
The Industrial Revolution in the 18th and 19th centuries marked another significant turning point, as technological innovations transformed economies and societies, leading to urbanization and shifts in labor dynamics.
The 20th century witnessed unprecedented global conflict, from the World Wars to the Cold War, shaping international relations and political ideologies.
The latter part of the century saw advancements in civil rights, technological innovations like the internet, and a growing awareness of environmental issues.
Today, we find ourselves in an interconnected world, facing challenges such as climate change, social inequality, and geopolitical tensions, all while navigating the complexities of a rapidly changing technological landscape.
The journey of human civilization is ongoing, marked by both triumphs and trials, and it continues to evolve as we seek solutions to the pressing issues of our time.
"""
print("\n\nSummarized Text is:\n\n")
summary = pipe(custom_dialogue, **gen_kwargs)[0]['summary_text']

# Split the summary into sentences and print each on a new line
formatted_summary = '\n'.join(summary.split('. '))
print(formatted_summary)

# !zip bart_samsum.zip -r bart_samsum_model/

