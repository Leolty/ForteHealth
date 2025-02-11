import time


import yaml
from forte.common.configuration import Config
from forte.data.data_pack import DataPack
from forte.pipeline import Pipeline
from forte.processors.writers import PackIdJsonPackWriter
from fortex.elastic import ElasticSearchPackIndexProcessor
from fortex.huggingface import BioBERTNERPredictor
from fortex.huggingface.transformers_processor import BERTTokenizer

from mimic3_note_reader import Mimic3DischargeNoteReader
from fortex.nltk import NLTKSentenceSegmenter


def main(
    input_path: str, output_path: str, max_packs: int = -1
    ):

    config = yaml.safe_load(open("clinical_config.yml", "r"))
    config = Config(config, default_hparams=None)

    pl = Pipeline[DataPack]()
    pl.set_reader(
        Mimic3DischargeNoteReader(), config={"max_num_notes": max_packs}
    )

    pl.add(NLTKSentenceSegmenter())
    pl.add(BERTTokenizer(), config=config.BERTTokenizer)

    pl.add(BioBERTNERPredictor(), config=config.BioBERTNERPredictor)
    pl.add(
        ElasticSearchPackIndexProcessor(),
        {
            "indexer": {
                "other_kwargs": {"refresh": True},
            }
        },
    )
    pl.add(
        PackIdJsonPackWriter(),
        {
            "output_dir": output_path,
            "indent": 2,
            "overwrite": True,
            "drop_record": True,
            "zip_pack": False,
        },
    )

    pl.initialize()

    for idx, pack in enumerate(pl.process_dataset(input_path)):
        if (idx + 1) % 50 == 0:
            print(f"{time.strftime('%m-%d %H:%M')}: Processed {idx + 1} packs")