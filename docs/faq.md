# Frequently Asked Questions

## General

### Why should I use Python for Viva Insights?

Python is a versatile and widely-used programming language, especially popular in data science and analytics. Here are four key reasons why a Viva Insights analyst might choose to use Python instead of other alternatives:

1.  Python has an **extensive library ecosystem** with libraries such as pandas, [NumPy](https://numpy.org/), [scikit-learn](https://scikit-learn.org/), and NetworkX for advanced applications, including building machine learning models and performing Organizational Network Analysis (ONA) graph visualizations. This enables analysts to perform specialized and in-depth analysis for specific Viva Insights use cases, such as predicting employee churn by analyzing Viva Insights metrics.
    
2.  Python is **open-source** and has **no licensing costs**, allowing analysts to leverage its powerful functionality without additional expenses.
    
3.  Python's code-oriented workflow promotes **reproducibility**. This is valuable for improving the quality of the analysis and for efficiently replicating analysis with different data samples.
    
4.  Python has a **large and active user community**, which analysts can access to support and enhance their analysis capabilities.

## Installation and Setup

### Which version of Python should I use?

You are recommended to use the latest stable version of Python. You can find the latest version on the [official Python website](https://www.python.org/). 

### How do I install the package? 

To install the package, simply run the following on your command prompt: 
```cmd
pip install vivainsights
```

After this has successfully installed, open your Python console and run: 
```python
import vivainsights as vi
```

### How do I install from this GitHub repository?

There are two ways to install from this GitHub repository. 

The first way to do this is to: 
1. Clone this repository to your local drive. 
2. On PowerShell, change directory (`cd`) to the repository on your local drive, and run `python setup.py install`. This should install 'vivainsights' to your python package registry. To check whether it is installed, you can run `pip freeze` on your command prompt.

The second way is to install from this GitHub repository directly using pip. Just run the following in command prompt:
```cmd
pip install -e git+https://github.com/microsoft/vivainsights-py#egg=vivainsights
```

You can also install from a specific branch with the following, replacing the branch name with `<remote-branch-name>`:
```cmd
pip install -e git+https://github.com/microsoft/vivainsights-py@<remote-branch-name>#egg=vivainsights
```


## Analysis and Visualization

### How do I get started with analysis? 

We recommend checking out our [demo notebook](https://microsoft.github.io/vivainsights-py/demo-vivainsights-py.html) on how to run essential analyses and visualizations with the Python package. 