from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name = 'asrassessment',
    version = '0.0.13',
    description = 'Provides Phoneme Error Rate & Visualisation Assessment',
    long_description = open('README.md').read(),
    url='',
    author = 'Jonathan Lim',
    author_email = 'Jonathanlimws@gmail.com',
    license = 'MIT',
    classifiers = classifiers,
    keywords = 'ASR',
    packages = find_packages(),
    install_requires = ['glob2 == 0.7',
                        'tqdm == 4.64.0',
                        'librosa == 0.9.2',
                        'scipy == 1.9.0',
                        'numpy == 1.23.1',
                        'pandas == 1.4.3',
                        'sklearn == 0.0',
                        'pydub == 0.25.1',
                        'soundfile == 0.10.3.post1']
)