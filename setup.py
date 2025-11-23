"""Setup script for longevity_map package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="longevity-map",
    version="0.1.0",
    author="Longevity R&D Map Team",
    description="A living platform mapping open problems in aging sciences to capabilities, resources, and gaps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/longevity-map",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "longevity-map-api=longevity_map.api.main:app",
            "longevity-map-update=longevity_map.agents.updater:main",
            "longevity-map-analyze=longevity_map.analysis.gap_analyzer:main",
        ],
    },
)

