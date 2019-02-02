import os
from elcato.helpers import calculate_paths, path_relative_to_document


def test_calculate_document_relative_path():
    root = "/home/oly/repos/do-blog/posts/"
    document_path = root + "python/gtk"
    document_image_path = "../../../images/gtk/tut12-listbox.png"

    paths = path_relative_to_document(
        root=root,
        document_location=document_path,
        relative_path=document_image_path,
    )

    assert paths.file_absolute == os.path.abspath(document_path + document_image_path)
    assert paths.relative == "python/gtk"

    root = "/home/oly/repos/do-blog/posts/"
    document_image_path = "../../images/hardware/PN532-PI.png"
    document_path = root + os.sep + "hardware"
    paths = path_relative_to_document(
        root=root,
        document_location=document_path,
        relative_path=document_image_path,
    )

    assert paths.file_absolute == os.path.abspath(document_path + document_image_path)
    assert paths.relative == "hardware"

    root = "/home/oly/repos/do-blog/posts/"
    document_image_path = "./sloe-gin.jpg"
    document_path = root + os.sep + "recipes/fermenting"
    paths = path_relative_to_document(
        root=root,
        document_location=document_path,
        relative_path=document_image_path,
    )

    assert paths.file_absolute == os.path.abspath(document_path + document_image_path)
    assert paths.relative == "recipes/fermenting"


def test_path_calculations():
    root = "/home/oly/repos/do-blog/posts/"
    document_path = root + "python/gtk"
    document_image_path = "../../../images/gtk/tut12-listbox.png"

    paths = calculate_paths(
        source_root=root,
        source_file=document_path,
        source_image=os.path.abspath(
            document_path + "/" + document_image_path
        ),
        destination_root="/tmp",
        destination_folder="/images/",
    )
    assert paths.depth == 2
    assert (
        paths.source_absolute
        == "/home/oly/repos/do-blog/images/gtk/tut12-listbox.png"
    )
    assert paths.destination_relative == "images/python/gtk"
    assert paths.destination_absolute == "/tmp/images/python/gtk"

    root = "/home/oly/repos/do-blog/posts/"
    document_path = root + "hardware"
    document_image_path = "../../images/hardware/PN532-PI.png"
    paths = calculate_paths(
        source_root=root,
        source_file=document_path,
        source_image=os.path.abspath(
            document_path + "/" + document_image_path
        ),
        destination_root="/tmp",
        destination_folder="/images/",
    )
    assert paths.depth == 1
    assert (
        paths.source_absolute
        == "/home/oly/repos/do-blog/images/hardware/PN532-PI.png"
    )
    assert paths.destination_relative == "images/hardware"
    assert paths.destination_absolute == "/tmp/images/hardware"



    root = "/home/oly/repos/do-blog/posts/"
    document_path = root + "recipes/fermenting"
    document_image_path = "./sloe-gin.jpg"
    paths = calculate_paths(
        source_root=root,
        source_file=document_path,
        source_image=os.path.abspath(
            document_path + "/" + document_image_path
        ),
        destination_root="/tmp",
        destination_folder="/images/",
    )
    assert paths.depth == 2
    assert (
        paths.source_absolute
        == "/home/oly/repos/do-blog/posts/recipes/fermenting/sloe-gin.jpg"
    )
    assert paths.destination_relative == "images/recipes/fermenting"
    assert paths.destination_absolute == "/tmp/images/recipes/fermenting"
