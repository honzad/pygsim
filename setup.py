from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
  long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Graphical interface for SimPY with PyGame'
LONG_DESCRIPTION = 'Visualize your SimPy simulations with PyGame game engine'

setup(
    name="pysg",
    version=VERSION,
    author="honzad (Jan Ďurďák)",
    author_email="<jandurdak@seznam.cz>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(include=['pysg', 'pysg.*']),
    install_requires=['pygame', 'simpy'],
		python_requires=">=3.6",
    keywords=['python', 'simulation', 'gui', 'pygame simpy', 'simpy visualizer'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
				"Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
				"Topic :: Scientific/Engineering :: Visualization",
				"Topic :: Scientific/Engineering :: Simulation"
    ],
)
