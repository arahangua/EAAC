from setuptools import setup, find_packages

setup(
    name='EAAC AI agent wrapper',
    version='0.1.0',  # Start with a small version
    description='A wrapper for common AI agent frameworks',
    author='THK',
    author_email='arahangua@gmail.com',
    packages=find_packages(),
    package_data={
        'eaac': ['*.json'],  # Include all JSON files within the eaac package
    },
    install_requires=[
        # Add your dependencies here
        # e.g., 'requests', 'numpy', etc.
    ],
    python_requires='>=3.6',  # Minimum version requirement of the Python
    classifiers=[
        'Development Status :: 3 - Alpha',  # Choose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Your license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
