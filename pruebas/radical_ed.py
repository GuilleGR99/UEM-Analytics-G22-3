#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from transformers import (
    TokenClassificationPipeline,
    SummarizationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,BigBirdPegasusForConditionalGeneration
)
from transformers.pipelines import AggregationStrategy
import numpy as np



# In[ ]:


class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs
        )

    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )
        return np.unique([result.get("word").strip() for result in results])


# In[ ]:


class summary(SummarizationPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(
            model = BigBirdPegasusForConditionalGeneration.from_pretrained("google/bigbird-pegasus-large-arxiv", attention_type="original_full", max_length=50),
            tokenizer = AutoTokenizer.from_pretrained("google/bigbird-pegasus-large-arxiv"),
            *args,
            **kwargs
        )
    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
        )
        res = "none data"
        if len(results) > 0 :
            res = results[0].get("summary_text") 
        return res


# In[ ]:


class keyword_extractor(TokenClassificationPipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained("ml6team/keyphrase-extraction-distilbert-inspec"),
            tokenizer=AutoTokenizer.from_pretrained("ml6team/keyphrase-extraction-distilbert-inspec"),
            *args,
            **kwargs
        )

    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )
        return np.unique([result.get("word").strip() for result in results])

