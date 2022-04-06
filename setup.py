from setuptools import setup, find_packages

try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

except Exception:
    long_description = ''
    requirements = [
        'requests', 
        'lxml', 
        'cchardet', 
        'urllib3', 
        'beautifulsoup4', 
        'RateMyProfessorAPI'
    ]

setup (
    name='CNU-Course-API',
    packages=find_packages(),
    version='1.0.0',
    license='',
    description='An API to get and parse information from the CNU Schedule of Classes website',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Todd Mahood',
    author_email='todd@toddmahood.com',
    url='toddmahood.com',
    download_url='https://github.com/toddmahood/CNU-Course-API/archive/refs/heads/main.zip',
    keywords=[],
    install_requires=requirements,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)