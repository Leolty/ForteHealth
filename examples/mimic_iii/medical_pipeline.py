import sys
from termcolor import colored

from forte.data.data_pack import DataPack
from forte.data.readers import StringReader
from forte.pipeline import Pipeline
from forte.processors.writers import PackIdJsonPackWriter
from ftx.onto.clinical import MedicalEntityMention
from ftx.medical.clinical_ontology import NegationContext

from ft.onto.base_ontology import (
    Token,
    Sentence,
    EntityMention,
)
from fortex.spacy import SpacyProcessor

from forte_medical.readers.mimic3_note_reader import Mimic3DischargeNoteReader
from forte_medical.processors.negation_context_analyzer import NegationContextAnalyzer


def main(input_path: str, output_path: str, max_packs: int = -1, singlePack: str = "True"):
    pl = Pipeline[DataPack]()

    if singlePack == "True":
        pl.set_reader(StringReader())
    else:
        pl.set_reader(
            Mimic3DischargeNoteReader(), config={"max_num_notes": max_packs}
        )

    configSpacy = {
        "processors": ["sentence", "tokenize", "pos", "ner", "umls_link"],
        "lang": "en_ner_bionlp13cg_md",
    }

    configNegation = {
        "negation_rules_path": "negex_triggers.txt",
    }

    pl.add(SpacyProcessor(), configSpacy)
    pl.add(NegationContextAnalyzer(), configNegation)

    pl.add(
        PackIdJsonPackWriter(),
        {
            "output_dir": output_path,
            "indent": 2,
            "overwrite": True,
            "drop_record": True,
            "zip_pack": True,
        },
    )

    pl.initialize()

    text = (
        "ADDENDUM:"
        "RADIOLOGIC STUDIES:  Radiologic studies also included a chest "
        "CT, which confirmed cavitary lesions in the left lung apex "
        "consistent with infectious process/tuberculosis.  This also "
        "moderate-sized left pleural effusion. "
        "HEAD CT:  Head CT showed no intracranial hemorrhage and no mass "
        "effect, but old infarction consistent with past medical history. "
        "ABDOMINAL CT:  Abdominal CT showed no lesions of "
        "T10 and sacrum most likely secondary to osteoporosis. These can "
        "be followed by repeat imaging as an outpatient. "
    )

    if singlePack == "True":
        pack = pl.process(text)
        showData(pack)
    else:
        packs = pl.process_dataset(input_path)
        for pack in packs:
            showData(pack)


def showData(pack: DataPack):
    for sentence in pack.get(Sentence):
        sent_text = sentence.text
        print(colored("Sentence:", "red"), sent_text, "\n")

        tokens = [
            (token.text, token.pos) for token in pack.get(Token, sentence)
        ]
        entities = [
            (entity.text, entity.ner_type)
            for entity in pack.get(EntityMention, sentence)
        ]

        medical_entities = []
        for entity in pack.get(MedicalEntityMention, sentence):
            for ent in entity.umls_entities:
                medical_entities.append(ent)

        negation_contexts = [
            (negation_context.text, negation_context.polarity)
            for negation_context in pack.get(NegationContext, sentence)]

        print(colored("Tokens:", "red"), tokens, "\n")
        print(colored("Entity Mentions:", "red"), entities, "\n")
        print(colored("UMLS Entity Mentions detected:", "cyan"), medical_entities, "\n")
        print(colored("Entity Negation Contexts:", "cyan"), negation_contexts, "\n")

        input(colored("Press ENTER to continue...\n", "green"))


main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
