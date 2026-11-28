# A Small Markdown Demo

This page is written in Markdown and rendered with the same Jupyter Book theme as the rest of the blog. It includes prose, math, code, and an image to make the appearance easy to compare with a notebook post.

## A simple experiment

For observations $x_1, \ldots, x_n$, the sample mean is

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i.
$$

Here is an example in Python:

```python
import numpy as np

samples = np.array([1.0, 2.0, 3.0, 4.0])
print(f"Sample mean: {samples.mean():.1f}")
```

The output below is included as text; this Markdown page does not execute code.

```text
Sample mean: 2.5
```

## A figure

![A gridworld environment](figures/gridworld_environment.png)

This demo can be removed after comparing it with the notebook-rendered posts.
