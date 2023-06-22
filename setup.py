from setuptools import setup

setup(
    name = 'acforces',
    version = '0.1.0',
    py_modules = ['acforces'],
    install_requires = [
        'Click', 
        'robobrowser', 
        'requests', 
        'lxml', 
        'browsercookie'
    ],
    entry_points = '''
        [console_scripts]
        acforces = acforces:main
    ''',
)