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
    version = '0.0.2',
    description = 'Provides Phoneme Error Rate & Visualisation Assessment',
    long_description = open('README.md').read(),
    url='',
    author = 'Jonathan Lim',
    author_email = 'Jonathanlimws@gmail.com',
    license = 'MIT',
    classifiers = classifiers,
    keywords = 'ASR',
    packages = find_packages(),
    install_requires = ['<glob>',
                        '<tqdm>',
                        '<librosa>',
                        '<scipy.io.wavfile>',
                        '<numpy>',
                        '<pandas>',
                        '<sklearn>',
                        '<pydub>',
                        '<s5oundfile>',
                        '<subprocess>',
                        '<copy>',
                        '<difflib>',
                        '<eng_to_ipa>']
)