

<p align="center">
   <a href="https://github.com/asyml/ForteHealth/actions/workflows/main.yml"><img src="https://github.com/asyml/forte/actions/workflows/main.yml/badge.svg" alt="build"></a>
   <a href="https://codecov.io/gh/asyml/forte"><img src="https://codecov.io/gh/asyml/forte/branch/master/graph/badge.svg" alt="test coverage"></a>
   <a href="https://asyml-forte.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/asyml-forte/badge/?version=latest" alt="documentation"></a>
   <a href="https://github.com/asyml/ForteHealth/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="apache license"></a>
   <a href="https://gitter.im/asyml/community"><img src="http://img.shields.io/badge/gitter.im-asyml/forte-blue.svg" alt="gitter"></a>
   <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="code style: black"></a>
</p>

<p align="center">
  <a href="#installation">Download</a> •
  <a href="#quick-start-guide">Quick Start</a> •
  <a href="#contributing">Contribution Guide</a> •
  <a href="#license">License</a> •
  <a href="https://asyml-forte.readthedocs.io/en/latest">Documentation</a> •
  <a href="https://aclanthology.org/2020.emnlp-demos.26/">Publication</a>
</p>

-----------------


**Bring good software engineering to your Biomedical/Clinical ML solutions, starting from Data!**

**ForteHealth** is a data-centric framework designed to engineer complex ML workflows in the clinical and biomedical domain. ForteHealth allows practitioners to build ML components in a composable and modular way. Behind the scene, it introduces [DataPack](https://asyml-forte.readthedocs.io/en/latest/notebook_tutorial/handling_structued_data.html), a standardized data structure for unstructured data, distilling
good software engineering practices such as reusability, extensibility, and flexibility into ML solutions.

DataPacks are standard data packages in an ML workflow, that can represent the source data (e.g. text, audio, images) and additional markups (e.g. entity mentions, bounding boxes). It is powered by a customizable data schema named "Ontology", allowing domain experts to inject their knowledge into ML engineering processes easily.

## Installation

To install from source:

```bash
git clone https://github.com/asyml/ForteHealth.git
cd ForteHealth
pip install .
```

To install some Forte adapter for some existing [libraries](https://github.com/asyml/forte-wrappers#libraries-and-tools-supported):

Install from PyPI:
```bash
# To install other tools. Check here https://github.com/asyml/forte-wrappers#libraries-and-tools-supported for available tools.
pip install forte.spacy
```

Some components or modules in forte may require some [extra requirements](https://github.com/asyml/forte/blob/master/setup.py#L45):

## Quick Start Guide
Writing biomedical NLP pipelines with ForteHealth is easy. The following example creates a simple pipeline that analyzes the sentences, tokens, and medical named entities from a discharge note.

Before we start, make sure the SpaCy wrapper is installed.
```bash
pip install forte.spacy
```
Let's look at an example of a full fledged medical pipeline:

```python
import sys
import yaml
from fortex.spacy import SpacyProcessor
from mimic3_note_reader import Mimic3DischargeNoteReader
from forte.common.configuration import Config
from forte.data.data_pack import DataPack
from forte.data.readers import PlainTextReader
from forte.pipeline import Pipeline
from ft.onto.base_ontology import Sentence, EntityMention
from ftx.medical.clinical_ontology import NegationContext, MedicalEntityMention
from forte_medical.processors.negation_context_analyzer import (
    NegationContextAnalyzer,
)

max_packs: int = 10
run_ner_pipeline = 0
use_mimic3_reader = False

print("Starting demo pipeline example..")

if run_ner_pipeline == 1:
print("Running NER pipeline...")
pl = Pipeline[DataPack]()
if use_mimic3_reader is False:
        pl.set_reader(PlainTextReader())
    else:
        pl.set_reader(
            Mimic3DischargeNoteReader(), config={"max_num_notes": max_packs}
        )
pl.add(SpacyProcessor(), config={
    processors: ["sentence", "tokenize", "pos", "ner", "umls_link"],
    medical_onto_type: "ftx.medical.clinical_ontology.MedicalEntityMention"
    umls_onto_type: "ftx.medical.clinical_ontology.UMLSConceptLink"
    lang: "en_ner_bc5cdr_md"
    })

pl.add(NegationContextAnalyzer())
pl.initialize()
```

Here we have successfully created a pipeline with a few components:
* a `PlainTextReader` that reads data from text files, given by the `input_path`
* a `SpacyProcessor` that calls SpaCy to split the sentences, create tokenization, 
  pos tagging, NER and umls_linking
* and finally the processor `NegationContextAnalyzer` detects negated contexts

Let's see it run in action!

```python
packs = pl.process_dataset(input_path)
for pack in packs:
    for sentence in pack.get(Sentence):

        medical_entities = []
        for entity in pack.get(MedicalEntityMention, sentence):
            for ent in entity.umls_entities:
                medical_entities.append(ent)

        negation_contexts = [
            (negation_context.text, negation_context.polarity)
            for negation_context in pack.get(NegationContext, sentence)
        ]

        print(
            "UMLS Entity Mentions detected:",
            medical_entities,
            "\n",
        )
        print(
            "Entity Negation Contexts:",
            negation_contexts,
            "\n",
        )
```

We have successfully created a simple pipeline. In the nutshell, the `DataPack`s are
the standard packages "flowing" on the pipeline. They are created by the reader, and
then pass along the pipeline.

Each processor, such as our `NegationContextAnalyzer`,
interfaces directly with `DataPack`s and do not need to worry about the
other part of the pipeline, making the engineering process more modular. 

The above mentioned code snippet has been taken from the [Examples](https://github.com/asyml/ForteHealth/tree/master/examples/mimic_iii) folder.

To learn more about the details, check out of [documentation](https://asyml-forte.readthedocs.io/)!
The classes used in this guide can also be found in this repository or
[the Forte Wrappers repository](https://github.com/asyml/forte-wrappers/tree/main/src/spacy)

## And There's More
The data-centric abstraction of Forte opens the gate to many other opportunities.
Go to [this](https://github.com/asyml/forte#and-theres-more) link for more information

To learn more about these, you can visit:
* [Examples](https://github.com/asyml/forte/tree/master/examples)
* [Documentation](https://asyml-forte.readthedocs.io/)
* Currently we are working on some interesting [tutorials](https://asyml-forte.readthedocs.io/en/latest/index_toc.html), stay tuned for a full set of documentation on how to do NLP with Forte!


## Contributing
This project is part of the [CASL Open Source](http://casl-project.ai/) family.

If you are interested in making enhancement to Forte, please first go over our [Code of Conduct](https://github.com/asyml/ForteHealth/master/CODE_OF_CONDUCT.md) and [Contribution Guideline](https://github.com/asyml/ForteHealth/master/CONTRIBUTING.md)

## About

### Supported By

<p align="center">
   <img src="https://user-images.githubusercontent.com/28021889/165799232-2bb9f819-f394-4ade-98b0-c55c751ec8b1.png", width="180" align="top">
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <img src="https://user-images.githubusercontent.com/28021889/165799272-9e51b864-04f6-432a-92e8-e0f84e091f72.png" width="180" align="top">
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <img src="https://user-images.githubusercontent.com/28021889/165802470-f478de54-6c44-4ec8-8cab-ba74ed1f0163.png" width="180" align="top">
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</p>

![image](https://user-images.githubusercontent.com/28021889/165806563-1542aeac-9656-4ad4-bf9c-f9a2e083f5d8.png)

### License

[Apache License 2.0](https://github.com/asyml/forte/blob/master/LICENSE)
