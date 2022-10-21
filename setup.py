from setuptools import setup, find_packages

requires = [
    'click',
    'flask',
    'osint-geo-extractor',
]

setup(
    name='media_search',
    author='conflict-research',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/conflict-research/media-search-engine',
    license='MIT',
    description='Search engine for URLs in OSINT databases',
    python_requires='>=3.8',
    install_requires=requires,
    entry_points={
        'console_scripts':
            ['media_search = media_search.cli:main'],
    },
)
