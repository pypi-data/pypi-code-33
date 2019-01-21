"""
Conventional Commits-related data.
"""


def patterns() -> dict:
    base_pattern: str = r'(:|\(.+\):) .+'

    return {
        'build': r'build' + base_pattern,
        'ci': r'ci' + base_pattern,
        'chore': r'chore' + base_pattern,
        'docs': r'docs' + base_pattern,
        'feat': r'feat' + base_pattern,
        'fix': r'fix' + base_pattern,
        'perf': r'perf' + base_pattern,
        'refactor': r'refactor' + base_pattern,
        'revert': r'revert' + base_pattern,
        'style': r'style' + base_pattern,
        'test': r'test' + base_pattern,
        'improvement': r'improvement' + base_pattern,
        'BREAKING CHANGE': r'BREAKING CHANGE' + base_pattern
    }
