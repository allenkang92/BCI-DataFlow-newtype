from setuptools import setup, find_packages

setup(
    name="neurosignal-processor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=0.24.0",
        "mlflow>=2.0.0",
        "pydantic>=2.0.0",
        "PyYAML>=5.4.0",
    ],
    python_requires=">=3.8",
)
