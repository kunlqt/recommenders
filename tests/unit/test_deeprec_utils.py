# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import pytest
import os
import tensorflow as tf
from reco_utils.recommender.deeprec.deeprec_utils import (
    prepare_hparams,
    download_deeprec_resources,
    load_yaml,
)
from reco_utils.recommender.deeprec.IO.iterator import FFMTextIterator
from reco_utils.recommender.deeprec.IO.dkn_iterator import DKNTextIterator
from reco_utils.recommender.deeprec.IO.sequential_iterator import SequentialIterator
from reco_utils.recommender.deeprec.models.sequential.sli_rec import SLI_RECModel
from reco_utils.dataset.amazon_reviews import download_and_extract, data_preprocessing


@pytest.fixture
def resource_path():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.mark.parametrize(
    "must_exist_attributes", ["FEATURE_COUNT", "data_format", "dim"]
)
@pytest.mark.gpu
@pytest.mark.deeprec
def test_prepare_hparams(must_exist_attributes, resource_path):
    data_path = os.path.join(resource_path, "..", "resources", "deeprec", "xdeepfm")
    yaml_file = os.path.join(data_path, "xDeepFM.yaml")
    if not os.path.exists(yaml_file):
        download_deeprec_resources(
            "https://recodatasets.blob.core.windows.net/deeprec/",
            data_path,
            "xdeepfmresources.zip",
        )
    hparams = prepare_hparams(yaml_file)
    assert hasattr(hparams, must_exist_attributes)


@pytest.mark.gpu
@pytest.mark.deeprec
def test_load_yaml_file(resource_path):
    data_path = os.path.join(resource_path, "..", "resources", "deeprec", "xdeepfm")
    yaml_file = os.path.join(data_path, "xDeepFM.yaml")

    if not os.path.exists(yaml_file):
        download_deeprec_resources(
            "https://recodatasets.blob.core.windows.net/deeprec/",
            data_path,
            "xdeepfmresources.zip",
        )

    config = load_yaml(yaml_file)
    assert config is not None


@pytest.mark.gpu
@pytest.mark.deeprec
def test_FFM_iterator(resource_path):
    data_path = os.path.join(resource_path, "..", "resources", "deeprec", "xdeepfm")
    yaml_file = os.path.join(data_path, "xDeepFM.yaml")
    data_file = os.path.join(data_path, "sample_FFM_data.txt")

    if not os.path.exists(yaml_file):
        download_deeprec_resources(
            "https://recodatasets.blob.core.windows.net/deeprec/",
            data_path,
            "xdeepfmresources.zip",
        )

    hparams = prepare_hparams(yaml_file)
    iterator = FFMTextIterator(hparams, tf.Graph())
    assert iterator is not None
    for res in iterator.load_data_from_file(data_file):
        assert isinstance(res, dict)


@pytest.mark.gpu
@pytest.mark.deeprec
def test_DKN_iterator(resource_path):
    data_path = os.path.join(resource_path, "..", "resources", "deeprec", "dkn")
    data_file = os.path.join(data_path, "final_test_with_entity.txt")
    yaml_file = os.path.join(data_path, "dkn.yaml")
    if not os.path.exists(yaml_file):
        download_deeprec_resources(
            "https://recodatasets.blob.core.windows.net/deeprec/",
            data_path,
            "dknresources.zip",
        )

    hparams = prepare_hparams(yaml_file, wordEmb_file="", entityEmb_file="")
    iterator = DKNTextIterator(hparams, tf.Graph())
    assert iterator is not None
    for res in iterator.load_data_from_file(data_file):
        assert isinstance(res, dict)


@pytest.mark.gpu
@pytest.mark.deeprec
@pytest.mark.sequential
def test_Sequential_Iterator(resource_path):
    data_path = os.path.join(resource_path, "..", "resources", "deeprec", "slirec")
    yaml_file = os.path.join(
        resource_path,
        "..",
        "..",
        "reco_utils",
        "recommender",
        "deeprec",
        "config",
        "sli_rec.yaml",
    )
    train_file = os.path.join(data_path, r"train_data")

    if not os.path.exists(train_file):
        valid_file = os.path.join(data_path, r"valid_data")
        test_file = os.path.join(data_path, r"test_data")
        user_vocab = os.path.join(data_path, r"user_vocab.pkl")
        item_vocab = os.path.join(data_path, r"item_vocab.pkl")
        cate_vocab = os.path.join(data_path, r"category_vocab.pkl")

        reviews_name = "reviews_Movies_and_TV_5.json"
        meta_name = "meta_Movies_and_TV.json"
        reviews_file = os.path.join(data_path, reviews_name)
        meta_file = os.path.join(data_path, meta_name)
        valid_num_ngs = (
            4  # number of negative instances with a positive instance for validation
        )
        test_num_ngs = (
            9  # number of negative instances with a positive instance for testing
        )
        sample_rate = (
            0.01  # sample a small item set for training and testing here for example
        )

        input_files = [
            reviews_file,
            meta_file,
            train_file,
            valid_file,
            test_file,
            user_vocab,
            item_vocab,
            cate_vocab,
        ]
        download_and_extract(reviews_name, reviews_file)
        download_and_extract(meta_name, meta_file)
        data_preprocessing(
            *input_files,
            sample_rate=sample_rate,
            valid_num_ngs=valid_num_ngs,
            test_num_ngs=test_num_ngs
        )

    hparams = prepare_hparams(yaml_file)
    iterator = SequentialIterator(hparams, tf.Graph())
    assert iterator is not None
    for res in iterator.load_data_from_file(train_file):
        assert isinstance(res, dict)
