from __future__ import division, print_function, absolute_import

from nnmnkwii.io import hts
from nnmnkwii.frontend import merlin as fe

from os.path import dirname, join
import numpy as np

DATA_DIR = join(dirname(__file__), "data")


def test_silence_frame_removal_given_hts_labels():
    qs_file_name = join(DATA_DIR, "questions-radio_dnn_416.hed")
    binary_dict, continuous_dict = hts.load_question_set(qs_file_name)

    input_state_label = join(DATA_DIR, "label_state_align", "arctic_a0001.lab")
    labels = hts.load(input_state_label)
    features = fe.linguistic_features(labels,
                                      binary_dict,
                                      continuous_dict,
                                      add_frame_features=True,
                                      subphone_features="full"
                                      )

    # Remove silence frames
    indices = labels.silence_frame_indices()
    features = np.delete(features, indices, axis=0)

    y = np.fromfile(join(DATA_DIR, "nn_no_silence_lab_425", "arctic_a0001.lab"),
                    dtype=np.float32).reshape(-1, features.shape[-1])
    assert features.shape == y.shape
    assert np.allclose(features, y)


# Make sure we can get same results with Merlin
def test_linguistic_and_duration_features_for_duration_model():
    qs_file_name = join(DATA_DIR, "questions-radio_dnn_416.hed")
    binary_dict, continuous_dict = hts.load_question_set(qs_file_name)

    # Phone-level linguistic features
    # Linguistic features
    input_state_label = join(DATA_DIR, "label_state_align", "arctic_a0001.lab")
    labels = hts.load(input_state_label)
    assert labels.is_state_alignment_label()
    x = fe.linguistic_features(labels,
                               binary_dict,
                               continuous_dict,
                               add_frame_features=False,
                               subphone_features=None
                               )
    y = np.fromfile(join(DATA_DIR, "binary_label_416",
                         "arctic_a0001.lab"), dtype=np.float32).reshape(-1, x.shape[-1])
    assert np.allclose(x, y)

    # Duration features
    labels = hts.load(input_state_label)
    x = fe.duration_features(labels, feature_type="numerical", unit_size="state",
                             feature_size="phoneme")
    y = np.fromfile(join(DATA_DIR, "duration_untrimmed",
                         "arctic_a0001.dur"), dtype=np.float32).reshape(-1, x.shape[-1])

    assert np.allclose(x, y)


def test_linguistic_features_for_acoustic_model():
    qs_file_name = join(DATA_DIR, "questions-radio_dnn_416.hed")
    binary_dict, continuous_dict = hts.load_question_set(qs_file_name)

    # Linguistic features
    # To train acoustic model paired with linguistic features,
    # we need frame-level linguistic feature representation.
    input_state_label = join(DATA_DIR, "label_state_align", "arctic_a0001.lab")
    labels = hts.load(input_state_label)
    assert labels.is_state_alignment_label()
    x = fe.linguistic_features(labels,
                               binary_dict,
                               continuous_dict,
                               add_frame_features=True,
                               subphone_features="full"
                               )
    y = np.fromfile(join(DATA_DIR, "binary_label_425",
                         "arctic_a0001.lab"), dtype=np.float32).reshape(-1, x.shape[-1])
    assert np.allclose(x, y)


def test_phone_alignment_label():
    qs_file_name = join(DATA_DIR, "questions-radio_dnn_416.hed")
    binary_dict, continuous_dict = hts.load_question_set(qs_file_name)

    input_state_label = join(DATA_DIR, "label_phone_align", "arctic_a0001.lab")
    labels = hts.load(input_state_label)
    x = fe.linguistic_features(labels, binary_dict, continuous_dict,
                               add_frame_features=False,
                               subphone_features=None)
    assert not labels.is_state_alignment_label()
    assert np.all(np.isfinite(x))
