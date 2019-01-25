# coding: utf8
def main():
    import sys
    if len(sys.argv) != 5:
        # pylint: disable=line-too-long
        print("Should be used as `pytorch_pretrained_bert convert_tf_checkpoint_to_pytorch TF_CHECKPOINT TF_CONFIG PYTORCH_DUMP_OUTPUT`")

if __name__ == '__main__':
    main()
