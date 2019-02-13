import pytest

pytest_parametrize = pytest.mark.parametrize


def update_locals(input_locals, funcs):
    """Modify input local symbol table"""

    input_locals.update({func.__name__: func for func in funcs})


def common_test(test_cases):
    """Common tests for Operators

    Input pytest parametrization should have 4 input arguments, including
    input_sequence, input_labels, output_sequence, output_labels.

    Additional common tests can be added here as needed.

    Arg:
        test_cases (pytest.param): list of pytest parametrizations

    Return
        funcs : list of parametrized functions.

    E.g.
        common_test(
            [
                pytest.param(
                    ['alvin', '喜歡', '吃', '榴槤'],
                    [1, 2, 3, 4],
                    ['<sos>', 'alvin', '喜歡', '吃', '榴槤', '<eos>'],
                    [0, 1, 2, 3, 4, 0],
                    id='zh',
                ),
            ]
        )

    """
    def test_data(input_sequence, input_labels, output_sequence, output_labels, op):
        assert len(input_sequence) == len(input_labels)
        assert len(output_sequence) == len(output_labels)

    def test_transform(input_sequence, input_labels, output_sequence, output_labels, op):
        output = op.transform(input_sequence)
        assert output_sequence == output[0]

    def test_transform_labels(input_sequence, input_labels, output_sequence, output_labels, op):
        _, label_aligner = op.transform(input_sequence)
        output = label_aligner.transform(input_labels)
        assert output_labels == output

    def test_inverse_transform_labels(
            input_sequence,
            input_labels,
            output_sequence,
            output_labels,
            op,
        ):
        _, label_aligner = op.transform(input_sequence)
        output = label_aligner.inverse_transform(output_labels)
        assert input_labels == output

    argstr = "input_sequence,input_labels,output_sequence,output_labels"
    local_objs = locals()
    funcs = [local_objs[func]
             for func in local_objs if callable(local_objs[func]) and func.startswith('test')]
    return [pytest_parametrize(argstr, test_cases)(f) for f in funcs]
