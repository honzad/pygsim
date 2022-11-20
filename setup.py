from setuptools import setup

extras_require = {
    "develop": [
        "check-manifest",
        "pytest",
        "pytest-cov",
        "bumpversion",
        "pyflakes",
        "pre-commit",
        "black",
        "twine",
    ],
}

extras_require["complete"] = sorted(set(sum(extras_require.values(), [])))

setup(
    extras_require=extras_require,
)
