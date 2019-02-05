def test_api():
    import limix_sphinx_theme

    for fn in ["get_html_theme_path", "setup", "test"]:
        assert hasattr(limix_sphinx_theme, fn)
