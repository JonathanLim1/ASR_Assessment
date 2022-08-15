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
    version = '0.1.9',
    description = 'Provides Phoneme Error Rate & Visualisation Assessment',
    long_description = "Click on github to find out more!",
    url='https://github.com/JonathanLim1/ASR_Assessment',
    author = 'Jonathan Lim',
    author_email = 'Jonathanlimws@gmail.com',
    license = 'MIT',
    classifiers = classifiers,
    keywords = 'ASR',
    packages = find_packages(),
    install_requires = ['glob2>=0.5,<0.7',
                        'tqdm>=4.64.0',
                        'librosa>=0.9.2',
                        'scipy>=1.9.0',
                        'numpy>=1.23.1',
                        'pandas>=1.4.3',
                        'sklearn>=0.0',
                        'pydub>=0.25.1',
                        'soundfile>=0.10.2',
                        'plotly>=5.8.0',
                        'matplotlib']
)