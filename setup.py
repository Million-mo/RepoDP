from setuptools import setup, find_packages

setup(
    name="ropedp",
    version="0.1.0",
    description="代码仓数据处理工具",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "gitpython>=3.1.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "tqdm>=4.64.0",
        "pyyaml>=6.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "jupyter>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ropedp=ropedp.cli:main",
        ],
    },
    python_requires=">=3.8",
)

