from setuptools import setup, find_packages

setup(
    name="true-lies-validator",
    version="0.9.2",
    packages=find_packages(),
    install_requires=[],
    description="True Lies - Separating truth from AI fiction. A powerful library for detecting LLM hallucinations, validating AI responses, and generating professional HTML reports with interactive dashboards.",
    author="Pato Miner",
    author_email="patominer@gmail.com",
    python_requires=">=3.10",
    keywords=["llm", "validation", "hallucination-detection", "ai", "python", "truth-detection", "html-reports", "dashboard", "chatbot-testing"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
)